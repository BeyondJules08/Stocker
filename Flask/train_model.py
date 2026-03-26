"""
Entrena el modelo de pronóstico de demanda.

Prioridad de datos:
  1. Ventas reales (detalle_venta + ventas + productos + categorias)
  2. Si hay < 50 filas reales → complementa con sintéticos basados en el catálogo real
  3. Sin ventas en absoluto   → 100 % sintéticos del catálogo real

Uso (dentro del contenedor):
    python train_model.py
"""

import os
import random
import warnings
warnings.filterwarnings('ignore')

from datetime import date, timedelta

import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

DB_URL     = os.environ.get('DATABASE_URL', 'mysql+pymysql://stocker:stocker123@db:3306/stocker')
MODEL_DIR  = os.environ.get('MODEL_DIR', '/app/models')
MODEL_PATH = os.path.join(MODEL_DIR, 'modelo_demanda.pkl')

FEATURES = ['precio', 'nivel_inventario', 'stock_minimo', 'categoria', 'dia_semana', 'mes']
TARGET   = 'unidades_vendidas'
CAT_COLS = ['categoria']

MIN_ROWS_REAL = 50   # umbral mínimo para usar sólo datos reales


# ---------------------------------------------------------------------------
# Carga de datos reales
# ---------------------------------------------------------------------------

def cargar_datos_reales(engine) -> pd.DataFrame:
    sql = text("""
        SELECT
            p.nombre                        AS producto,
            c.nombre                        AS categoria,
            p.precio_venta                  AS precio,
            p.stock_actual                  AS nivel_inventario,
            p.stock_minimo                  AS stock_minimo,
            MIN(DAYOFWEEK(v.fecha))         AS dia_semana,
            MIN(MONTH(v.fecha))             AS mes,
            SUM(dv.cantidad)                AS unidades_vendidas
        FROM detalle_venta dv
        JOIN ventas     v  ON dv.venta_id    = v.id
        JOIN productos  p  ON dv.producto_id = p.id
        JOIN categorias c  ON p.categoria_id = c.id
        WHERE v.estado = 'completada'
        GROUP BY p.id, p.nombre, c.nombre, p.precio_venta,
                 p.stock_actual, p.stock_minimo, DATE(v.fecha)
        ORDER BY DATE(v.fecha) DESC
    """)
    return pd.read_sql(sql, engine)


# ---------------------------------------------------------------------------
# Generación de datos sintéticos basados en el catálogo real
# ---------------------------------------------------------------------------

def demanda_base(precio: float) -> tuple:
    if precio < 20:   return (30, 80)
    if precio < 50:   return (15, 45)
    if precio < 100:  return (8,  25)
    return (3, 12)


def generar_sinteticos(engine, n_dias: int = 90) -> pd.DataFrame:
    productos = pd.read_sql(text("""
        SELECT p.nombre, c.nombre AS categoria,
               p.precio_venta  AS precio,
               p.stock_actual  AS nivel_inventario,
               p.stock_minimo  AS stock_minimo
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
    """), engine)

    if productos.empty:
        return pd.DataFrame()

    filas = []
    base_date = date.today() - timedelta(days=n_dias)

    for _, prod in productos.iterrows():
        lo, hi = demanda_base(float(prod['precio']))
        for offset in range(n_dias):
            d   = base_date + timedelta(days=offset)
            dow = d.isoweekday()   # 1=Lun … 7=Dom
            mes = d.month

            base = random.randint(lo, hi)
            if dow in (6, 7):                                   # fin de semana
                base = int(base * 1.2)
            if prod['nivel_inventario'] < prod['stock_minimo'] * 2:
                base = int(base * 0.6)                          # stock bajo
            if mes in (11, 12):                                 # temporada alta
                base = int(base * 1.15)

            filas.append({
                'producto':          prod['nombre'],
                'categoria':         prod['categoria'],
                'precio':            float(prod['precio']),
                'nivel_inventario':  int(prod['nivel_inventario']),
                'stock_minimo':      int(prod['stock_minimo']),
                'dia_semana':        dow,
                'mes':               mes,
                'unidades_vendidas': max(1, base + random.randint(-5, 5)),
            })

    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('Conectando a la base de datos...')
    engine = create_engine(DB_URL)

    df_real = cargar_datos_reales(engine)
    n_real  = len(df_real)
    print(f'Registros reales de ventas: {n_real:,}')

    if n_real >= MIN_ROWS_REAL:
        df     = df_real
        fuente = 'real'
    elif n_real > 0:
        df_sint = generar_sinteticos(engine)
        df      = pd.concat([df_real, df_sint], ignore_index=True)
        fuente  = 'mixta'
        print(f'Pocos datos reales — combinando {n_real} reales + {len(df_sint)} sintéticos')
    else:
        df     = generar_sinteticos(engine)
        fuente = 'sintetica'
        print(f'Sin ventas — usando {len(df)} registros sintéticos del catálogo real')

    if len(df) < 10:
        print('ERROR: El catálogo no tiene productos activos. Agrega productos primero.')
        return

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.20, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    print(f'Entrenamiento completado [{fuente}]')
    print(f'  MAE : {mae:.2f}  unidades de error promedio')
    print(f'  R²  : {r2:.4f}  ({r2 * 100:.1f} % varianza explicada)')

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({
        'model':    model,
        'scaler':   scaler,
        'encoders': encoders,
        'features': FEATURES,
        'mae':      mae,
        'r2':       r2,
        'fuente':   fuente,
        'n_train':  len(df),
    }, MODEL_PATH)
    print(f'Modelo guardado en: {MODEL_PATH}')


if __name__ == '__main__':
    main()

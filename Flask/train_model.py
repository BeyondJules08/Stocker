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
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

DB_URL     = os.environ.get('DATABASE_URL', 'mysql+pymysql://stocker:stocker123@db:3306/stocker')
MODEL_DIR  = os.environ.get('MODEL_DIR', '/app/models')
MODEL_PATH = os.path.join(MODEL_DIR, 'modelo_demanda.pkl')

FEATURES = [
    'precio', 'bajo_stock', 'stock_minimo', 'categoria',
    'dia_semana', 'mes',
    'ventas_ayer', 'promedio_7_dias', 'promedio_30_dias',
]
TARGET   = 'unidades_vendidas'
CAT_COLS = ['categoria']

MIN_ROWS_REAL = 50   # umbral mínimo para usar sólo datos reales


# ---------------------------------------------------------------------------
# Carga de datos reales
# ---------------------------------------------------------------------------

def cargar_datos_reales(engine) -> pd.DataFrame:
    sql = text("""
        SELECT
            DATE(v.fecha)                   AS fecha,
            p.nombre                        AS producto,
            c.nombre                        AS categoria,
            p.precio_venta                  AS precio,
            p.stock_actual                  AS nivel_inventario,
            p.stock_minimo                  AS stock_minimo,
            DAYOFWEEK(MIN(v.fecha))         AS dia_semana,
            MONTH(MIN(v.fecha))             AS mes,
            SUM(dv.cantidad)                AS unidades_vendidas
        FROM detalle_venta dv
        JOIN ventas     v  ON dv.venta_id    = v.id
        JOIN productos  p  ON dv.producto_id = p.id
        JOIN categorias c  ON p.categoria_id = c.id
        WHERE v.estado = 'completada'
        GROUP BY DATE(v.fecha), p.id, p.nombre, c.nombre,
                 p.precio_venta, p.stock_actual, p.stock_minimo
        ORDER BY p.nombre, DATE(v.fecha) ASC
    """)
    df = pd.read_sql(sql, engine)
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
    return df


# ---------------------------------------------------------------------------
# Generación de datos sintéticos basados en el catálogo real
# ---------------------------------------------------------------------------

def demanda_base(precio: float) -> tuple:
    if precio < 20:   return (30, 80)
    if precio < 50:   return (15, 45)
    if precio < 100:  return (8,  25)
    return (3, 12)


def generar_sinteticos(engine, n_dias: int = 180) -> pd.DataFrame:
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
        lo, hi   = demanda_base(float(prod['precio']))
        mid      = (lo + hi) / 2.0

        # Each product gets a stable demand personality drawn once.
        # This makes lag features informative: a high-selling product
        # stays high across consecutive days.
        factor_producto = random.uniform(0.7, 1.3)
        demanda_estable = mid * factor_producto

        bajo_stock = prod['nivel_inventario'] < prod['stock_minimo'] * 2

        demanda_ayer = demanda_estable  # seed for autocorrelation

        for offset in range(n_dias):
            d   = base_date + timedelta(days=offset)
            dow = d.isoweekday()   # 1=Lun … 7=Dom
            mes = d.month

            # Build today's expected demand from stable base + modifiers
            esperada = demanda_estable
            if dow in (6, 7):      esperada *= 1.20   # fin de semana
            if bajo_stock:         esperada *= 0.60   # stock bajo
            if mes in (11, 12):    esperada *= 1.15   # temporada alta

            # Autocorrelation: blend 70% today's pattern + 30% yesterday's
            # actual sales. Real demand has momentum.
            demanda_hoy = 0.70 * esperada + 0.30 * demanda_ayer

            # Proportional noise ~±8% (not absolute ±5 which destroys
            # low-volume products)
            ruido = random.uniform(0.92, 1.08)
            unidades = max(1, round(demanda_hoy * ruido))

            filas.append({
                'fecha':             pd.Timestamp(d),
                'producto':          prod['nombre'],
                'categoria':         prod['categoria'],
                'precio':            float(prod['precio']),
                'nivel_inventario':  int(prod['nivel_inventario']),
                'stock_minimo':      int(prod['stock_minimo']),
                'dia_semana':        dow,
                'mes':               mes,
                'unidades_vendidas': unidades,
            })

            demanda_ayer = unidades

    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def agregar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds bajo_stock flag and lag features (per-product time series)."""
    df = df.sort_values(['producto', 'fecha']).copy()

    df['bajo_stock'] = (df['nivel_inventario'] < df['stock_minimo']).astype(int)

    grp = df.groupby('producto')['unidades_vendidas']
    df['ventas_ayer']      = grp.shift(1).fillna(0)
    df['promedio_7_dias']  = grp.transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean()
    ).fillna(0)
    df['promedio_30_dias'] = grp.transform(
        lambda x: x.shift(1).rolling(30, min_periods=1).mean()
    ).fillna(0)

    return df


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

    df = agregar_features(df)

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    print(f'Entrenamiento completado [{fuente}]')
    print(f'  MAE : {mae:.2f}  unidades de error promedio')
    print(f'  R²  : {r2:.4f}  ({r2 * 100:.1f} % varianza explicada)')

    # Feature importance
    importances = sorted(
        zip(FEATURES, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print('  Importancia de features:')
    for feat, imp in importances:
        print(f'    {feat:<20} {imp:.3f}')

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({
        'model':    model,
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

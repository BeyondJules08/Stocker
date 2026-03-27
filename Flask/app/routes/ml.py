import os
import sys
import subprocess
import warnings
warnings.filterwarnings('ignore')

from datetime import date, timedelta

import numpy as np
import pandas as pd
import joblib
from flask import Blueprint, jsonify
from sqlalchemy import text, bindparam
from app import db

ml_bp = Blueprint('ml', __name__)

MODEL_PATH = os.path.join(
    os.environ.get('MODEL_DIR', '/app/models'),
    'modelo_demanda.pkl'
)

FEATURES = [
    'precio', 'bajo_stock', 'stock_minimo', 'categoria',
    'dia_semana', 'mes',
    'ventas_ayer', 'promedio_7_dias', 'promedio_30_dias',
]
CAT_COLS = ['categoria']


def _consultar_lag(producto_ids: list, fecha_desde: date, fecha_hasta: date, divisor: float) -> dict:
    """Returns {producto_id: avg_daily_units} for the given date range."""
    if not producto_ids:
        return {}
    sql = text("""
        SELECT dv.producto_id,
               COALESCE(SUM(dv.cantidad), 0) / :divisor AS valor
        FROM detalle_venta dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.estado = 'completada'
          AND DATE(v.fecha) BETWEEN :desde AND :hasta
          AND dv.producto_id IN :ids
        GROUP BY dv.producto_id
    """).bindparams(bindparam('ids', expanding=True))
    rows = db.session.execute(sql, {
        'desde': fecha_desde, 'hasta': fecha_hasta,
        'divisor': divisor, 'ids': producto_ids,
    }).fetchall()
    return {r[0]: float(r[1]) for r in rows}


def obtener_lag_features(producto_ids: list) -> dict:
    """Returns lag feature dict keyed by producto_id."""
    hoy  = date.today()
    ayer = hoy - timedelta(days=1)

    ayer_map  = _consultar_lag(producto_ids, ayer,                    ayer,  1.0)
    prom7_map = _consultar_lag(producto_ids, hoy - timedelta(days=7), ayer,  7.0)
    prom30_map= _consultar_lag(producto_ids, hoy - timedelta(days=30),ayer, 30.0)

    return {
        pid: {
            'ventas_ayer':      ayer_map.get(pid,   0.0),
            'promedio_7_dias':  prom7_map.get(pid,  0.0),
            'promedio_30_dias': prom30_map.get(pid, 0.0),
        }
        for pid in producto_ids
    }


@ml_bp.route('/api/ml/prediccion')
def prediccion():
    if not os.path.exists(MODEL_PATH):
        return jsonify({
            'error': 'Modelo no entrenado. Ejecuta: python train_model.py'
        }), 503

    data     = joblib.load(MODEL_PATH)
    model    = data['model']
    encoders = data['encoders']

    # Todos los productos activos del catálogo real
    rows = db.session.execute(text("""
        SELECT p.id, p.nombre, c.nombre AS categoria,
               p.precio_venta, p.stock_actual, p.stock_minimo
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
        ORDER BY c.nombre, p.nombre
    """)).fetchall()

    if not rows:
        return jsonify({'error': 'No hay productos activos en el catálogo.'}), 404

    hoy = date.today()
    df  = pd.DataFrame(rows, columns=[
        'producto_id', 'producto', 'categoria',
        'precio', 'nivel_inventario', 'stock_minimo',
    ])
    df['dia_semana'] = hoy.isoweekday()
    df['mes']        = hoy.month
    df['bajo_stock'] = (df['nivel_inventario'] < df['stock_minimo']).astype(int)

    # Lag features from real sales history (defaults to 0 when no data)
    producto_ids = df['producto_id'].tolist()
    lag_map      = obtener_lag_features(producto_ids)
    df['ventas_ayer']      = df['producto_id'].map(lambda pid: lag_map[pid]['ventas_ayer'])
    df['promedio_7_dias']  = df['producto_id'].map(lambda pid: lag_map[pid]['promedio_7_dias'])
    df['promedio_30_dias'] = df['producto_id'].map(lambda pid: lag_map[pid]['promedio_30_dias'])

    X = df[FEATURES].copy()
    for col in CAT_COLS:
        le = encoders[col]
        X[col] = X[col].apply(
            lambda v: int(le.transform([v])[0]) if v in le.classes_ else 0
        )

    preds = np.maximum(model.predict(X), 0)
    df['prediccion_diaria'] = preds.round().astype(int)

    # Días de cobertura = stock actual / demanda diaria predicha
    df['dias_cobertura'] = np.where(
        df['prediccion_diaria'] > 0,
        (df['nivel_inventario'] / df['prediccion_diaria']).round(1),
        999.0,
    )

    result = df[[
        'producto_id', 'producto', 'categoria',
        'precio', 'nivel_inventario', 'stock_minimo',
        'prediccion_diaria', 'dias_cobertura',
    ]].copy()

    result['precio']           = result['precio'].round(2)
    result['nivel_inventario'] = result['nivel_inventario'].astype(int)
    result['stock_minimo']     = result['stock_minimo'].astype(int)
    result['dias_cobertura']   = result['dias_cobertura'].round(1)
    result = result.sort_values('prediccion_diaria', ascending=False)

    return jsonify({
        'predicciones':    result.to_dict(orient='records'),
        'mae':             round(data.get('mae', 0), 2),
        'r2':              round(data.get('r2', 0), 4),
        'total_registros': int(data.get('n_train', 0)),
        'fuente_datos':    data.get('fuente', 'desconocida'),
    })


@ml_bp.route('/api/ml/retrain', methods=['POST'])
def retrain():
    """Reentrena el modelo con los datos más recientes."""
    train_script = os.path.join(os.path.dirname(__file__), '..', '..', 'train_model.py')
    train_script = os.path.abspath(train_script)

    try:
        result = subprocess.run(
            [sys.executable, train_script],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return jsonify({'ok': True, 'output': result.stdout.strip()})
        return jsonify({'ok': False, 'error': result.stderr.strip()}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'ok': False, 'error': 'El entrenamiento tardó demasiado (> 120 s).'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

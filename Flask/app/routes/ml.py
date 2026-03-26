import os
import sys
import subprocess
import warnings
warnings.filterwarnings('ignore')

from datetime import date

import numpy as np
import pandas as pd
import joblib
from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db

ml_bp = Blueprint('ml', __name__)

MODEL_PATH = os.path.join(
    os.environ.get('MODEL_DIR', '/app/models'),
    'modelo_demanda.pkl'
)

FEATURES = ['precio', 'nivel_inventario', 'stock_minimo', 'categoria', 'dia_semana', 'mes']
CAT_COLS = ['categoria']


@ml_bp.route('/api/ml/prediccion')
def prediccion():
    if not os.path.exists(MODEL_PATH):
        return jsonify({
            'error': 'Modelo no entrenado. Ejecuta: python train_model.py'
        }), 503

    data     = joblib.load(MODEL_PATH)
    model    = data['model']
    scaler   = data['scaler']
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
    df['dia_semana'] = hoy.isoweekday()   # 1=Lun … 7=Dom
    df['mes']        = hoy.month

    X = df[FEATURES].copy()
    for col in CAT_COLS:
        le = encoders[col]
        X[col] = X[col].apply(
            lambda v: int(le.transform([v])[0]) if v in le.classes_ else 0
        )

    preds = np.maximum(model.predict(scaler.transform(X)), 0)
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

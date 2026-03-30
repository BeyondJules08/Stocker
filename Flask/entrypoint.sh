#!/bin/sh
set -e

MODEL_FILE="${MODEL_DIR:-/app/models}/modelo_demanda.pkl"

if [ ! -f "$MODEL_FILE" ]; then
    echo ">>> Entrenando modelo ML por primera vez..."
    python train_model.py || echo ">>> Advertencia: entrenamiento falló (sin datos aún). Se puede reentrenar desde el panel."
fi

exec gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} "app:create_app()"

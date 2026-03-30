import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'stocker-secret-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://stocker:stocker123@db:3306/stocker?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    PDF_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'documentos')
    XML_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'documentos')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

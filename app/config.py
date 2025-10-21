import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-insight-pyme-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'insight_pyme.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUBSCRIPTION_PLANS = {
        'basico':  {'nombre': 'Plan Básico',  'precio': 29.99, 'features': ['Dashboard', 'Análisis de productos', 'Reportes básicos']},
        'pro':     {'nombre': 'Plan Pro',     'precio': 59.99, 'features': ['Todo lo básico', 'Segmentación', 'Alertas']},
        'premium': {'nombre': 'Plan Premium', 'precio': 99.99, 'features': ['Todo lo Pro', 'Predicción', 'API']}
    }
# app/config.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.dirname(basedir), "app.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

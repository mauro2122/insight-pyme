# app/__init__.py
from flask import Flask
from .config import Config          # <— relativo
from .models import db              # <— relativo
from .routes import main            # <— relativo


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(main)
    return app


from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from app.config import config
from app.models import db
from app.logger import setup_logger
from app.middleware import register_error_handlers
from app.routes import auth_bp, models_bp, health_bp, datasets_bp, training_bp, dashboard_bp, inference_bp, alerts_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)

    app.config.from_object(config.get(config_name))

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    setup_logger(app, app.config.get('LOG_LEVEL', 'INFO'))

    register_error_handlers(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inference_bp)
    app.register_blueprint(alerts_bp)

    with app.app_context():
        db.create_all()

    app.logger.info(f"Fine-Tuning Studio API initialized - Mode: {config_name}")

    return app

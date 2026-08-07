import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///finetuning_studio.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Model Configuration
    SUPPORTED_MODELS = ['llama', 'mistral', 'qwen']
    MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), '../../models_cache')

    # Training Configuration
    DEFAULT_DEVICE = 'cuda' if os.getenv('USE_GPU', 'true').lower() == 'true' else 'cpu'
    MAX_CHECKPOINTS_PER_JOB = 5

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5GB max file size
    ALLOWED_EXTENSIONS = {'csv', 'json', 'jsonl', 'txt', 'parquet'}

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # API Configuration
    API_TITLE = 'Fine-Tuning Studio API'
    API_VERSION = '1.0.0'
    API_DESCRIPTION = 'Platform for training and fine-tuning LLMs'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

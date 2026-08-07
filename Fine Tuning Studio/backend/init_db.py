#!/usr/bin/env python
"""Initialize database with sample data"""

from app import create_app
from app.models import db
from app.models.user import User
from app.models.model_metadata import ModelMetadata
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with sample data"""
    app = create_app()

    with app.app_context():
        # Create tables
        logger.info("Creating database tables...")
        db.create_all()

        # Check if already initialized
        if User.query.first():
            logger.info("Database already initialized")
            return

        # Create admin user
        logger.info("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@finetuning-studio.com',
            full_name='Admin User',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Create default models
        logger.info("Adding default models...")
        models = [
            {
                'name': 'Llama 2 7B',
                'model_type': 'llama',
                'model_size': '7b',
                'huggingface_id': 'meta-llama/Llama-2-7b-hf',
                'description': 'Meta Llama 2 7B parameter model',
                'parameters_count': 7000000000,
                'context_window': 4096
            },
            {
                'name': 'Llama 2 13B',
                'model_type': 'llama',
                'model_size': '13b',
                'huggingface_id': 'meta-llama/Llama-2-13b-hf',
                'description': 'Meta Llama 2 13B parameter model',
                'parameters_count': 13000000000,
                'context_window': 4096
            },
            {
                'name': 'Mistral 7B',
                'model_type': 'mistral',
                'model_size': '7b',
                'huggingface_id': 'mistralai/Mistral-7B-v0.1',
                'description': 'Mistral 7B parameter model',
                'parameters_count': 7000000000,
                'context_window': 8192
            },
            {
                'name': 'Qwen 7B',
                'model_type': 'qwen',
                'model_size': '7b',
                'huggingface_id': 'Qwen/Qwen-7B',
                'description': 'Qwen 7B parameter model',
                'parameters_count': 7000000000,
                'context_window': 2048
            }
        ]

        for model_data in models:
            model = ModelMetadata(**model_data)
            db.session.add(model)

        db.session.commit()

        logger.info("Database initialized successfully!")
        logger.info(f"Admin user created: admin / admin123")
        logger.info(f"Total models added: {len(models)}")

if __name__ == '__main__':
    init_database()

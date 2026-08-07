from flask import Blueprint, request, jsonify
from app.models import db
from app.models.model_metadata import ModelMetadata
from app.middleware import ValidationError, NotFoundError
from app.utils import ModelRegistry, token_required
import logging

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__, url_prefix='/api/models')

@models_bp.route('/supported', methods=['GET'])
def get_supported_models():
    """Get list of supported model types"""
    try:
        return jsonify({
            'supported_types': ModelRegistry.get_supported_types(),
            'models': ModelRegistry.MODELS
        }), 200

    except Exception as e:
        logger.error(f"Error fetching supported models: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500

@models_bp.route('', methods=['GET'])
@token_required
def list_models(user_id):
    """List all available models"""
    try:
        models = ModelMetadata.query.filter_by(is_active=True).all()
        return jsonify([model.to_dict() for model in models]), 200

    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500

@models_bp.route('/<int:model_id>', methods=['GET'])
@token_required
def get_model(user_id, model_id):
    """Get model details"""
    try:
        model = ModelMetadata.query.get(model_id)

        if not model:
            raise NotFoundError('Model not found')

        return jsonify(model.to_dict()), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching model: {str(e)}")
        return jsonify({'error': 'Failed to fetch model'}), 500

@models_bp.route('', methods=['POST'])
@token_required
def create_model(user_id):
    """Create/register a new model (admin only)"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['name', 'model_type', 'huggingface_id']):
            raise ValidationError('Name, model_type, and huggingface_id are required')

        if not ModelRegistry.is_supported(data['model_type']):
            raise ValidationError(f"Unsupported model type: {data['model_type']}")

        # Check if model already exists
        if ModelMetadata.query.filter_by(name=data['name']).first():
            raise ValidationError('Model with this name already exists')

        model = ModelMetadata(
            name=data['name'],
            model_type=data['model_type'],
            model_size=data.get('model_size'),
            huggingface_id=data['huggingface_id'],
            description=data.get('description'),
            parameters_count=data.get('parameters_count'),
            context_window=data.get('context_window')
        )

        db.session.add(model)
        db.session.commit()

        logger.info(f"Model created: {model.name}")

        return jsonify(model.to_dict()), 201

    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating model: {str(e)}")
        return jsonify({'error': 'Failed to create model'}), 500

@models_bp.route('/<int:model_id>', methods=['PUT'])
@token_required
def update_model(user_id, model_id):
    """Update model information"""
    try:
        model = ModelMetadata.query.get(model_id)

        if not model:
            raise NotFoundError('Model not found')

        data = request.get_json() or {}

        # Update fields
        if 'name' in data:
            model.name = data['name']
        if 'description' in data:
            model.description = data['description']
        if 'is_active' in data:
            model.is_active = data['is_active']

        db.session.commit()

        logger.info(f"Model updated: {model.name}")

        return jsonify(model.to_dict()), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating model: {str(e)}")
        return jsonify({'error': 'Failed to update model'}), 500

@models_bp.route('/<int:model_id>', methods=['DELETE'])
@token_required
def delete_model(user_id, model_id):
    """Delete a model"""
    try:
        model = ModelMetadata.query.get(model_id)

        if not model:
            raise NotFoundError('Model not found')

        db.session.delete(model)
        db.session.commit()

        logger.info(f"Model deleted: {model.name}")

        return jsonify({'message': 'Model deleted'}), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting model: {str(e)}")
        return jsonify({'error': 'Failed to delete model'}), 500

from flask import Blueprint, request, jsonify
from app.models import db
from app.models.user import User, APIKey
from app.middleware import ValidationError, ConflictError, UnauthorizedError
from app.utils import create_tokens, generate_api_key, token_required
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            raise ValidationError('Username, email, and password are required')

        if User.query.filter_by(username=data['username']).first():
            raise ConflictError('Username already exists')

        if User.query.filter_by(email=data['email']).first():
            raise ConflictError('Email already registered')

        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', '')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        tokens = create_tokens(user.id)

        logger.info(f"User registered: {user.username}")

        return jsonify({
            'user': user.to_dict(),
            'tokens': tokens
        }), 201

    except (ValidationError, ConflictError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            raise ValidationError('Username and password are required')

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.verify_password(data['password']):
            raise UnauthorizedError('Invalid username or password')

        if not user.is_active:
            raise UnauthorizedError('User account is inactive')

        tokens = create_tokens(user.id)

        logger.info(f"User logged in: {user.username}")

        return jsonify({
            'user': user.to_dict(),
            'tokens': tokens
        }), 200

    except (ValidationError, UnauthorizedError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/create-api-key', methods=['POST'])
@token_required
def create_api_key(user_id):
    """Create new API key for user"""
    try:
        data = request.get_json() or {}
        key_name = data.get('name', 'Default Key')

        api_key = APIKey(
            user_id=user_id,
            key=generate_api_key(),
            name=key_name
        )

        db.session.add(api_key)
        db.session.commit()

        logger.info(f"API key created for user {user_id}")

        return jsonify({
            'api_key': api_key.to_dict(),
            'full_key': api_key.key  # Show full key only on creation
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"API key creation error: {str(e)}")
        return jsonify({'error': 'Failed to create API key'}), 500

@auth_bp.route('/api-keys', methods=['GET'])
@token_required
def list_api_keys(user_id):
    """List user API keys"""
    try:
        keys = APIKey.query.filter_by(user_id=user_id).all()
        return jsonify([key.to_dict() for key in keys]), 200

    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        return jsonify({'error': 'Failed to fetch API keys'}), 500

@auth_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@token_required
def delete_api_key(user_id, key_id):
    """Delete API key"""
    try:
        api_key = APIKey.query.filter_by(id=key_id, user_id=user_id).first()

        if not api_key:
            return jsonify({'error': 'API key not found'}), 404

        db.session.delete(api_key)
        db.session.commit()

        logger.info(f"API key deleted for user {user_id}")

        return jsonify({'message': 'API key deleted'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"API key deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete API key'}), 500

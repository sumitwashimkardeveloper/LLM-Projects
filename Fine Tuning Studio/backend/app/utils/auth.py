from flask_jwt_extended import create_access_token, create_refresh_token
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

def generate_api_key():
    """Generate a random API key"""
    return secrets.token_urlsafe(32)

def create_tokens(user_id: int) -> dict:
    """Create JWT access and refresh tokens"""
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=24)
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

def token_required(fn):
    """Decorator to require JWT token"""
    @wraps(fn)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        return fn(user_id, *args, **kwargs)
    return decorated

def api_key_required(fn):
    """Decorator to require API key"""
    @wraps(fn)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        from app.models.user import APIKey
        key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()

        if not key_obj:
            return jsonify({'error': 'Invalid or inactive API key'}), 401

        # Update last used time
        key_obj.last_used_at = datetime.utcnow()
        from app.models import db
        db.session.commit()

        return fn(key_obj.user_id, *args, **kwargs)

    return decorated

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        from app.models.user import User
        user = User.query.get(user_id)

        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return fn(user_id, *args, **kwargs)

    return decorated

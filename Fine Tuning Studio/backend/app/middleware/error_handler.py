from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message):
        super().__init__(message, 400)

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message):
        super().__init__(message, 404)

class UnauthorizedError(APIError):
    """Unauthorized error"""
    def __init__(self, message):
        super().__init__(message, 401)

class ForbiddenError(APIError):
    """Forbidden error"""
    def __init__(self, message):
        super().__init__(message, 403)

class ConflictError(APIError):
    """Conflict error"""
    def __init__(self, message):
        super().__init__(message, 409)

def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        logger.error(f"API Error: {error.message}")
        return jsonify({
            'error': error.message,
            'status': error.status_code
        }), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        logger.error(f"HTTP Exception: {error.description}")
        return jsonify({
            'error': error.description,
            'status': error.code
        }), error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled Exception: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500

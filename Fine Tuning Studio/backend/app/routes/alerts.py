from flask import Blueprint, request, jsonify
from app.middleware import ValidationError
from app.utils import token_required
from app.utils.alerts import NotificationService
import logging

logger = logging.getLogger(__name__)

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

notification_service = NotificationService()

@alerts_bp.route('', methods=['GET'])
@token_required
def get_alerts(user_id):
    try:
        job_id = request.args.get('job_id', type=int)
        alert_type = request.args.get('type')
        limit = request.args.get('limit', 100, type=int)

        alerts = notification_service.alert_manager.get_alerts(
            job_id=job_id,
            alert_type=alert_type,
            limit=limit
        )

        return jsonify(alerts), 200

    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return jsonify({'error': 'Failed to fetch alerts'}), 500

@alerts_bp.route('/notify/completion', methods=['POST'])
@token_required
def notify_job_completion(user_id):
    try:
        data = request.get_json()

        if not data or 'job_id' not in data or 'job_name' not in data or 'status' not in data:
            raise ValidationError('job_id, job_name, and status are required')

        job_id = data['job_id']
        job_name = data['job_name']
        status = data['status']
        email = data.get('email')

        notification_service.notify_job_completed(job_id, job_name, status, email)

        return jsonify({'message': 'Notification sent'}), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return jsonify({'error': 'Failed to send notification'}), 500

@alerts_bp.route('/notify/resource', methods=['POST'])
@token_required
def notify_resource_limit(user_id):
    try:
        data = request.get_json()

        if not data or 'job_id' not in data or 'resource_type' not in data:
            raise ValidationError('job_id and resource_type are required')

        job_id = data['job_id']
        resource_type = data['resource_type']
        limit = data.get('limit')
        current = data.get('current')

        notification_service.notify_resource_limit(job_id, resource_type, limit, current)

        return jsonify({'message': 'Alert created'}), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        return jsonify({'error': 'Failed to create alert'}), 500

@alerts_bp.route('/notify/error', methods=['POST'])
@token_required
def notify_error(user_id):
    try:
        data = request.get_json()

        if not data or 'job_id' not in data or 'error_message' not in data:
            raise ValidationError('job_id and error_message are required')

        job_id = data['job_id']
        error_message = data['error_message']

        notification_service.notify_error(job_id, error_message)

        return jsonify({'message': 'Error alert created'}), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error creating error alert: {str(e)}")
        return jsonify({'error': 'Failed to create alert'}), 500

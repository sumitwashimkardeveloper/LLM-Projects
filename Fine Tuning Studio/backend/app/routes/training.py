from flask import Blueprint, request, jsonify
from app.models import db
from app.models.training_job import TrainingJob
from app.models.model_metadata import ModelMetadata, Checkpoint
from app.models.dataset import Dataset
from app.middleware import ValidationError, NotFoundError
from app.utils import token_required
from app.tasks import train_model
import logging
import os

logger = logging.getLogger(__name__)

training_bp = Blueprint('training', __name__, url_prefix='/api/training')

@training_bp.route('/jobs', methods=['POST'])
@token_required
def create_training_job(user_id):
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['name', 'model_id', 'dataset_id', 'training_type']):
            raise ValidationError('name, model_id, dataset_id, and training_type are required')

        model = ModelMetadata.query.get(data['model_id'])
        if not model:
            raise NotFoundError('Model not found')

        dataset = Dataset.query.filter_by(id=data['dataset_id'], user_id=user_id).first()
        if not dataset:
            raise NotFoundError('Dataset not found')

        output_dir = os.path.join('outputs', f"training_{data['name']}_{user_id}")

        job = TrainingJob(
            name=data['name'],
            user_id=user_id,
            model_id=data['model_id'],
            dataset_id=data['dataset_id'],
            training_type=data['training_type'],
            learning_rate=data.get('learning_rate', 2e-4),
            batch_size=data.get('batch_size', 4),
            num_epochs=data.get('num_epochs', 3),
            lora_r=data.get('lora_r', 8),
            lora_alpha=data.get('lora_alpha', 16),
            lora_dropout=data.get('lora_dropout', 0.05),
            lora_target_modules=data.get('lora_target_modules'),
            use_4bit=data.get('use_4bit', False),
            use_8bit=data.get('use_8bit', False),
            output_dir=output_dir,
            save_strategy=data.get('save_strategy', 'steps'),
            save_steps=data.get('save_steps', 500)
        )

        db.session.add(job)
        db.session.commit()

        logger.info(f"Training job created: {job.id}")

        return jsonify(job.to_dict()), 201

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating training job: {str(e)}")
        return jsonify({'error': 'Failed to create training job'}), 500

@training_bp.route('/jobs', methods=['GET'])
@token_required
def list_training_jobs(user_id):
    try:
        jobs = TrainingJob.query.filter_by(user_id=user_id).all()
        return jsonify([j.to_dict() for j in jobs]), 200

    except Exception as e:
        logger.error(f"Error listing training jobs: {str(e)}")
        return jsonify({'error': 'Failed to fetch training jobs'}), 500

@training_bp.route('/jobs/<int:job_id>', methods=['GET'])
@token_required
def get_training_job(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        job_data = job.to_dict()
        job_data['checkpoints'] = [c.to_dict() for c in job.checkpoints]

        return jsonify(job_data), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching training job: {str(e)}")
        return jsonify({'error': 'Failed to fetch training job'}), 500

@training_bp.route('/jobs/<int:job_id>/start', methods=['POST'])
@token_required
def start_training(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if job.status != 'queued':
            raise ValidationError(f'Cannot start job with status: {job.status}')

        train_model.delay(job.id)

        return jsonify({'message': 'Training started', 'job_id': job.id}), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        return jsonify({'error': 'Failed to start training'}), 500

@training_bp.route('/jobs/<int:job_id>/pause', methods=['POST'])
@token_required
def pause_training(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if job.status != 'running':
            raise ValidationError(f'Cannot pause job with status: {job.status}')

        job.status = 'paused'
        db.session.commit()

        return jsonify({'message': 'Training paused', 'job_id': job.id}), 200

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error pausing training: {str(e)}")
        return jsonify({'error': 'Failed to pause training'}), 500

@training_bp.route('/jobs/<int:job_id>/cancel', methods=['POST'])
@token_required
def cancel_training(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if job.status not in ['queued', 'running', 'paused']:
            raise ValidationError(f'Cannot cancel job with status: {job.status}')

        job.status = 'cancelled'
        db.session.commit()

        logger.info(f"Training job cancelled: {job_id}")

        return jsonify({'message': 'Training cancelled', 'job_id': job.id}), 200

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling training: {str(e)}")
        return jsonify({'error': 'Failed to cancel training'}), 500

@training_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@token_required
def delete_training_job(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if job.status == 'running':
            raise ValidationError('Cannot delete running training job')

        db.session.delete(job)
        db.session.commit()

        logger.info(f"Training job deleted: {job_id}")

        return jsonify({'message': 'Training job deleted'}), 200

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting training job: {str(e)}")
        return jsonify({'error': 'Failed to delete training job'}), 500

@training_bp.route('/checkpoints/<int:job_id>', methods=['GET'])
@token_required
def list_checkpoints(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        checkpoints = Checkpoint.query.filter_by(training_job_id=job_id).all()

        return jsonify([c.to_dict() for c in checkpoints]), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error listing checkpoints: {str(e)}")
        return jsonify({'error': 'Failed to fetch checkpoints'}), 500

@training_bp.route('/checkpoints/<int:checkpoint_id>/restore', methods=['POST'])
@token_required
def restore_checkpoint(user_id, checkpoint_id):
    try:
        checkpoint = Checkpoint.query.get(checkpoint_id)

        if not checkpoint:
            raise NotFoundError('Checkpoint not found')

        job = TrainingJob.query.get(checkpoint.training_job_id)
        if job.user_id != user_id:
            raise ValidationError('Unauthorized')

        return jsonify({
            'message': 'Checkpoint restoration initiated',
            'checkpoint_id': checkpoint_id,
            'checkpoint_path': checkpoint.checkpoint_path
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error restoring checkpoint: {str(e)}")
        return jsonify({'error': 'Failed to restore checkpoint'}), 500

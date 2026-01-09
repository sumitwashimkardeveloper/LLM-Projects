from flask import Blueprint, request, jsonify
from app.models import db
from app.models.training_job import TrainingJob
from app.models.model_metadata import ModelMetadata, Checkpoint
from app.middleware import NotFoundError
from app.utils import token_required
from app.utils.metrics_utils import MetricsCollector
import logging
import os

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/overview', methods=['GET'])
@token_required
def dashboard_overview(user_id):
    try:
        jobs = TrainingJob.query.filter_by(user_id=user_id).all()

        total_jobs = len(jobs)
        running = sum(1 for j in jobs if j.status == 'running')
        completed = sum(1 for j in jobs if j.status == 'completed')
        failed = sum(1 for j in jobs if j.status == 'failed')

        return jsonify({
            'total_jobs': total_jobs,
            'running_jobs': running,
            'completed_jobs': completed,
            'failed_jobs': failed,
            'recent_jobs': [j.to_dict() for j in sorted(jobs, key=lambda x: x.created_at, reverse=True)[:5]]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching overview: {str(e)}")
        return jsonify({'error': 'Failed to fetch overview'}), 500

@dashboard_bp.route('/jobs/<int:job_id>/metrics', methods=['GET'])
@token_required
def get_job_metrics(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if not os.path.exists(job.output_dir):
            return jsonify({'error': 'Metrics not available yet'}), 404

        collector = MetricsCollector(job_id, job.output_dir)
        summary = collector.get_metrics_summary()

        if not summary:
            return jsonify({'error': 'No metrics available'}), 404

        return jsonify(summary), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@dashboard_bp.route('/jobs/<int:job_id>/metrics/recent', methods=['GET'])
@token_required
def get_recent_metrics(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        limit = request.args.get('limit', 50, type=int)

        if not os.path.exists(job.output_dir):
            return jsonify({'error': 'Metrics not available yet'}), 404

        collector = MetricsCollector(job_id, job.output_dir)
        metrics = collector.get_latest_metrics(limit)

        return jsonify(metrics), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching recent metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@dashboard_bp.route('/jobs/<int:job_id>/progress', methods=['GET'])
@token_required
def get_job_progress(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        elapsed = 0
        if job.training_time:
            elapsed = job.training_time

        eta_seconds = None
        if job.progress > 0 and job.progress < 100:
            total_estimate = (elapsed / job.progress) * 100
            eta_seconds = int(total_estimate - elapsed)

        return jsonify({
            'job_id': job_id,
            'status': job.status,
            'progress': job.progress,
            'current_step': job.current_step,
            'total_steps': job.total_steps,
            'elapsed_seconds': elapsed,
            'eta_seconds': eta_seconds,
            'loss': job.current_loss,
            'best_loss': job.best_loss
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching progress: {str(e)}")
        return jsonify({'error': 'Failed to fetch progress'}), 500

@dashboard_bp.route('/jobs/<int:job_id>/logs', methods=['GET'])
@token_required
def get_job_logs(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        log_file = os.path.join(job.output_dir, 'training.log')
        limit = request.args.get('limit', 100, type=int)

        if not os.path.exists(log_file):
            return jsonify({'logs': []}), 200

        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-limit:] if len(lines) > limit else lines

        return jsonify({'logs': recent_lines}), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return jsonify({'error': 'Failed to fetch logs'}), 500

@dashboard_bp.route('/jobs/compare', methods=['POST'])
@token_required
def compare_jobs(user_id):
    try:
        data = request.get_json()

        if not data or 'job_ids' not in data:
            return jsonify({'error': 'job_ids required'}), 400

        job_ids = data['job_ids']
        jobs = TrainingJob.query.filter(
            TrainingJob.id.in_(job_ids),
            TrainingJob.user_id == user_id
        ).all()

        if not jobs:
            raise NotFoundError('Jobs not found')

        comparison = []
        for job in jobs:
            collector = MetricsCollector(job.id, job.output_dir) if os.path.exists(job.output_dir) else None
            metrics_summary = collector.get_metrics_summary() if collector else None

            comparison.append({
                'job_id': job.id,
                'name': job.name,
                'training_type': job.training_type,
                'status': job.status,
                'progress': job.progress,
                'current_loss': job.current_loss,
                'best_loss': job.best_loss,
                'metrics_summary': metrics_summary
            })

        return jsonify(comparison), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error comparing jobs: {str(e)}")
        return jsonify({'error': 'Failed to compare jobs'}), 500

@dashboard_bp.route('/jobs/<int:job_id>/checkpoints/best', methods=['GET'])
@token_required
def get_best_checkpoint(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        checkpoint = Checkpoint.query.filter_by(training_job_id=job_id, is_best=True).first()

        if not checkpoint:
            return jsonify({'error': 'No best checkpoint found'}), 404

        return jsonify(checkpoint.to_dict()), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching best checkpoint: {str(e)}")
        return jsonify({'error': 'Failed to fetch checkpoint'}), 500

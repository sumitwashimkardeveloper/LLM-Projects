from flask import Blueprint, request, jsonify
from app.models import db
from app.models.training_job import TrainingJob
from app.middleware import ValidationError, NotFoundError
from app.utils import token_required
from app.utils.export_utils import ModelExporter, AdapterMerger
from app.utils.model_loader import ModelLoader
import logging
import os

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

model_loader = ModelLoader('.')

@export_bp.route('/jobs/<int:job_id>/merge', methods=['POST'])
@token_required
def merge_adapters(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        if job.status != 'completed':
            raise ValidationError('Only completed jobs can be merged')

        data = request.get_json() or {}

        try:
            base_model, tokenizer = model_loader.load_model(
                job.base_model.model_type,
                job.base_model.huggingface_id
            )
        except Exception as e:
            logger.error(f"Error loading base model: {str(e)}")
            raise ValidationError('Failed to load base model')

        try:
            from peft import PeftModel
            merged_model = PeftModel.from_pretrained(base_model, job.output_dir)
            merged_model = merged_model.merge_and_unload()
        except Exception as e:
            logger.error(f"Error merging adapters: {str(e)}")
            raise ValidationError('Failed to merge adapters')

        merge_dir = os.path.join('outputs', f'merged_{job_id}')
        AdapterMerger.save_merged_model(merged_model, tokenizer, merge_dir)

        return jsonify({
            'message': 'Adapters merged successfully',
            'job_id': job_id,
            'output_dir': merge_dir
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error merging adapters: {str(e)}")
        return jsonify({'error': 'Failed to merge adapters'}), 500

@export_bp.route('/jobs/<int:job_id>/export/huggingface', methods=['POST'])
@token_required
def export_huggingface(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        data = request.get_json() or {}
        repo_name = data.get('repo_name')

        if not repo_name:
            raise ValidationError('repo_name is required')

        try:
            base_model, tokenizer = model_loader.load_model(
                job.base_model.model_type,
                job.base_model.huggingface_id
            )

            from peft import PeftModel
            merged_model = PeftModel.from_pretrained(base_model, job.output_dir)
            merged_model = merged_model.merge_and_unload()

            merged_model.push_to_hub(repo_name)
            tokenizer.push_to_hub(repo_name)

        except Exception as e:
            logger.error(f"Error exporting to HuggingFace: {str(e)}")
            raise ValidationError('Failed to export to HuggingFace')

        return jsonify({
            'message': 'Model exported to HuggingFace',
            'repo_name': repo_name
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error exporting: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@export_bp.route('/jobs/<int:job_id>/export/onnx', methods=['POST'])
@token_required
def export_onnx(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        try:
            base_model, tokenizer = model_loader.load_model(
                job.base_model.model_type,
                job.base_model.huggingface_id
            )

            from peft import PeftModel
            merged_model = PeftModel.from_pretrained(base_model, job.output_dir)
            merged_model = merged_model.merge_and_unload()

            exporter = ModelExporter(merged_model, tokenizer)
            export_dir = os.path.join('outputs', f'onnx_{job_id}')
            exporter.export_onnx(export_dir)

        except Exception as e:
            logger.error(f"Error exporting to ONNX: {str(e)}")
            raise ValidationError('Failed to export to ONNX')

        return jsonify({
            'message': 'Model exported to ONNX',
            'output_dir': export_dir
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error exporting: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@export_bp.route('/jobs/<int:job_id>/export/torchscript', methods=['POST'])
@token_required
def export_torchscript(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        try:
            base_model, tokenizer = model_loader.load_model(
                job.base_model.model_type,
                job.base_model.huggingface_id
            )

            from peft import PeftModel
            merged_model = PeftModel.from_pretrained(base_model, job.output_dir)
            merged_model = merged_model.merge_and_unload()

            exporter = ModelExporter(merged_model, tokenizer)
            export_dir = os.path.join('outputs', f'torchscript_{job_id}')
            exporter.export_torchscript(export_dir)

        except Exception as e:
            logger.error(f"Error exporting to TorchScript: {str(e)}")
            raise ValidationError('Failed to export to TorchScript')

        return jsonify({
            'message': 'Model exported to TorchScript',
            'output_dir': export_dir
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error exporting: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@export_bp.route('/jobs/<int:job_id>/export/ggml', methods=['POST'])
@token_required
def export_ggml(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        try:
            base_model, tokenizer = model_loader.load_model(
                job.base_model.model_type,
                job.base_model.huggingface_id
            )

            from peft import PeftModel
            merged_model = PeftModel.from_pretrained(base_model, job.output_dir)
            merged_model = merged_model.merge_and_unload()

            exporter = ModelExporter(merged_model, tokenizer)
            export_dir = os.path.join('outputs', f'ggml_{job_id}')
            exporter.export_ggml(export_dir)

        except Exception as e:
            logger.error(f"Error exporting to GGML: {str(e)}")
            raise ValidationError('Failed to export to GGML')

        return jsonify({
            'message': 'Model exported to GGML',
            'output_dir': export_dir
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error exporting: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

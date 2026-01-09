from flask import Blueprint, request, jsonify
from app.models import db
from app.models.training_job import TrainingJob
from app.models.model_metadata import ModelMetadata
from app.middleware import ValidationError, NotFoundError
from app.utils import token_required
from app.utils.model_loader import ModelLoader
from app.utils.comparison_utils import InferenceTestor, ModelComparator
import logging
import os

logger = logging.getLogger(__name__)

inference_bp = Blueprint('inference', __name__, url_prefix='/api/inference')

model_loader = ModelLoader('.')
comparator = ModelComparator()

@inference_bp.route('/test', methods=['POST'])
@token_required
def test_inference(user_id):
    try:
        data = request.get_json()

        if not data or 'model_id' not in data or 'text' not in data:
            raise ValidationError('model_id and text are required')

        job_id = data.get('job_id')
        model_id = data['model_id']
        text = data['text']
        max_length = data.get('max_length', 100)

        model = None
        tokenizer = None

        if job_id:
            job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()
            if job:
                try:
                    model, tokenizer = model_loader.load_model(
                        job.base_model.model_type,
                        job.base_model.huggingface_id,
                        use_8bit=job.use_8bit,
                        use_4bit=job.use_4bit
                    )
                except Exception as e:
                    logger.error(f"Error loading model: {str(e)}")
        else:
            base_model = ModelMetadata.query.get(model_id)
            if base_model:
                try:
                    model, tokenizer = model_loader.load_model(
                        base_model.model_type,
                        base_model.huggingface_id
                    )
                except Exception as e:
                    logger.error(f"Error loading model: {str(e)}")

        if not model or not tokenizer:
            raise NotFoundError('Model could not be loaded')

        testor = InferenceTestor(model, tokenizer)
        output = testor.test_single(text, max_length)

        return jsonify({
            'input': text,
            'output': output,
            'model_id': model_id
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        return jsonify({'error': 'Inference failed'}), 500

@inference_bp.route('/test/batch', methods=['POST'])
@token_required
def test_batch_inference(user_id):
    try:
        data = request.get_json()

        if not data or 'model_id' not in data or 'texts' not in data:
            raise ValidationError('model_id and texts are required')

        model_id = data['model_id']
        texts = data['texts']
        max_length = data.get('max_length', 100)

        if not isinstance(texts, list) or len(texts) == 0:
            raise ValidationError('texts must be a non-empty list')

        base_model = ModelMetadata.query.get(model_id)
        if not base_model:
            raise NotFoundError('Model not found')

        try:
            model, tokenizer = model_loader.load_model(
                base_model.model_type,
                base_model.huggingface_id
            )
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise NotFoundError('Model could not be loaded')

        testor = InferenceTestor(model, tokenizer)
        outputs = testor.test_batch(texts, max_length)

        return jsonify({
            'inputs': texts,
            'outputs': outputs,
            'model_id': model_id,
            'count': len(outputs)
        }), 200

    except (ValidationError, NotFoundError) as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Batch inference error: {str(e)}")
        return jsonify({'error': 'Batch inference failed'}), 500

@inference_bp.route('/benchmark/<int:model_id>', methods=['POST'])
@token_required
def benchmark_model(user_id, model_id):
    try:
        data = request.get_json() or {}
        text = data.get('text', 'Hello, how are you?')
        num_iterations = data.get('num_iterations', 5)

        base_model = ModelMetadata.query.get(model_id)
        if not base_model:
            raise NotFoundError('Model not found')

        try:
            model, tokenizer = model_loader.load_model(
                base_model.model_type,
                base_model.huggingface_id
            )
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise NotFoundError('Model could not be loaded')

        testor = InferenceTestor(model, tokenizer)
        inputs = tokenizer(text, return_tensors='pt')

        latency = testor.measure_latency(text, num_iterations)

        try:
            memory = testor.profile_memory(text)
        except:
            memory = None

        return jsonify({
            'model_id': model_id,
            'latency_ms': latency,
            'memory': memory
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Benchmark error: {str(e)}")
        return jsonify({'error': 'Benchmark failed'}), 500

@inference_bp.route('/compare', methods=['POST'])
@token_required
def compare_models(user_id):
    try:
        data = request.get_json()

        if not data or 'model_ids' not in data:
            raise ValidationError('model_ids required')

        model_ids = data['model_ids']
        text = data.get('text', 'Hello, how are you?')

        if not isinstance(model_ids, list) or len(model_ids) == 0:
            raise ValidationError('model_ids must be a non-empty list')

        comparison = {}
        for model_id in model_ids:
            base_model = ModelMetadata.query.get(model_id)
            if not base_model:
                continue

            try:
                model, tokenizer = model_loader.load_model(
                    base_model.model_type,
                    base_model.huggingface_id
                )

                testor = InferenceTestor(model, tokenizer)
                output = testor.test_single(text)
                latency = testor.measure_latency(text, 3)

                comparison[str(model_id)] = {
                    'model_name': base_model.name,
                    'output': output,
                    'latency_ms': latency
                }
            except Exception as e:
                logger.warning(f"Could not test model {model_id}: {str(e)}")
                continue

        return jsonify(comparison), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Model comparison error: {str(e)}")
        return jsonify({'error': 'Comparison failed'}), 500

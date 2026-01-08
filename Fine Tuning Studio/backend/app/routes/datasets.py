from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.models import db
from app.models.dataset import Dataset
from app.middleware import ValidationError, NotFoundError
from app.utils import token_required
from app.utils.dataset_utils import DatasetProcessor
from app.tasks import process_dataset
import os
import logging

logger = logging.getLogger(__name__)

datasets_bp = Blueprint('datasets', __name__, url_prefix='/api/datasets')

ALLOWED_EXTENSIONS = {'csv', 'json', 'jsonl', 'parquet'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@datasets_bp.route('', methods=['POST'])
@token_required
def create_dataset(user_id):
    try:
        if 'file' not in request.files:
            raise ValidationError('No file provided')

        file = request.files['file']
        if file.filename == '':
            raise ValidationError('No file selected')

        if not allowed_file(file.filename):
            raise ValidationError(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')

        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, f"{user_id}_{filename}")
        file.save(file_path)

        dataset = Dataset(
            name=request.form.get('name', filename),
            user_id=user_id,
            description=request.form.get('description', ''),
            file_path=file_path,
            file_format=file_ext,
            file_size=os.path.getsize(file_path),
            status='uploaded'
        )

        db.session.add(dataset)
        db.session.commit()

        process_dataset.delay(dataset.id)

        logger.info(f"Dataset created: {dataset.id}")

        return jsonify(dataset.to_dict()), 201

    except ValidationError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Dataset creation error: {str(e)}")
        return jsonify({'error': 'Failed to create dataset'}), 500

@datasets_bp.route('', methods=['GET'])
@token_required
def list_datasets(user_id):
    try:
        datasets = Dataset.query.filter_by(user_id=user_id).all()
        return jsonify([d.to_dict() for d in datasets]), 200

    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        return jsonify({'error': 'Failed to fetch datasets'}), 500

@datasets_bp.route('/<int:dataset_id>', methods=['GET'])
@token_required
def get_dataset(user_id, dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()

        if not dataset:
            raise NotFoundError('Dataset not found')

        return jsonify(dataset.to_dict()), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error fetching dataset: {str(e)}")
        return jsonify({'error': 'Failed to fetch dataset'}), 500

@datasets_bp.route('/<int:dataset_id>/preview', methods=['GET'])
@token_required
def preview_dataset(user_id, dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()

        if not dataset:
            raise NotFoundError('Dataset not found')

        limit = request.args.get('limit', 10, type=int)

        df = DatasetProcessor.load_dataset(dataset.file_path, dataset.file_format)
        preview_data = df.head(limit).to_dict(orient='records')

        return jsonify({
            'dataset_id': dataset.id,
            'total_rows': len(df),
            'columns': list(df.columns),
            'preview': preview_data
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error previewing dataset: {str(e)}")
        return jsonify({'error': 'Failed to preview dataset'}), 500

@datasets_bp.route('/<int:dataset_id>/split', methods=['POST'])
@token_required
def split_dataset(user_id, dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()

        if not dataset:
            raise NotFoundError('Dataset not found')

        data = request.get_json() or {}
        train_ratio = data.get('train_ratio', 0.8)
        val_ratio = data.get('val_ratio', 0.1)
        test_ratio = data.get('test_ratio', 0.1)

        df = DatasetProcessor.load_dataset(dataset.file_path, dataset.file_format)
        splits = DatasetProcessor.split_dataset(df, train_ratio, val_ratio, test_ratio)

        split_dir = os.path.join('uploads', f'dataset_{dataset.id}_splits')
        DatasetProcessor.save_splits(splits, split_dir)

        dataset.train_samples = len(splits['train'])
        dataset.val_samples = len(splits['val'])
        dataset.test_samples = len(splits['test'])
        db.session.commit()

        return jsonify({
            'dataset_id': dataset.id,
            'train_samples': dataset.train_samples,
            'val_samples': dataset.val_samples,
            'test_samples': dataset.test_samples,
            'split_dir': split_dir
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error splitting dataset: {str(e)}")
        return jsonify({'error': 'Failed to split dataset'}), 500

@datasets_bp.route('/<int:dataset_id>', methods=['DELETE'])
@token_required
def delete_dataset(user_id, dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()

        if not dataset:
            raise NotFoundError('Dataset not found')

        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)

        db.session.delete(dataset)
        db.session.commit()

        logger.info(f"Dataset deleted: {dataset_id}")

        return jsonify({'message': 'Dataset deleted'}), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting dataset: {str(e)}")
        return jsonify({'error': 'Failed to delete dataset'}), 500

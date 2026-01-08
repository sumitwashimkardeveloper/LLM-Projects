from app.celery_app import app
from app.models import db
from app.models.training_job import TrainingJob
from app.models.model_metadata import ModelMetadata, Checkpoint
from app.models.dataset import Dataset
from app.utils.training_utils import ModelTrainer, TrainingConfig, LoRAConfig
from datasets import load_dataset
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

@app.task(bind=True)
def train_model(self, training_job_id):
    try:
        from app import create_app
        app_instance = create_app()

        with app_instance.app_context():
            training_job = TrainingJob.query.get(training_job_id)
            if not training_job:
                raise ValueError(f"Training job {training_job_id} not found")

            training_job.status = 'running'
            training_job.current_step = 0
            db.session.commit()

            base_model = ModelMetadata.query.get(training_job.model_id)
            dataset = Dataset.query.get(training_job.dataset_id)

            if not base_model or not dataset:
                raise ValueError("Model or dataset not found")

            trainer = ModelTrainer(
                base_model.huggingface_id,
                training_type=training_job.training_type,
                use_4bit=training_job.use_4bit,
                use_8bit=training_job.use_8bit
            )

            trainer.load_model()

            if training_job.training_type in ['lora', 'qlora']:
                lora_config = LoRAConfig(
                    r=training_job.lora_r,
                    lora_alpha=training_job.lora_alpha,
                    lora_dropout=training_job.lora_dropout,
                    target_modules=training_job.lora_target_modules or ["q_proj", "v_proj"]
                )
                trainer.apply_lora(lora_config)

            os.makedirs(training_job.output_dir, exist_ok=True)

            training_config = TrainingConfig(
                output_dir=training_job.output_dir,
                num_train_epochs=training_job.num_epochs,
                per_device_train_batch_size=training_job.batch_size,
                learning_rate=training_job.learning_rate,
                save_steps=training_job.save_steps
            )

            train_data = load_dataset('json', data_files=dataset.file_path)['train']

            train_dataset, eval_dataset = train_data.train_test_split(test_size=0.1).values()

            def update_progress(step):
                training_job.current_step = step
                training_job.progress = min(100, (step / (training_job.num_epochs * len(train_dataset))) * 100)
                db.session.commit()

            trainer.train(train_dataset, eval_dataset, training_config)

            if training_job.training_type in ['lora', 'qlora']:
                trainer.save_adapter(training_job.output_dir)
            else:
                trainer.save_model(training_job.output_dir)

            checkpoint = Checkpoint(
                training_job_id=training_job_id,
                checkpoint_name='final_checkpoint',
                step=training_job.current_step,
                checkpoint_path=training_job.output_dir,
                is_best=True
            )
            db.session.add(checkpoint)

            training_job.status = 'completed'
            training_job.progress = 100.0
            db.session.commit()

            logger.info(f"Training job {training_job_id} completed")
            return {'status': 'completed', 'job_id': training_job_id}

    except Exception as e:
        logger.error(f"Training job {training_job_id} failed: {str(e)}")

        from app import create_app
        app_instance = create_app()
        with app_instance.app_context():
            training_job = TrainingJob.query.get(training_job_id)
            if training_job:
                training_job.status = 'failed'
                training_job.error_message = str(e)
                db.session.commit()

        raise

@app.task
def process_dataset(dataset_id):
    try:
        from app import create_app
        app_instance = create_app()

        with app_instance.app_context():
            dataset = Dataset.query.get(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")

            dataset.status = 'processing'
            db.session.commit()

            from app.utils.dataset_utils import DatasetProcessor

            DatasetProcessor.validate_file(dataset.file_path, dataset.file_format)
            df = DatasetProcessor.load_dataset(dataset.file_path, dataset.file_format)
            stats = DatasetProcessor.get_dataset_stats(df)

            dataset.total_samples = stats['total_rows']
            dataset.metadata = stats
            dataset.status = 'processed'
            db.session.commit()

            logger.info(f"Dataset {dataset_id} processed")
            return {'status': 'processed', 'dataset_id': dataset_id}

    except Exception as e:
        logger.error(f"Dataset processing failed: {str(e)}")
        raise

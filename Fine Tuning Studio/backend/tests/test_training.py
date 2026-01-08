import pytest
from app import create_app
from app.models import db
from app.models.user import User
from app.models.model_metadata import ModelMetadata
from app.models.dataset import Dataset
from app.models.training_job import TrainingJob

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def model(app):
    with app.app_context():
        model = ModelMetadata(
            name='Test Model',
            model_type='llama',
            model_size='7b',
            huggingface_id='meta-llama/Llama-2-7b-hf'
        )
        db.session.add(model)
        db.session.commit()
        return model

@pytest.fixture
def dataset(app, user):
    with app.app_context():
        dataset = Dataset(
            name='Test Dataset',
            user_id=user.id,
            file_path='/tmp/test.jsonl',
            file_format='jsonl'
        )
        db.session.add(dataset)
        db.session.commit()
        return dataset

def get_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return response.json['tokens']['access_token']

def test_create_training_job(client, user, model, dataset):
    token = get_token(client)
    job_data = {
        'name': 'Test Training',
        'model_id': model.id,
        'dataset_id': dataset.id,
        'training_type': 'lora',
        'batch_size': 4,
        'num_epochs': 3,
        'learning_rate': 2e-4
    }

    response = client.post(
        '/api/training/jobs',
        json=job_data,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201
    assert response.json['name'] == 'Test Training'
    assert response.json['status'] == 'queued'

def test_list_training_jobs(client, user):
    token = get_token(client)
    response = client.get(
        '/api/training/jobs',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_training_job(client, user, model, dataset):
    token = get_token(client)

    with client.application.app_context():
        job = TrainingJob(
            name='Test Job',
            user_id=user.id,
            model_id=model.id,
            dataset_id=dataset.id,
            training_type='lora',
            output_dir='/tmp/output'
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    response = client.get(
        f'/api/training/jobs/{job_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json['name'] == 'Test Job'

def test_start_training_job(client, user, model, dataset):
    token = get_token(client)

    with client.application.app_context():
        job = TrainingJob(
            name='Test Job',
            user_id=user.id,
            model_id=model.id,
            dataset_id=dataset.id,
            training_type='lora',
            status='queued',
            output_dir='/tmp/output'
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    response = client.post(
        f'/api/training/jobs/{job_id}/start',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

def test_cancel_training_job(client, user, model, dataset):
    token = get_token(client)

    with client.application.app_context():
        job = TrainingJob(
            name='Test Job',
            user_id=user.id,
            model_id=model.id,
            dataset_id=dataset.id,
            training_type='lora',
            status='running',
            output_dir='/tmp/output'
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    response = client.post(
        f'/api/training/jobs/{job_id}/cancel',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

def test_missing_required_fields(client, user):
    token = get_token(client)
    job_data = {
        'name': 'Test Training'
    }

    response = client.post(
        '/api/training/jobs',
        json=job_data,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

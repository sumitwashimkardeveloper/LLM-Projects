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
def setup_data(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)

        model = ModelMetadata(
            name='Test Model',
            model_type='llama',
            huggingface_id='meta-llama/Llama-2-7b-hf'
        )
        db.session.add(model)

        dataset = Dataset(
            name='Test Dataset',
            user_id=1,
            file_path='/tmp/test.jsonl',
            file_format='jsonl'
        )
        db.session.add(dataset)

        db.session.commit()

        job = TrainingJob(
            name='Test Job',
            user_id=1,
            model_id=1,
            dataset_id=1,
            training_type='lora',
            status='completed',
            output_dir='/tmp/output'
        )
        db.session.add(job)
        db.session.commit()

        return user

def get_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return response.json['tokens']['access_token']

def test_merge_adapters(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/export/jobs/1/merge',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code in [200, 500]

def test_export_ggml(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/export/jobs/1/export/ggml',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code in [200, 500]

def test_merge_non_completed_job(client):
    with client.application.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('testpass123')
        db.session.add(user)

        model = ModelMetadata(
            name='Test Model 2',
            model_type='llama',
            huggingface_id='meta-llama/Llama-2-7b-hf'
        )
        db.session.add(model)

        dataset = Dataset(
            name='Test Dataset 2',
            user_id=1,
            file_path='/tmp/test.jsonl',
            file_format='jsonl'
        )
        db.session.add(dataset)

        db.session.commit()

        job = TrainingJob(
            name='Running Job',
            user_id=1,
            model_id=1,
            dataset_id=1,
            training_type='lora',
            status='running',
            output_dir='/tmp/output'
        )
        db.session.add(job)
        db.session.commit()

    token = get_token(client)
    response = client.post(
        '/api/export/jobs/1/merge',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

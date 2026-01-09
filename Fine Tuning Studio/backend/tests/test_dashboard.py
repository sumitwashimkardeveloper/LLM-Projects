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
            output_dir='/tmp/output',
            current_loss=0.5,
            best_loss=0.4,
            progress=50.0
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

def test_dashboard_overview(client, setup_data):
    token = get_token(client)
    response = client.get(
        '/api/dashboard/overview',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert 'total_jobs' in response.json
    assert response.json['total_jobs'] >= 0

def test_get_job_progress(client, setup_data):
    token = get_token(client)
    response = client.get(
        '/api/dashboard/jobs/1/progress',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert 'progress' in response.json
    assert response.json['progress'] == 50.0

def test_compare_jobs(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/dashboard/jobs/compare',
        json={'job_ids': [1]},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_best_checkpoint(client, setup_data):
    token = get_token(client)
    response = client.get(
        '/api/dashboard/jobs/1/checkpoints/best',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404

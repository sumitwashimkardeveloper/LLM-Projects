import pytest
from app import create_app
from app.models import db
from app.models.user import User
from app.models.model_metadata import ModelMetadata

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
        db.session.commit()

        return user

def get_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return response.json['tokens']['access_token']

def test_inference_missing_fields(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/inference/test',
        json={'text': 'Hello'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

def test_batch_inference_invalid_texts(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/inference/test/batch',
        json={'model_id': 1, 'texts': []},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

def test_compare_models_missing_ids(client, setup_data):
    token = get_token(client)
    response = client.post(
        '/api/inference/compare',
        json={},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

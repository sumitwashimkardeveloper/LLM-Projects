import pytest
import io
from app import create_app
from app.models import db
from app.models.user import User
from app.models.dataset import Dataset

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

def get_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return response.json['tokens']['access_token']

def test_upload_dataset(client, user):
    token = get_token(client)
    csv_data = b'text,label\nHello world,1\nGood morning,2'
    data = {
        'file': (io.BytesIO(csv_data), 'test.csv'),
        'name': 'Test Dataset',
        'description': 'Test Description'
    }

    response = client.post(
        '/api/datasets',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )

    assert response.status_code == 201
    assert response.json['name'] == 'Test Dataset'

def test_list_datasets(client, user):
    token = get_token(client)
    response = client.get(
        '/api/datasets',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_dataset(client, user):
    token = get_token(client)

    with client.application.app_context():
        dataset = Dataset(
            name='Test Dataset',
            user_id=user.id,
            file_path='/tmp/test.csv',
            file_format='csv'
        )
        db.session.add(dataset)
        db.session.commit()
        dataset_id = dataset.id

    response = client.get(
        f'/api/datasets/{dataset_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json['name'] == 'Test Dataset'

def test_invalid_file_type(client, user):
    token = get_token(client)
    invalid_data = b'invalid'
    data = {
        'file': (io.BytesIO(invalid_data), 'test.txt'),
    }

    response = client.post(
        '/api/datasets',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400

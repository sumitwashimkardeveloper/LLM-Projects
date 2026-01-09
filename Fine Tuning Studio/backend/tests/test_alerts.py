import pytest
from app import create_app
from app.models import db
from app.models.user import User

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
        user = User(username='testuser', email='test@example.com')
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

def test_get_alerts(client, user):
    token = get_token(client)
    response = client.get(
        '/api/alerts',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_notify_completion_missing_fields(client, user):
    token = get_token(client)
    response = client.post(
        '/api/alerts/notify/completion',
        json={'job_id': 1},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

def test_notify_completion(client, user):
    token = get_token(client)
    response = client.post(
        '/api/alerts/notify/completion',
        json={
            'job_id': 1,
            'job_name': 'Test Job',
            'status': 'completed'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

def test_notify_resource_limit(client, user):
    token = get_token(client)
    response = client.post(
        '/api/alerts/notify/resource',
        json={
            'job_id': 1,
            'resource_type': 'gpu_memory',
            'limit': 24,
            'current': 25
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

def test_notify_error(client, user):
    token = get_token(client)
    response = client.post(
        '/api/alerts/notify/error',
        json={
            'job_id': 1,
            'error_message': 'OOM error'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

import pytest
from app import create_app
from app.models import db
from app.models.user import User

@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'full_name': 'Test User'
    })

    assert response.status_code == 201
    assert response.json['user']['username'] == 'testuser'
    assert response.json['user']['email'] == 'test@example.com'
    assert 'access_token' in response.json['tokens']

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'testpass123'
    })

    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'testpass123'
    })

    assert response.status_code == 409

def test_login_user(client):
    """Test user login"""
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })

    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })

    assert response.status_code == 200
    assert response.json['user']['username'] == 'testuser'
    assert 'access_token' in response.json['tokens']

def test_login_invalid_password(client):
    """Test login with invalid password"""
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })

    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_ping(client):
    """Test ping endpoint"""
    response = client.get('/api/ping')
    assert response.status_code == 200
    assert response.json['message'] == 'pong'

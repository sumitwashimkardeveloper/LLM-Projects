import pytest
from app import create_app
from app.models import db
from app.models.user import User
from app.models.collaboration import Team

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

def test_create_team(client, user):
    token = get_token(client)
    response = client.post(
        '/api/collaboration/teams',
        json={
            'name': 'Test Team',
            'description': 'Test Description'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201
    assert response.json['name'] == 'Test Team'

def test_list_teams(client, user):
    token = get_token(client)

    client.post(
        '/api/collaboration/teams',
        json={'name': 'Test Team'},
        headers={'Authorization': f'Bearer {token}'}
    )

    response = client.get(
        '/api/collaboration/teams',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert len(response.json) >= 1

def test_create_team_missing_name(client, user):
    token = get_token(client)
    response = client.post(
        '/api/collaboration/teams',
        json={'description': 'No name'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

def test_add_team_member(client, user):
    token = get_token(client)

    team_response = client.post(
        '/api/collaboration/teams',
        json={'name': 'Test Team'},
        headers={'Authorization': f'Bearer {token}'}
    )

    team_id = team_response.json['id']

    with client.application.app_context():
        user2 = User(username='testuser2', email='test2@example.com')
        user2.set_password('testpass123')
        db.session.add(user2)
        db.session.commit()
        user2_id = user2.id

    response = client.post(
        f'/api/collaboration/teams/{team_id}/members',
        json={'user_id': user2_id, 'role': 'member'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201

def test_save_config_version(client, user):
    token = get_token(client)
    response = client.post(
        '/api/collaboration/config-versions',
        json={
            'name': 'Config v1',
            'config_data': {'lr': 0.001, 'epochs': 3},
            'description': 'Initial config'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201
    assert response.json['name'] == 'Config v1'

def test_list_config_versions(client, user):
    token = get_token(client)

    client.post(
        '/api/collaboration/config-versions',
        json={
            'name': 'Config v1',
            'config_data': {'lr': 0.001}
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    response = client.get(
        '/api/collaboration/config-versions',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert len(response.json) >= 1

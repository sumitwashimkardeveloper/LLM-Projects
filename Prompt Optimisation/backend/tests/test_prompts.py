import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base
from app.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_NAME = "Test User"

TEST_PROMPT_TITLE = "Test Prompt"
TEST_PROMPT_CONTENT = "You are a helpful assistant. Answer the following question: {query}"
TEST_PROMPT_MODEL = "gpt-3.5-turbo"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_token():
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


class TestPromptCRUD:
    def test_create_prompt(self, user_token):
        response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
                "tags": ["test", "example"],
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == TEST_PROMPT_TITLE
        assert data["content"] == TEST_PROMPT_CONTENT
        assert data["model"] == TEST_PROMPT_MODEL

    def test_get_prompt(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        response = client.get(f"/api/prompts/{prompt_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
        assert data["title"] == TEST_PROMPT_TITLE

    def test_list_prompts(self, user_token):
        client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        response = client.get("/api/prompts/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["prompts"]) == 1

    def test_update_prompt(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        response = client.put(
            f"/api/prompts/{prompt_id}",
            json={"title": "Updated Prompt Title"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Prompt Title"

    def test_delete_prompt(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        response = client.delete(f"/api/prompts/{prompt_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 204


class TestVersioning:
    def test_create_version(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        response = client.post(
            f"/api/prompts/{prompt_id}/versions",
            json={
                "content": "Updated prompt content: {query}",
                "model": "gpt-4",
                "change_description": "Improved instruction clarity",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version_number"] == 2

    def test_get_versions(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        client.post(
            f"/api/prompts/{prompt_id}/versions",
            json={
                "content": "Updated content",
                "model": "gpt-4",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        response = client.get(f"/api/prompts/{prompt_id}/versions", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["version_number"] == 1
        assert data[1]["version_number"] == 2

    def test_rollback_version(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": TEST_PROMPT_CONTENT,
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]
        initial_content = TEST_PROMPT_CONTENT

        version_response = client.post(
            f"/api/prompts/{prompt_id}/versions",
            json={
                "content": "New content that we don't like",
                "model": "gpt-4",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        versions = client.get(f"/api/prompts/{prompt_id}/versions", headers={"Authorization": f"Bearer {user_token}"}).json()
        version_1_id = versions[0]["id"]

        rollback_response = client.post(
            f"/api/prompts/{prompt_id}/rollback/{version_1_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert rollback_response.status_code == 200
        data = rollback_response.json()
        assert data["content"] == initial_content

    def test_compare_versions(self, user_token):
        create_response = client.post(
            "/api/prompts/",
            json={
                "title": TEST_PROMPT_TITLE,
                "description": "A test prompt",
                "content": "Original content",
                "model": TEST_PROMPT_MODEL,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        prompt_id = create_response.json()["id"]

        client.post(
            f"/api/prompts/{prompt_id}/versions",
            json={
                "content": "Modified content",
                "model": "gpt-4",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        versions = client.get(f"/api/prompts/{prompt_id}/versions", headers={"Authorization": f"Bearer {user_token}"}).json()
        v1_id = versions[0]["id"]
        v2_id = versions[1]["id"]

        response = client.post(
            f"/api/prompts/{prompt_id}/compare?version_1_id={v1_id}&version_2_id={v2_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["version_1_id"] == v1_id
        assert data["version_2_id"] == v2_id


class TestAuthentication:
    def test_register_user(self):
        response = client.post(
            "/api/auth/register",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        assert data["full_name"] == TEST_USER_NAME

    def test_login_user(self, user_token):
        assert user_token is not None

    def test_get_current_user(self, user_token):
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base

test_engine = create_engine(
    # 임시 DB를 사용하기 위해 작성, 실제 DB를 건들지 않기 위해
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally :
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind = test_engine)

def make_auth_headers(client, username, password="test1234"):
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}



@pytest.fixture
def auth_headers(client):
    return make_auth_headers(client, "testuser")

@pytest.fixture
def other_auth_headers(client):
    return make_auth_headers(client, "otheruser")
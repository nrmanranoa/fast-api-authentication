from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base
from app import database

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_create_duplicate_user():
    # Create a user
    client.post("/users", json={"email": "test@example.com", "password": "testpassword"})
    
    # Try to create the same user again
    response = client.post(
        "/users",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert "Email already registered" in response.text

def test_login():
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200

def test_fail_login():
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "failloginpassword"},
    )
    assert response.status_code == 403

def setup():
    Base.metadata.create_all(bind=engine)

def teardown():
    Base.metadata.drop_all(bind=engine)
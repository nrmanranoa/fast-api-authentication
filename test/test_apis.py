from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base
from app import database, schemas

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
        json={"email": "test@example.com", "password": "Testpassword1"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_create_duplicate_user():
    # Create a user
    client.post("/users", json={"email": "test@example.com", "password": "Testpassword1"})
    
    # Try to create the same user again
    response = client.post(
        "/users",
        json={"email": "test@example.com", "password": "Testpassword1"},
    )
    assert response.status_code == 409
    assert "Email already registered" in response.text

def test_login():
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "Testpassword1"},
    )
    login_res = schemas.Token(**response.json())
    assert login_res.token_type == "bearer"
    assert response.status_code == 200

def test_fail_login():
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "failloginpassword"},
    )
    assert response.status_code == 401
    assert "Invalid credentials." in response.text

def test_invalid_email_create_user():
    response = client.post(
        "/users",
        data={"username": "testexample.com", "password": "failloginpassword"},
    )
    assert response.status_code == 422
    assert "has exactly one @-sign." in response.text

def test_invalid_email_login():
    response = client.post(
        "/login",
        data={"username": "testexample.com", "password": "failloginpassword"},
    )
    assert response.status_code == 401
    assert "Invalid credentials." in response.text

def test_failed_password_criteria():
    response = client.post(
        "/users",
        json={"email": "failedpassword@example.com", "password": "Testpassword"},
    )
    assert response.status_code == 422
    assert "The password policy requires a minimum length of 8 characters" in response.text

def setup():
    Base.metadata.create_all(bind=engine)

def teardown():
    Base.metadata.drop_all(bind=engine)
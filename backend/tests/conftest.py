"""
Pytest Test Fixtures and Configuration
Sets up an isolated SQLite test database and FastAPI TestClient.
"""
import os
import sys
import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure TESTING environment variable is set
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test_rag.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

# SQLite test engine
TEST_DB_URL = "sqlite:///./test_rag.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_rag.db"):
        try:
            os.remove("./test_rag.db")
        except Exception:
            pass


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Creates a primary test user."""
    user = User(
        name="Alex Morgan",
        email="alex@example.com",
        password_hash=hash_password("Password123!")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Returns access token for the primary test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def user2(db):
    """Creates a second user for testing isolation."""
    user = User(
        name="Jordan Lee",
        email="jordan@example.com",
        password_hash=hash_password("SecretPass456!")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user2_token(user2):
    return create_access_token(subject=str(user2.id))

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from framework.db import Base, get_db
from framework import db as db_module


# Set testing environment: Need to set before we define the app
os.environ["TESTING"] = "true"

from app import app



# Initialize test database once per session
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    db_module.engine = engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Now you can create tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Creates a fresh database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()
    
    # Start a savepoint for nested transactions
    db.begin_nested()
    
    yield db
    
    # Cleanup
    db.rollback()
    db.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_joke_response():
    return {
        "categories": [],
        "created_at": "2020-01-05 13:42:22.980058",
        "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
        "id": "abc123",
        "updated_at": "2020-01-05 13:42:22.980058",
        "url": "https://api.chucknorris.io/jokes/abc123",
        "value": "Chuck Norris can divide by zero."
    }    
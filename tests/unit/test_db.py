import os
import pytest
from unittest import mock
from framework import db
from fastapi.testclient import TestClient
from app import app
from sqlalchemy.exc import OperationalError


@pytest.fixture(autouse=True)
def clear_env():
    """Clear relevant env vars before each test."""
    keys = [
        "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST",
        "POSTGRES_PORT", "POSTGRES_DB"
    ]
    original = {key: os.getenv(key) for key in keys}
    for key in keys:
        os.environ.pop(key, None)
    yield
    for key, val in original.items():
        if val is not None:
            os.environ[key] = val


def test_init_db_success(monkeypatch):
    """Test init_db with all required env vars present."""
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "testdb")

    with mock.patch("framework.db.create_engine") as mock_engine:
        db.init_db()
        expected_url = "postgresql+psycopg2://user:pass@localhost:5432/testdb"
        mock_engine.assert_called_once_with(
            expected_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600
        )
        assert db.SessionLocal is not None
        assert db.engine is not None


@pytest.mark.parametrize("missing_key", [
    "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST",
    "POSTGRES_PORT", "POSTGRES_DB"
])
def test_init_db_missing_env_raises(missing_key, monkeypatch):
    """Ensure missing environment variables raise errors."""
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "testdb")

    monkeypatch.delenv(missing_key, raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        db.init_db()
    assert missing_key in str(exc_info.value)

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from models import ChuckJoke
from datetime import datetime

@pytest.fixture
def client():
    """Returns a test client with the app including middleware and DB."""
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
def test_health_endpoint(client):
    """Test the /health endpoint returns status UP."""
    response = client.get("/api/v1/articles/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


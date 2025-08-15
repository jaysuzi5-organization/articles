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
@patch("main.requests.get")
def test_sample_endpoint_inserts_and_returns_jokes(mock_get, client):
    """
    Test the /sample endpoint fetches a joke, inserts if new,
    and returns the latest 10 jokes.
    """

    # Prepare mock response from external API
    mock_joke = {
        "categories": [],
        "created_at": "2020-01-05 13:42:22.980058",
        "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
        "id": "unique_id_123",
        "updated_at": "2020-01-05 13:42:22.980058",
        "url": "https://api.chucknorris.io/jokes/unique_id_123",
        "value": "Chuck Norris can unit test entire applications with a single assertion."
    }
    mock_get.return_value.json = lambda: mock_joke

    # Call the sample endpoint
    response = client.get("/api/articles/v1/sample")
    assert response.status_code == 200

    data = response.json()
    assert "api_data" in data
    assert "jokes" in data
    assert isinstance(data["jokes"], list)
    assert any(j["joke"] == mock_joke["value"] for j in data["jokes"])

    # Call again to test that duplicate joke is not re-inserted and no error occurs
    response2 = client.get("/api/articles/v1/sample")
    assert response2.status_code == 200

    data2 = response2.json()
    # Joke still present and no duplicates should be inserted
    jokes_texts = [j["joke"] for j in data2["jokes"]]
    assert jokes_texts.count(mock_joke["value"]) == 1

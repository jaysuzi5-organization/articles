def test_health(client):
    """Test the /health endpoint returns UP status."""
    response = client.get("/api/v1/articles/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

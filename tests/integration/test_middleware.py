import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from framework.middleware import LoggingMiddleware

@pytest.fixture
def test_app():
    # Create a fresh FastAPI app with your LoggingMiddleware for isolated testing
    test_app = FastAPI()

    # Import your LoggingMiddleware class from your middleware module
    test_app.add_middleware(LoggingMiddleware)

    # Add a simple test endpoint
    @test_app.get("/test-success")
    async def success_endpoint():
        return {"message": "success"}

    @test_app.get("/test-error")
    async def error_endpoint():
        raise RuntimeError("Test exception")

    return test_app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_logging_middleware_success(client, caplog):
    caplog.set_level("INFO")

    response = client.get("/api/myapp/v1/test-success")

    assert response.status_code == 200
    assert response.json() == {"message": "success"}

    # Check logs for Request and Response events
    request_logs = [r for r in caplog.records if r.levelname == "INFO" and "Request" in r.message]
    response_logs = [r for r in caplog.records if r.levelname == "INFO" and "Response" in r.message]

    assert len(request_logs) == 1
    assert len(response_logs) == 1

    # Optional: check some expected fields in the logged dict (assuming JSON logged)
    for record in request_logs + response_logs:
        for key in ["method", "path", "endpoint", "transaction_id"]:
            assert key in record.message or key in record.args[0] if isinstance(record.args, tuple) else True

def test_logging_middleware_exception(client, caplog):
    caplog.set_level("INFO")

    with pytest.raises(RuntimeError, match="Test exception"):
        client.get("/api/myapp/v1/test-error")

    # Check there is at least one error log for the exception
    error_logs = [r for r in caplog.records if r.levelname == "ERROR" and "Unhandled Exception" in r.message]

    assert len(error_logs) >= 1

    # Optional: check for keys in the error log message
    error_log = error_logs[0]
    for key in ["exception", "stack_trace", "transaction_id"]:
        assert key in error_log.message or key in error_log.args[0] if isinstance(error_log.args, tuple) else True

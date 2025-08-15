import logging
import socket
import time
import uuid
import datetime
import traceback
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from opentelemetry.sdk._logs import LoggingHandler
from starlette.responses import StreamingResponse
import json

# Configure logger
middleware_logger = logging.getLogger("middleware")
middleware_logger.setLevel(logging.INFO)

if not middleware_logger.handlers:
    middleware_logger.addHandler(LoggingHandler())


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging, endpoint normalization, and transaction tracking.

    This middleware intercepts all incoming HTTP requests and outgoing HTTP responses to:
    - Assign a unique transaction ID for each request.
    - Parse and normalize the `version`, `service`, and `endpoint` from API paths.
      * Supports replacing numeric path segments with `{id}` placeholders.
      * Example:
          /api/v1/users/19           → version = v1, service = users, endpoint = users/{id}
          /api/v1/users/info         → version = v1, service = users, endpoint = users/info
          /api/v1/users/openapi.json → version = v1, service = users, endpoint = users/openapi.json
    - Log structured details for both the request and response.
    - Optionally parse JSON request/response bodies.
    - Append the `transaction_id` header to the HTTP response for correlation.

    Logging fields include:
        - level: log severity (INFO/ERROR)
        - event: "Request" or "Response"
        - method: HTTP method (GET, POST, etc.)
        - version: extracted API version (e.g., "v1")
        - service: service derived from the path
        - endpoint: normalized endpoint string
        - path: original request path
        - remote_addr: client IP address
        - hostname: server hostname handling the request
        - transaction_id: UUID assigned to this transaction
        - request_body: parsed JSON or raw string for applicable HTTP methods
        - query_params: dictionary of query parameters
        - duration_seconds: request processing time (response only)
        - status: HTTP status code (response only)
        - response_body: parsed JSON or raw string (response only)
        - exception: exception string (error cases)
        - stack_trace: traceback string (error cases)

    Example log for a GET request:
        {
            "level": "INFO",
            "event": "Request",
            "method": "GET",
            "version": "v1",
            "service": "users",
            "endpoint": "users/{id}",
            "path": "/api/v1/users/42",
            "remote_addr": "192.168.1.10",
            "timestamp": "2025-08-12T22:18:30.123Z",
            "hostname": "my-server",
            "transaction_id": "f1a2c3d4-5678-90ab-cdef-1234567890ab",
            "query_params": {}
        }

    Example response header:
        transaction_id: f1a2c3d4-5678-90ab-cdef-1234567890ab

    Notes:
        - Numeric path segments are replaced with `{id}` to avoid logging sensitive or unique IDs.
        - This middleware does not modify the request path or method.
        - Works with both regular and streaming responses.
    """

    async def dispatch(self, request: Request, call_next):
        transaction_id = str(uuid.uuid4())
        start_time = time.time()

        path = request.url.path
        method = request.method

        version = None
        endpoint = None

        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "api":
            version = parts[1]

            endpoint_parts = []
            for part in parts[2:]:
                if re.fullmatch(r"\d+", part):  # replace numeric IDs
                    endpoint_parts.append("{id}")
                else:
                    endpoint_parts.append(part)
            endpoint = "/".join(endpoint_parts)

        # Read request body if needed
        request_body = None
        if method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = json.loads(body_bytes.decode("utf-8"))
                    except json.JSONDecodeError:
                        request_body = body_bytes.decode("utf-8")
            except Exception:
                request_body = None

        middleware_logger.info({
            "level": "INFO",
            "event": "Request",
            "method": method,
            "version": version,
            "service": "articles",
            "endpoint": endpoint,
            "path": path,
            "remote_addr": request.client.host,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "hostname": socket.gethostname(),
            "transaction_id": transaction_id,
            "request_body": request_body,
            "query_params": dict(request.query_params)
        })

        try:
            response = await call_next(request)
        except Exception as e:
            stack_trace = traceback.format_exc()
            middleware_logger.error({
                "level": "ERROR",
                "event": "Unhandled Exception",
                "method": method,
                "version": version,
                "service": "articles",
                "endpoint": endpoint,
                "path": path,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "exception": str(e),
                "stack_trace": stack_trace,
                "transaction_id": transaction_id,
                "request_body": request_body
            })
            raise e

        # Add transaction_id to response header
        response.headers["transaction_id"] = transaction_id

        # Process response body
        response_body = b''
        if isinstance(response, StreamingResponse):
            async for chunk in response.body_iterator:
                response_body += chunk

            async def new_body_iterator():
                yield response_body

            response = StreamingResponse(
                content=new_body_iterator(),
                status_code=response.status_code,
                media_type=response.media_type,
                headers=response.headers
            )
        else:
            response_body = response.body

        parsed_response_body = None
        if response_body:
            try:
                parsed_response_body = json.loads(response_body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                try:
                    parsed_response_body = response_body.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    parsed_response_body = str(response_body)

        duration = time.time() - start_time
        middleware_logger.info({
            "level": "INFO",
            "event": "Response",
            "method": method,
            "version": version,
            "service": "articles",
            "endpoint": endpoint,
            "path": path,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration_seconds": round(duration, 4),
            "status": response.status_code,
            "transaction_id": transaction_id,
            "response_body": parsed_response_body
        })

        return response

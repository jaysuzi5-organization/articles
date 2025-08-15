"""
app.py

Entry point for the FastAPI application.  
Configures logging, middleware, database connections, routes, and OpenTelemetry instrumentation.

This application follows a modular architecture:
- API endpoints are defined in `api/` modules.
- Database models are located in `models/`.
- Middleware and instrumentation logic is in `framework/`.

Environment Variables:
    TESTING (str): If set to `"true"`, disables middleware and OpenTelemetry, and uses basic logging.

"""

import os
import logging
from time import sleep
from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import framework.db
from models.articles import Base
from api import health, info, articles

# Setup logging before anything else uses it
logger = logging.getLogger(__name__)

if os.getenv("TESTING") != "true":
    from framework.middleware import LoggingMiddleware
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    app_middleware = [LoggingMiddleware]
    otel_enabled = True
else:
    # Basic logging when running tests (no OTEL or custom middleware)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    app_middleware = []
    otel_enabled = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.
    On startup:
        - Attempts to establish a database connection.
        - Retries connection up to `max_retries` times with `retry_delay` seconds between attempts.
        - Initializes database tables if they do not exist.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        Exception: If database connection fails after the maximum number of retries.

    Yields:
        None: Control is returned to the application after startup logic completes.
    """
    max_retries = 5
    retry_delay = 2

    if os.getenv("TESTING") != "true":
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})")
                framework.db.init_db()
                Base.metadata.create_all(bind=framework.db.engine)
                with framework.db.SessionLocal() as session:
                    session.execute(text("SELECT 1"))
                logger.info("Database connection established successfully")
                break
            except Exception as e:
                logger.error(f"Database connection failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached, failing startup")
                    raise
                sleep(retry_delay)

    yield


app = FastAPI(
    title="Articles API",
    version="1.0.0",
    openapi_url="/api/v1/articles/openapi.json",
    docs_url="/api/v1/articles/docs",
    lifespan=lifespan
)

# Add middleware and instrumentation
if os.getenv("TESTING") != "true":
    for mw in app_middleware:
        app.add_middleware(mw)
    if otel_enabled:
        FastAPIInstrumentor.instrument_app(app)

# Register routes
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(articles.router, tags=["articles"])
app.mount("/articles/test", StaticFiles(directory="static", html=True), name="test")

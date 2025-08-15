"""
Database Initialization and Session Management

This module provides:
- A global SQLAlchemy `Base` class for ORM models.
- Database initialization logic that supports both production and testing environments.
- A dependency function for FastAPI routes to get a database session.

Environment Variables for Production:
    POSTGRES_USER     - PostgreSQL username
    POSTGRES_PASSWORD - PostgreSQL password
    POSTGRES_HOST     - Hostname or IP address of the database server
    POSTGRES_PORT     - Database port (default: 5432)
    POSTGRES_DB       - Database name
    DB_POOL_SIZE      - SQLAlchemy pool size (default: 10)
    DB_MAX_OVERFLOW   - Max overflow connections beyond pool_size (default: 20)
    DB_POOL_RECYCLE   - Connection lifetime in seconds before recycling (default: 3600)

Environment Variables for Testing:
    DATABASE_URL - Full SQLAlchemy database URL (e.g., sqlite:///./test.db)

"""

import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

# Global SQLAlchemy declarative base for ORM models
Base = declarative_base()

# Session factory and engine references
SessionLocal: Optional[sessionmaker] = None
engine: Optional[Any] = None


def init_db(database_url: str = None, **engine_kwargs):
    """
    Initialize the database connection and create a session factory.

    This function:
    - Reads database configuration from environment variables if `database_url` is not provided.
    - Creates an SQLAlchemy engine with appropriate connection pooling.
    - Configures `SessionLocal` for use in request-scoped database sessions.

    Args:
        database_url (str, optional):
            Full database connection string. If omitted, values are read from environment variables.
        **engine_kwargs:
            Additional keyword arguments passed to `create_engine()`.

    Raises:
        EnvironmentError:
            If required environment variables are missing for production configuration.
        Exception:
            For any other error during database initialization.

    Example:
        >>> init_db()
        >>> from framework.db import SessionLocal
        >>> session = SessionLocal()
    """
    global SessionLocal, engine

    try:
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")
            if database_url is None:
                # Production configuration from env vars
                required_keys = {
                    "POSTGRES_USER": None,
                    "POSTGRES_PASSWORD": None,
                    "POSTGRES_HOST": None,
                    "POSTGRES_PORT": None,
                    "POSTGRES_DB": None
                }

                missing_vars = []
                for key in required_keys:
                    value = os.getenv(key)
                    if not value:
                        missing_vars.append(key)
                    required_keys[key] = value

                if missing_vars:
                    raise EnvironmentError(
                        f"Missing required environment variables: {', '.join(missing_vars)}"
                    )

                database_url = (
                    f"postgresql+psycopg2://{required_keys['POSTGRES_USER']}:"
                    f"{required_keys['POSTGRES_PASSWORD']}@"
                    f"{required_keys['POSTGRES_HOST']}:"
                    f"{required_keys['POSTGRES_PORT']}/"
                    f"{required_keys['POSTGRES_DB']}"
                )

                # Default production pool config
                pool_config = {
                    "pool_pre_ping": True,
                    "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
                    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
                    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 3600))
                }
                pool_config.update(engine_kwargs)
            else:
                # Testing: use DATABASE_URL as is
                pool_config = engine_kwargs
        else:
            # Explicit database URL provided
            pool_config = engine_kwargs

        logger.info(f"Initializing database with URL: {database_url.split('@')[0]}...@...")  # Mask password
        engine = create_engine(database_url, **pool_config)
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def get_db():
    """
    Dependency function for FastAPI to get a database session.

    This function is designed for use in FastAPI routes:
    - Yields a database session bound to the current request.
    - Ensures the session is closed after the request finishes.

    Yields:
        sqlalchemy.orm.Session: A SQLAlchemy session object.

    Raises:
        RuntimeError:
            If the database has not been initialized via `init_db()`.

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/items/")
        ... def read_items(db: Session = Depends(get_db)):
        ...     return db.query(Item).all()
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

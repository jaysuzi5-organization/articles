"""
articles Model and Pydantic Schema

This module defines:
- The SQLAlchemy ORM model for persisting articles data.
- The Pydantic schema for validating API requests when creating a articles.

"""

from sqlalchemy import Column, DateTime, Integer, String
from framework.db import Base
from datetime import datetime, UTC
from pydantic import BaseModel
from typing import Optional


class articles(Base):
    """
    SQLAlchemy ORM model representing a articles record.

    Attributes:
        id (int): Primary key, unique identifier for the record.
        username (str): Unique username, up to 50 characters. Cannot be null.
        email (str): Unique email address, up to 120 characters. Cannot be null.
        full_name (str | None): Optional full name of the user, up to 100 characters.
        create_date (datetime): Timestamp when the record was created (UTC).
        update_date (datetime): Timestamp when the record was last updated (UTC).

    Notes:
        - `create_date` is automatically set when the record is created.
        - `update_date` is automatically updated whenever the record changes.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    create_date = Column(DateTime, default=lambda: datetime.now(UTC))
    update_date = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)  # auto-update on change
    )

    def __repr__(self):
        """
        Returns a string representation of the articles instance.

        Example:
            <articles(id=1, username='johndoe', email='john@example.com')>
        """
        return f"<articles(id={self.id}, username='{self.username}', email='{self.email}')>"


class articlesCreate(BaseModel):
    """
    Pydantic schema for creating a new articles.

    Attributes:
        username (str): Required username for the new user.
        email (str): Required email address for the new user.
        full_name (str | None): Optional full name of the user.

    Example:
        {
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe"
        }
    """
    username: str
    email: str
    full_name: Optional[str] = None

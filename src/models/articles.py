"""
articles Model and Pydantic Schema

This module defines:
- The SQLAlchemy ORM model for persisting article-related data.
- The Pydantic schema for validating API requests when creating an article.

The articles table stores metadata and scoring information for processed articles,
including relevancy, urgency, costs, and model details.
"""
from sqlalchemy import Column, DateTime, Integer, String, Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, UTC
from pydantic import BaseModel

class Base(DeclarativeBase):
    pass


class Articles(Base):
    """
    SQLAlchemy ORM model representing an article record.

    Attributes:
        article_id (int): Primary key, unique identifier for the record.
        title (str): Title of the article (max 256 characters).
        link (str): URL link to the article (max 256 characters).
        summary (str): Text summary of the article.
        reasons (str): Explanation of why the article was selected or scored.
        tags (str): Comma-separated list of tags or keywords (max 512 characters).
        relevancy_score (int): Numeric score indicating how relevant the article is.
        urgency_score (int): Numeric score indicating urgency level of the article.
        overall_score (int): Calculated combined score for the article.
        input_cost (float): Cost (e.g., API cost) for processing the article input.
        output_cost (float): Cost for generating the article output.
        total_cost (float): Combined cost of input and output.
        model (str): Name or identifier of the AI model used.
        create_date (datetime): Timestamp when the record was created (UTC).
        update_date (datetime): Timestamp when the record was last updated (UTC).

    Notes:
        - `create_date` is automatically set when the record is created.
        - `update_date` is automatically updated whenever the record changes.
    """

    __tablename__ = "articles"

    article_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    link = Column(String(256), nullable=False)
    summary = Column(Text, nullable=False)
    reasons = Column(Text, nullable=False)
    tags = Column(String(512), nullable=False)
    relevancy_score = Column(Integer, nullable=False)
    urgency_score = Column(Integer, nullable=False)
    overall_score = Column(Integer, nullable=False)
    input_cost = Column(Float, nullable=False)
    output_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    model = Column(String(256), nullable=False)
    create_date = Column(DateTime, default=lambda: datetime.now(UTC))
    update_date = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        """
        Returns a string representation of the articles instance.

        Example:
            <articles(id=1, title='AI News', link='https://example.com/article')>
        """
        return f"<articles(id={self.article_id}, title='{self.title}', link='{self.link}')>"


class ArticlesCreate(BaseModel):
    """
    Pydantic schema for creating a new article.

    Attributes:
        title (str): Title of the article.
        link (str): URL link to the article.
        summary (str): Summary text of the article.
        reasons (str): Explanation for selecting or scoring the article.
        tags (str): Comma-separated tags or keywords.
        relevancy_score (int): Relevancy score for the article.
        urgency_score (int): Urgency score for the article.
        overall_score (int): Overall score for ranking purposes.
        input_cost (float): Processing cost for input.
        output_cost (float): Processing cost for output.
        total_cost (float): Combined cost for processing.
        model (str): AI model name or identifier.

    Example:
        {
            "title": "AI Breakthrough in NLP",
            "link": "https://example.com/ai-breakthrough",
            "summary": "Researchers achieved a new benchmark in NLP tasks...",
            "reasons": "Highly relevant to AI research trends",
            "tags": "AI,NLP,Research",
            "relevancy_score": 9,
            "urgency_score": 8,
            "overall_score": 8,
            "input_cost": 0.005,
            "output_cost": 0.012,
            "total_cost": 0.017,
            "model": "gpt-4"
        }
    """
    title: str
    link: str
    summary: str
    reasons: str
    tags: str
    relevancy_score: int
    urgency_score: int
    overall_score: int
    input_cost: float
    output_cost: float
    total_cost: float
    model: str

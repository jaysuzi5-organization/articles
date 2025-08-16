from framework.db import get_db
from models.articles import Articles, ArticlesCreate, ArticlesSearch
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC


router = APIRouter()

def serialize_sqlalchemy_obj(obj):
    """
    Convert a SQLAlchemy ORM model instance into a dictionary.

    Args:
        obj: SQLAlchemy model instance.

    Returns:
        dict: Dictionary containing all column names and their values.
    """
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

@router.get("/api/v1/articles/{article_id}")
def get_articles_by_id(article_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single articles record by ID.

    Args:
        article_id (int): The ID of the record.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The matching articles record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Articles).filter(Articles.article_id == article_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"articles with id {article_id} not found")
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/v1/articles")
def list_articles(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    days_back: int | None = Query(None, ge=0, description="Optional number of days back to filter articles"),
    sort_by: str | None = Query(None, description="Column to sort by (e.g. 'create_date', 'title')"),
    sort_order: str | None = Query(None, regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of articles records, optionally filtered by how many days back.
    Results are sorted by the specified column and order. Defaults to descending by create_date.

    Args:
        page (int): Page number starting from 1.
        limit (int): Maximum number of records to return per page.
        days_back (int | None): Optional number of days back to filter articles.
        sort_by (str | None): Column to sort by (default: 'create_date').
        sort_order (str | None): 'asc' or 'desc' (default: 'desc').
        db (Session): SQLAlchemy database session.

    Returns:
        list[dict]: A list of serialized articles records.
    """
    try:
        query = db.query(Articles)

        # Apply days_back filter if provided
        if days_back is not None:
            cutoff = datetime.now(UTC) - timedelta(days=days_back)
            query = query.filter(Articles.create_date >= cutoff)

        # Sorting
        if sort_by is None:
            # Default sort
            query = query.order_by(Articles.create_date.desc())
        else:
            # Ensure the column exists
            if not hasattr(Articles, sort_by):
                raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")

            column = getattr(Articles, sort_by)
            if sort_order == "asc":
                query = query.order_by(asc(column))
            else:  # default or explicit "desc"
                query = query.order_by(desc(column))

        # Pagination
        offset = (page - 1) * limit
        articles_records = query.offset(offset).limit(limit).all()

        return [serialize_sqlalchemy_obj(item) for item in articles_records]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/v1/articles")
def create_record(
    articles_data: ArticlesCreate = Body(..., description="Data for the new record"),
    db: Session = Depends(get_db)
):
    """
    Create a new articles record.

    Args:
        articles_data (articlesCreate): Data model for the record to create.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The newly created articles record.
    """
    try:
        data = articles_data.model_dump(exclude_unset=True)
        new_record = Articles(**data)
        new_record.create_date = datetime.now(UTC)
        new_record.update_date = datetime.now(UTC)

        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return serialize_sqlalchemy_obj(new_record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/v1/articles/{id}")
def get_articles_by_id(article_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single articles record by ID.

    Args:
        article_id (int): The ID of the record.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The matching articles record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Articles).filter(Articles.article_id == article_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"articles with id {article_id} not found")
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/api/v1/articles/{id}")
def update_articles_full(
    article_id: int,
    articles_data: ArticlesCreate = Body(..., description="Updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Fully update an existing articles record (all fields required).

    Args:
        article_id (int): The ID of the record to update.
        articles_data (articlesCreate): Updated record data (all fields).
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated articles record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Articles).filter(Articles.article_id == article_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"articles with id {article_id} not found")

        data = articles_data.model_dump(exclude_unset=False)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/api/v1/articles/{id}")
def update_articles_partial(
    article_id: int,
    articles_data: ArticlesCreate = Body(..., description="Partial updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing articles record (only provided fields are updated).

    Args:
        article_id (int): The ID of the record to update.
        articles_data (articlesCreate): Partial updated data.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated articles record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Articles).filter(Articles.article_id == article_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"articles with id {article_id} not found")

        data = articles_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/api/v1/articles/{id}")
def delete_articles(article_id: int, db: Session = Depends(get_db)):
    """
    Delete an articles record by ID.

    Args:
        article_id (int): The ID of the record to delete.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Articles).filter(Articles.article_id == article_id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"articles with id {article_id} not found")

        db.delete(record)
        db.commit()
        return {"detail": f"articles with id {article_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/v1/articles/search")
def search_articles(
    search_data: ArticlesSearch = Body(..., description="Search criteria"),
    db: Session = Depends(get_db)
):
    """
    Search for articles matching any of the provided fields.
    Defaults to articles created in the last 24 hours.
    Supports 'value IN field' searches for list-like fields (e.g., tags).
    """
    try:
        filters = []
        data = search_data.model_dump(exclude_unset=True)

        # Default time filter: last 24 hours
        if "create_date" not in data:
            last_24h = datetime.now(UTC) - timedelta(hours=24)
            filters.append(Articles.create_date >= last_24h)

        # Build OR conditions for matching any field
        for field, value in data.items():
            if hasattr(Articles, field):
                column = getattr(Articles, field)

                # Special handling for tags or list-like fields (assuming stored as comma-separated string or array)
                if field == "tags":
                    filters.append(column.ilike(f"%{value}%"))  # tags substring match
                else:
                    filters.append(column == value)

        query = db.query(Articles).filter(and_(*filters))
        results = query.all()

        return [serialize_sqlalchemy_obj(record) for record in results]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
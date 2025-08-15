import pytest
from sqlalchemy import text, inspect
from db import init_db, SessionLocal, engine, Base
from models import ChuckJoke

@pytest.fixture(scope="module")
def db_session():
    # Initialize the DB (engine & SessionLocal)
    init_db()
    Base.metadata.create_all(bind=engine)  # Ensure tables exist

    # Create a new session
    session = SessionLocal()
    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test run

# @pytest.mark.integration
# def test_database_connection_and_crud(db_session):
#     """
#     Integration test to verify connection to the test PostgreSQL database
#     and that basic CRUD operations work with the ChuckJoke model.
#     """
#     # Test raw connection
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT 1"))
#         assert result.scalar() == 1

#     # Verify table existence
#     inspector = inspect(engine)
#     tables = inspector.get_table_names()
#     assert "chuck_jokes" in tables

#     # Test CRUD
#     joke_text = "Integration test Chuck Norris joke."
#     new_joke = ChuckJoke(joke=joke_text)
#     db_session.add(new_joke)
#     db_session.commit()

#     fetched = db_session.query(ChuckJoke).filter_by(joke=joke_text).first()
#     assert fetched is not None
#     assert fetched.joke == joke_text

#     # Cleanup
#     db_session.delete(fetched)
#     db_session.commit()

#     deleted = db_session.query(ChuckJoke).filter_by(joke=joke_text).first()
#     assert deleted is None

import pytest
from datetime import datetime, timedelta
from models.chuck_joke import ChuckJoke

@pytest.mark.integration
def test_chuckjoke_crud(db_session):
    """Test ChuckJoke CRUD operations against the test database."""

    # Create a new joke
    joke_text = "Chuck Norris can divide by zero."
    joke = ChuckJoke(joke=joke_text)

    # Add and commit
    db_session.add(joke)
    db_session.commit()
    assert joke.id is not None

    # Read back
    stored = db_session.query(ChuckJoke).filter_by(joke=joke_text).first()
    assert stored is not None
    assert stored.joke == joke_text
    assert isinstance(stored.create_date, datetime)

    # create_date should be close to now (within 5 seconds)
    assert datetime.utcnow() - stored.create_date < timedelta(seconds=5)

    # Test uniqueness constraint - adding duplicate joke should fail
    duplicate = ChuckJoke(joke=joke_text)
    db_session.add(duplicate)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

    # Update joke text
    stored.joke = "Chuck Norris can count to infinity twice."
    db_session.commit()

    updated = db_session.query(ChuckJoke).filter_by(id=stored.id).first()
    assert updated.joke == "Chuck Norris can count to infinity twice."

    # Delete joke
    db_session.delete(updated)
    db_session.commit()

    deleted = db_session.query(ChuckJoke).filter_by(id=stored.id).first()
    assert deleted is None

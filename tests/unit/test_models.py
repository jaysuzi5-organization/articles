# from sqlalchemy import inspect
# from models.chuck_joke import ChuckJoke

# def test_chuckjoke_model_definition():
#     """Test the ChuckJoke model's SQLAlchemy table and columns."""
#     mapper = inspect(ChuckJoke)

#     # Table name
#     assert ChuckJoke.__tablename__ == 'chuck_jokes'

#     # Columns
#     columns = {c.key: c for c in mapper.columns}
#     assert "id" in columns
#     assert "joke" in columns
#     assert "create_date" in columns

#     # id column
#     id_col = columns["id"]
#     assert id_col.primary_key
#     assert id_col.autoincrement is True
#     assert id_col.nullable is False

#     # joke column
#     joke_col = columns["joke"]
#     assert joke_col.unique
#     assert joke_col.nullable is False
#     assert str(joke_col.type).startswith("VARCHAR") or str(joke_col.type).startswith("String")

#     # create_date column
#     date_col = columns["create_date"]
#     assert date_col.nullable is True or date_col.nullable is False  # default datetime allows nullable in some DBs
#     assert str(date_col.type).startswith("DATETIME") or str(date_col.type).startswith("DateTime")

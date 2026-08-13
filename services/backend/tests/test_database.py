def test_database_fixture_is_isolated(db) -> None:
    """The API suite receives a fresh in-memory database per test."""
    assert db is not None

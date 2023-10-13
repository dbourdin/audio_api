"""Main pytest config file."""

import pytest
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from audio_api.api import deps
from audio_api.app import app
from audio_api.db.base_class import Base
from audio_api.settings import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
def test_db_uri() -> PostgresDsn:
    """Get the Postgres URI."""
    return PostgresDsn.build(
        scheme="postgresql",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        path=f"/{settings.POSTGRES_TEST_DB}",
    )


@pytest.fixture(scope="session", name="testing_session_local")
def init_db(test_db_uri: PostgresDsn) -> Session:
    """Create a new database and yield a sessionmaker. Then drop the db tables."""
    engine = create_engine(test_db_uri, pool_pre_ping=True)

    if not database_exists(engine.url):
        create_database(engine.url)

        # Need to create the uuid extension in the test database if it doesn't exist
        with engine.connect() as con:
            _ = con.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the tables at the beginning of the test session
    # And destroy them at the end
    Base.metadata.create_all(bind=engine)
    yield testing_session_local
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_fixture(testing_session_local):
    """Create a new db session and yield it. Then close it and empty all db tables."""
    try:
        db = testing_session_local()
        yield db
    finally:
        db.close()

        # Empty all tables after each test
        tables = reversed(Base.metadata.sorted_tables)
        if any(tables):
            con = testing_session_local()
            con.execute(
                "TRUNCATE {} RESTART IDENTITY;".format(
                    ",".join(table.name for table in tables)
                )
            )
            con.commit()
            con.close()


@pytest.fixture
def client(db_fixture) -> TestClient:
    """Return a FastAPI test client."""

    def _get_db_override():
        return db_fixture

    app.dependency_overrides[deps.get_db] = _get_db_override
    return TestClient(app)

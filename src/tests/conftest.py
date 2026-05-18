import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from specatalog.models.base import Model

@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    return engine


@pytest.fixture
def db_session(engine):
    Model.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Model.metadata.drop_all(engine)

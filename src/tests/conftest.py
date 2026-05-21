import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from specatalog.models.base import Model
import shutil
import json
from pathlib import Path


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


@pytest.fixture
def test_workspace(tmp_path, monkeypatch):
    # fake workspace
    workspace = tmp_path / "archive_specatalog"
    workspace.mkdir()

    # allowed_values.py bereitstellen
    shutil.copy(
        Path("specatalog/helpers/allowed_values_not_adapted.py"),
        workspace / "allowed_values.py",
    )

    # fake defaults.json
    defaults_dir = Path.home() / ".specatalog" / "defaults.json"
    defaults_dir.mkdir()

    defaults = {
        "base_path": str(workspace),
        "usr_name": "test",
        "password": "test",
        "database_url": "localhost/test",
    }

    with open(defaults_dir / "defaults.json", "w") as f:
        json.dump(defaults, f)

    # monkeypatch.setattr(Path, "home", lambda: tmp_path)

    yield workspace

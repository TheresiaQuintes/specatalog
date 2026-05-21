import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import shutil
import json
from pathlib import Path
import tempfile


TEST_ROOT = None
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent


def pytest_configure():
    global TEST_ROOT
    # create temp root
    TEST_ROOT = Path(tempfile.mkdtemp())

    # fake HOME
    fake_home = TEST_ROOT

    # ~/.specatalog
    specatalog_dir = fake_home / ".specatalog"
    specatalog_dir.mkdir(parents=True)

    Path.home = lambda: fake_home

    # workspace
    workspace = TEST_ROOT / "archive_specatalog"
    workspace.mkdir()

    # provide allowed_values.py
    source_file = (
        PROJECT_ROOT / "specatalog" / "helpers" / "allowed_values_not_adapted.py"
    )
    shutil.copy(Path(source_file), workspace / "allowed_values.py")

    # fake defaults.json
    defaults = {
        "base_path": str(workspace),
        "usr_name": "test",
        "password": "test",
        "database_url": "localhost/test",
    }

    with open(specatalog_dir / "defaults.json", "w") as f:
        json.dump(defaults, f)


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
    from specatalog.models.base import Model

    Model.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Model.metadata.drop_all(engine)

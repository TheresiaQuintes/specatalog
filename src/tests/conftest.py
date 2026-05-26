import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import shutil
import json
from pathlib import Path
import tempfile
from datetime import date



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

@pytest.fixture
def entry_factory(db_session):

    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db_session.add(obj)
        db_session.commit()
        return obj

    return create

@pytest.fixture
def molecule_instance(entry_factory):
    from specatalog.models.molecules import Molecule
    data = dict(name="TestMol",
                molecular_formula="C10H10",
                structural_formula="/tmp/test",
                group="base")

    mol = entry_factory(Molecule, **data)
    return mol

@pytest.fixture
def measurement_instance(entry_factory, molecule_instance):
    from specatalog.models.measurements import Measurement
    data = dict(molecule=molecule_instance,
                method="base",
                temperature=300,
                solvent="Water",
                date=date(2025, 5, 6),
                measured_by="Alice",
                path="/tmp/m1",
                corrected=False,
                evaluated=False)
    ms = entry_factory(Measurement, **data)
    return ms

    mol = entry_factory(Molecule, **data)
    return mol


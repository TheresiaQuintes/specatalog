import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import shutil
import json
from pathlib import Path
import tempfile
from datetime import date
from fixtures import MOLECULE_SPECS, MEASUREMENT_SPECS
import specatalog.models.molecules as mol
import specatalog.models.measurements as ms


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

    data = dict(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="base",
    )

    mol = entry_factory(Molecule, **data)
    return mol


@pytest.fixture
def measurement_instance(entry_factory, molecule_instance):
    from specatalog.models.measurements import Measurement

    data = dict(
        molecule=molecule_instance,
        method="base",
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )
    ms = entry_factory(Measurement, **data)
    return ms


@pytest.fixture(params=list(MOLECULE_SPECS.keys()))
def model_spec(request):
    return MOLECULE_SPECS[request.param]


@pytest.fixture
def model_instance(model_spec):
    return model_spec["class"](**model_spec["factory"]())


@pytest.fixture(params=list(MEASUREMENT_SPECS.keys()))
def measurement_spec(request):
    return MEASUREMENT_SPECS[request.param]


@pytest.fixture
def measurement_instance_pyd(measurement_spec):
    return measurement_spec["class"](**measurement_spec["factory"]())


@pytest.fixture
def db_with_content(entry_factory, db_session):
    def make_molecule(model, **inputs):
        base = dict(
            name="TestMol",
            molecular_formula="C10H10",
            structural_formula="/tmp/test1",
        )
        return entry_factory(model, **{**base, **inputs})

    def make_measurement(model, **inputs):
        base = dict(
            molecule=molecule1,
            temperature=300,
            solvent="water",
            date=date(2025, 5, 6),
            measured_by="Alice",
            path="m6",
            corrected=False,
            evaluated=False,
        )
        return entry_factory(model, **{**base, **inputs})

    # create molecules
    molecule1 = make_molecule(mol.Molecule)

    molecule2 = make_molecule(
        mol.Molecule, structural_formula="/tmp/test2", name="TestMol2"
    )
    make_molecule(mol.Molecule, structural_formula="/tmp/Test3", name="TestMol3")

    make_molecule(
        mol.TDP,
        structural_formula="/tmp/Test4",
        doublet="no1",
        linker="co",
        chromophore="per",
        name="per-co-no1",
    )

    # create measurements
    make_measurement(ms.Measurement)
    make_measurement(ms.Measurement, path="m4", temperature=50, solvent="toluene")
    make_measurement(ms.Measurement, path="m2", temperature=200)
    make_measurement(ms.Measurement, path="m3", temperature=100)
    make_measurement(ms.Measurement, path="m1", temperature=50, molecule=molecule2)
    make_measurement(ms.CWEPR, path="m5", frequency_band="x", attenuation="20dB")
    return db_session

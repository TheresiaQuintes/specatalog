from specatalog.models.base import Model
import time
from sqlalchemy import Column, Integer, String
from specatalog.models.base import TimeStampedModel
from specatalog.models.molecules import  Molecule
from specatalog.models.measurements import Measurement, TREPR
from datetime import datetime, date


class Dummy(TimeStampedModel):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String)

def test_table_exists(engine):
    assert "dummy" in Model.metadata.tables



def test_created_at_is_set(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    assert obj.created_at is not None
    assert isinstance(obj.created_at, datetime)

def test_updated_at_initial(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    assert obj.updated_at is None


def test_updated_at_on_update(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    first_created = obj.created_at

    time.sleep(0.01)  # wichtig für Timestamp-Differenz

    obj.name = "changed"
    db_session.commit()

    assert obj.updated_at is not None
    assert obj.updated_at >= first_created

def test_no_update_does_not_change_timestamp(db_session):
    obj = Dummy(name="test")
    db_session.add(obj)
    db_session.commit()

    created_updated = obj.updated_at


    db_session.commit()  # kein change

    assert obj.updated_at == created_updated


def test_create_molecule(db_session):
    mol = Molecule(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="single",
    )

    db_session.add(mol)
    db_session.commit()

    assert mol.id is not None

def test_create_measurement(db_session):
    mol = Molecule(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="single",
    )
    db_session.add(mol)
    db_session.commit()

    m = Measurement(
        molecule=mol,
        method="base",
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )

    db_session.add(m)
    db_session.commit()

    assert m.id is not None

def test_molecule_has_measurements(db_session):
    mol = Molecule(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="single",
    )
    db_session.add(mol)
    db_session.commit()

    m = Measurement(
        molecule=mol,
        method="base",
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )

    db_session.add(m)
    db_session.commit()

    assert len(mol.measurements) == 1

def test_trepr_polymorphism(db_session):
    mol = Molecule(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="single",
    )
    db_session.add(mol)
    db_session.commit()

    m = TREPR(
        molecule=mol,
        method="trepr",
        temperature=298,
        solvent="Toluene",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m2",
        corrected=False,
        evaluated=False,
        frequency_band="X",
        excitation_wl=532,
        attenuation="10dB",
    )

    db_session.add(m)
    db_session.commit()

    loaded = db_session.query(Measurement).filter_by(id=m.id).one()

    assert isinstance(loaded, TREPR)

def test_cascade_delete(db_session):
    mol = Molecule(
        name="TestMol",
        molecular_formula="C10H10",
        structural_formula="/tmp/test",
        group="single",
    )
    db_session.add(mol)
    db_session.commit()

    m = Measurement(
        molecule=mol,
        method="base",
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )

    db_session.add(m)
    db_session.commit()

    db_session.delete(mol)
    db_session.commit()

    assert db_session.query(Measurement).count() == 0
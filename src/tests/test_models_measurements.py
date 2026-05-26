import specatalog.models.measurements as mmes
from datetime import date

def test_create_measurement(db_session, molecule_instance):
    m = mmes.Measurement(
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

    db_session.add(m)
    db_session.commit()

    assert m.id is not None


def test_molecule_has_measurements(db_session, molecule_instance):
    mol = molecule_instance
    m = mmes.Measurement(
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


def test_trepr_polymorphism(db_session, molecule_instance):

    m = mmes.TREPR(
        molecule=molecule_instance,
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

    loaded = db_session.query(mmes.Measurement).filter_by(id=m.id).one()

    assert isinstance(loaded, mmes.TREPR)


def test_cascade_delete(db_session, molecule_instance):
    mol = molecule_instance
    m = mmes.Measurement(
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

    assert db_session.query(mmes.Measurement).count() == 0

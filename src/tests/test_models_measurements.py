import pytest
from sqlalchemy.exc import IntegrityError

import specatalog.models.measurements as mmes
from datetime import date
from utils import parametrize_measurements


@parametrize_measurements()
def test_create_measurement(
    db_session, entry_factory, molecule_instance, model_class, kwargs
):
    ms = entry_factory(model_class, molecule=molecule_instance, **kwargs)
    assert ms.id is not None


@parametrize_measurements()
def test_polymorphism(
    db_session, entry_factory, molecule_instance, model_class, kwargs
):
    ms = entry_factory(model_class, molecule=molecule_instance, **kwargs)
    loaded = db_session.query(mmes.Measurement).filter_by(id=ms.id).one()
    assert isinstance(loaded, model_class)
    assert ms.id == loaded.id


@parametrize_measurements()
def test_table_entry(db_session, entry_factory, molecule_instance, model_class, kwargs):
    entry_factory(model_class, molecule=molecule_instance, **kwargs)
    loaded = db_session.query(model_class).one()
    assert loaded.temperature == 298


def test_cascade_delete(db_session, molecule_instance):
    mol = molecule_instance
    m = mmes.Measurement(
        molecule=mol,
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


def test_bidirectional_relationship(db_session, molecule_instance):
    mol = molecule_instance
    ms = mmes.Measurement(
        molecule=molecule_instance,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )

    db_session.add(ms)
    db_session.commit()

    assert ms.molecule is mol
    assert ms in mol.measurements


@parametrize_measurements()
def test_set_polymorphic_identity(
    db_session, entry_factory, molecule_instance, model_class, kwargs
):
    with pytest.raises(AttributeError):
        entry_factory(
            model_class, molecule=molecule_instance, method="self_set", **kwargs
        )


def test_measurement_path_unique(db_session, molecule_instance):
    ms1 = mmes.Measurement(
        molecule=molecule_instance,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )
    ms2 = mmes.Measurement(
        molecule=molecule_instance,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )

    db_session.add_all([ms1, ms2])

    with pytest.raises(IntegrityError):
        db_session.commit()


def generate_params():
    rows = [[None if col == row else "bla" for col in range(18)] for row in range(13)]

    rows.extend(
        [
            [None if col == 13 else True for col in range(18)],
            [None if col == 14 else True for col in range(18)],
            [None if col == 15 else True for col in range(18)],
        ]
    )

    rows.extend(
        [
            [None if col == 16 else 1.2 for col in range(18)],
            [None if col == 17 else 1.2 for col in range(18)],
        ]
    )

    return list(zip(*rows))


params = generate_params()


def make_base(molecule, **overrides):
    base = dict(
        molecule=molecule,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    "str_a,str_b,str_c,str_d,str_e,str_f,str_g,str_h,str_i,str_j,str_k,str_l,str_m,"
    "bool_a,bool_b,bool_c,num_a,num_b",
    params,
)
def test_required_values(
    db_session,
    molecule_instance,
    str_a,
    str_b,
    str_c,
    str_d,
    str_e,
    str_f,
    str_g,
    str_h,
    str_i,
    str_j,
    str_k,
    str_l,
    str_m,
    bool_a,
    bool_b,
    bool_c,
    num_a,
    num_b,
):
    ms = mmes.Measurement(
        **make_base(
            molecule_instance,
            temperature=num_a,
            solvent=str_a,
            measured_by=str_b,
            path=str_c,
            corrected=bool_a,
            evaluated=bool_b,
        )
    )

    trepr = mmes.TREPR(
        **make_base(
            molecule_instance,
            frequency_band=str_d,
            excitation_wl=num_b,
            attenuation=str_e,
        )
    )

    cwepr = mmes.CWEPR(
        **make_base(
            molecule_instance,
            frequency_band=str_f,
            attenuation=str_g,
        )
    )

    pulse = mmes.PulseEPR(
        **make_base(
            molecule_instance,
            pulse_experiment=str_h,
        )
    )

    uvvis = mmes.UVVis(
        **make_base(
            molecule_instance,
            dim_cuvette=str_i,
        )
    )

    fluorescence = mmes.Fluorescence(
        **make_base(
            molecule_instance,
            excitation=bool_c,
            excitation_wl=str_j,
        )
    )

    ta = mmes.TA(
        **make_base(
            molecule_instance,
            timedomain=str_k,
            excitation_energy=str_l,
            excitation_wl=str_m,
        )
    )

    db_session.add_all([ms, trepr, cwepr, pulse, uvvis, fluorescence, ta])

    with pytest.raises(IntegrityError):
        db_session.commit()

import pytest

import specatalog.models.measurements as mmes
from datetime import date
from utils import parametrize_measurements

@parametrize_measurements()
def test_create_measurement(db_session, entry_factory, molecule_instance, model_class, kwargs):
    ms = entry_factory(model_class, molecule=molecule_instance, **kwargs)
    assert ms.id is not None


@parametrize_measurements()
def test_polymorphism(db_session, entry_factory, molecule_instance, model_class, kwargs):
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
def test_set_polymorphic_identity(db_session, entry_factory, molecule_instance, model_class, kwargs):
    with pytest.raises(AttributeError):
        entry_factory(model_class, molecule=molecule_instance, method="self_set", **kwargs)



    """
    @pytest.mark.parametrize(
    "name1,name2,struct1,struct2",
    [
        # same name
        ("Mol", "Mol", "/tmp/a", "/tmp/b"),

        # same structural_formula
        ("MolA", "MolB", "/tmp/a", "/tmp/a"),
    ],
)
def test_molecule_name_unique(db_session, name1, name2, struct1, struct2):
    mol1 = mol_model.Molecule(
        name=name1,
        structural_formula=struct1,
        group="base",
    )

    mol2 = mol_model.Molecule(
        name=name2,
        structural_formula=struct2,
        group="base",
    )

    db_session.add_all([mol1, mol2])

    with pytest.raises(IntegrityError):
        db_session.commit()


params = [
    tuple(
        None if i == none_index else "bla"
        for i in range(11)
    )
    for none_index in range(11)
]
@pytest.mark.parametrize(
    "a,b,c,d,e,f,g,h,i,j,k",
    params,
)
def test_required_values(db_session, a, b, c, d, e, f, g, h, i, j, k):
    mol = mol_model.Molecule(
        name=a,
        structural_formula=b
    )

    rp = mol_model.RP(
        name="bla",
        structural_formula="bla",
        radical_1=c,
        radical_2=d,
        linker=e)

    tdp = mol_model.TDP(
        name="bla",
        structural_formula="bla",
        doublet=f,
        linker=g,
        chromophore=h)

    ttp = mol_model.TTP(
        name="bla",
        structural_formula="bla",
        triplet_1=i,
        linker=j,
        triplet_2=k)

    db_session.add_all([mol, rp, tdp, ttp])

    with pytest.raises(IntegrityError):
        db_session.commit()
        
        """

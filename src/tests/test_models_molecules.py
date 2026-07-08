from utils import parametrize_molecules
import specatalog.models.molecules as mol_model
import pytest
from sqlalchemy.exc import IntegrityError
from datetime import date


@parametrize_molecules()
def test_create_molecule(db_session, entry_factory, model_class, kwargs):
    mol = entry_factory(model_class, **kwargs)
    assert mol.id is not None


@parametrize_molecules()
def test_polymorphism(db_session, entry_factory, model_class, kwargs):
    mol = entry_factory(model_class, **kwargs)
    loaded = db_session.query(mol_model.Molecule).filter_by(id=mol.id).one()
    assert isinstance(loaded, model_class)
    assert mol.id == loaded.id


@parametrize_molecules()
def test_table_entry(db_session, entry_factory, model_class, kwargs):
    entry_factory(model_class, **kwargs)
    loaded = db_session.query(model_class).one()
    assert loaded.molecular_formula == "C10H10"


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
    tuple(None if i == none_index else "bla" for i in range(11))
    for none_index in range(11)
]


@pytest.mark.parametrize(
    "a,b,c,d,e,f,g,h,i,j,k",
    params,
)
def test_required_values(db_session, a, b, c, d, e, f, g, h, i, j, k):
    mol = mol_model.Molecule(name=a, structural_formula=b)

    rp = mol_model.RP(
        name="bla", structural_formula="bla", radical_1=c, radical_2=d, linker=e
    )

    tdp = mol_model.TDP(
        name="bla", structural_formula="bla", doublet=f, linker=g, chromophore=h
    )

    ttp = mol_model.TTP(
        name="bla", structural_formula="bla", triplet_1=i, linker=j, triplet_2=k
    )

    db_session.add_all([mol, rp, tdp, ttp])

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_multiple_measurements(molecule_instance, entry_factory):
    from specatalog.models.measurements import Measurement

    mol = molecule_instance

    data1 = dict(
        molecule=mol,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m1",
        corrected=False,
        evaluated=False,
    )
    data2 = dict(
        molecule=mol,
        temperature=300,
        solvent="Water",
        date=date(2025, 5, 6),
        measured_by="Alice",
        path="/tmp/m2",
        corrected=False,
        evaluated=False,
    )

    entry_factory(Measurement, **data1)
    entry_factory(Measurement, **data2)

    assert len(mol.measurements) == 2

import pytest
import specatalog.crud_db.create as cr
from specatalog.models.molecules import Molecule


#  TODO: Hinzufügen von Ausnahme, falls ein MoleculeModel in der create-Funktion verwendet wurde (= nicht erlaubt) oder sogar ein nicht erlaubter Wert
def molecule_forbidden_model_instance(model_instance, db_session):
    # model_instance beliebge pydantic-Klasse
    # model_instance = MoleculeModel
    pass


def test_molecule_created(model_instance, db_session):
    if hasattr(model_instance, "model_class"):
        molecule = cr._create_new_molecule(model_instance, db_session)
        assert molecule.id is not None


def test_structural_formula(model_instance, db_session):
    if hasattr(model_instance, "model_class"):
        molecule = cr._create_new_molecule(model_instance, db_session)
        assert molecule.structural_formula == f"molecules/MOL{molecule.id}"


def test_model_class(model_instance, db_session):
    if hasattr(model_instance, "model_class"):
        molecule = cr._create_new_molecule(model_instance, db_session)
        assert isinstance(molecule, model_instance.model_class)


def test_measurement_created(entry_factory, measurement_instance_pyd, db_session):
    if hasattr(
        measurement_instance_pyd, "measurement_class"
    ):  # TODO: Auch hierfür noch einen Ausnahmefall (wie bei den Molekülen)
        molecule = entry_factory(
            Molecule,
            name="TestMol",
            molecular_formula="C10H10",
            structural_formula="/tmp/test",
            group="base",
        )

        measurement_instance_pyd.molecular_id = molecule.id

        measurement = cr._create_new_measurement(measurement_instance_pyd, db_session)

        # measurement exists
        assert measurement.id is not None

        # correct measurement class
        assert isinstance(measurement, measurement_instance_pyd.measurement_class)

        # correct measurement path
        assert measurement.path == f"data/M{measurement.id}"

        # conversion from enum to value
        assert type(measurement.solvent) is str


def test_no_molecule(measurement_instance_pyd, db_session):
    if hasattr(measurement_instance_pyd, "measurement_class"):
        with pytest.raises(ValueError):
            cr._create_new_measurement(measurement_instance_pyd, db_session)

import models.molecules as mol
from main import Session, MOLECULES_PATH, MEASUREMENTS_PATH
from helpers.helper_functions import safe_commit, safe_flush

session = Session()


def create_new_measurement(data):
    molecule = mol.Molecule.query.filter(
        mol.Molecule.id == data.molecular_id).first()
    if molecule is None:
        raise ValueError(f"Kein Molekül mit ID {data.molecular_id} gefunden.")

    metadata = data.model_dump(exclude={"measurement_class"})
    measurement_class = data.measurement_class
    measurement = measurement_class(molecule=molecule, **metadata, path="")

    session.add(measurement)
    safe_flush(session)
    measurement.path = f"{MEASUREMENTS_PATH}/M{measurement.id}"

    safe_commit(session)

    return measurement



def create_new_molecule(data):
    metadata = data.model_dump(exclude={"model_class"})
    model_class = data.model_class
    molecule = model_class(**metadata, structural_formula="")

    session.add(molecule)
    safe_flush(session)
    molecule.structural_formula = f"{MOLECULES_PATH}/MOL{molecule.id}"

    safe_commit(session)

    return molecule

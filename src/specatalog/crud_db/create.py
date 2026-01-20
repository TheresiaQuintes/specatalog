import specatalog.models.molecules as mol

from typing import TypeVar
from specatalog.models.creation_pydantic_measurements import MeasurementModel
from specatalog.models.measurements import Measurement
from specatalog.models.creation_pydantic_molecules import MoleculeModel
from specatalog.models.molecules import Molecule

from specatalog.main import MOLECULES_PATH, MEASUREMENTS_PATH, db_session


measurement_model_pyd = TypeVar(
    "models.creation_pydantic_measurements.MeasurementModel",
    bound=MeasurementModel)
measurement_model_alc = TypeVar("models.measurements.Measurement",
                                bound=Measurement)
molecule_model_pyd = TypeVar(
    "models.creation_pydantic_molecules.MoleculeModel", bound=MoleculeModel)
molecule_model_alc = TypeVar("models.molecules.Measurement", bound=Molecule)


def _create_new_measurement(data: measurement_model_pyd, session: db_session
                            ) -> measurement_model_alc:
    """
    Create a new database entry for the measurement table.

    The entry is created and the measurement_path is set automatically from the
    MEASUREMTS_PATH and the measurement-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MeasurementModel
        Model from models.creation_pydantic_measurements. The subclass of the
        model classifies the experement e.g. cwEPR or trEPR.
    session: db_session
        Object of the class db_session.

    Raises
    ------
    ValueError
        A ValueError is raised in case the molecular id is not existent in the
        data base.

    Returns
    -------
    measurement : Measurement
        Object from the models.mesurements.Measurement class (=sqalchemy model)
        the subclass is dependent on the chosen method.

    """
    molecule = mol.Molecule.query.filter(
        mol.Molecule.id == data.molecular_id).first()
    if molecule is None:
        raise ValueError(f"No molecule with the ID \
                         MOL{data.molecular_id} found.")

    metadata = data.model_dump(exclude={"measurement_class"})
    measurement_class = data.measurement_class
    measurement = measurement_class(molecule=molecule, **metadata, path="")

    session.add(measurement)
    session.flush()
    measurement.path = f"{MEASUREMENTS_PATH}/M{measurement.id}"

    return measurement


def create_new_measurement(data: measurement_model_pyd
                           ) -> measurement_model_alc:
    """
    Create a new database entry for the measurement table.

    The entry is created and the measurement_path is set automatically from the
    MEASUREMTS_PATH and the measurement-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MeasurementModel
        Model from models.creation_pydantic_measurements. The subclass of the
        model classifies the experement e.g. cwEPR or trEPR.

    Raises
    ------
    ValueError
        A ValueError is raised in case the molecular id is not existent in the
        data base.

    Returns
    -------
    measurement : Measurement
        Object from the models.mesurements.Measurement class (=sqalchemy model)
        the subclass is dependent on the chosen method.

    """

    with db_session() as session:
        return _create_new_measurement(data, session)



def _create_new_molecule(data: molecule_model_pyd, session: db_session
                         ) -> molecule_model_alc:
    """
    Create a new database entry for the molecule table.

    The entry is created and the path for the structural formula is set
    automatically from the MEASUREMTS_PATH and the molecule-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MoleculeModel
        Model from models.creation_pydantic_molecules. The class of the
        model classifies the group of the molecule e.g. TDP or RP.
    session: db_session
        Object of the class db_session.

    Returns
    -------
    molecule : Molecule
        Object from the models.molecules.Molecule class (=sqalchemy model).
        The subclass is dependent on the chosen molecule group.

    """
    metadata = data.model_dump(exclude={"model_class"})
    model_class = data.model_class
    molecule = model_class(**metadata, structural_formula="")

    session.add(molecule)
    session.flush
    molecule.structural_formula = f"{MOLECULES_PATH}/MOL{molecule.id}"

    return molecule


def create_new_molecule(data: molecule_model_pyd
                        ) -> molecule_model_alc:
    """
    Create a new database entry for the molecule table.

    The entry is created and the path for the structural formula is set
    automatically from the MEASUREMTS_PATH and the molecule-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MoleculeModel
        Model from models.creation_pydantic_molecules. The class of the
        model classifies the group of the molecule e.g. TDP or RP.

    Returns
    -------
    molecule : Molecule
        Object from the models.molecules.Molecule class (=sqalchemy model).
        The subclass is dependent on the chosen molecule group.

    """

    with db_session() as session:
        return _create_new_molecule(data, session)

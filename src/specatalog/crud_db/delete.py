from specatalog.models.measurements import Measurement
from specatalog.models.molecules import Molecule
from specatalog.models.base import TimeStampedModel

from specatalog.main import db_session



def _delete_object(obj: TimeStampedModel, session: db_session):
    """
    Delete an entry from the database.

    Parameters
    ----------
    obj : TimeStampedModel
        Any object from the models.base.TimeStampedModel (=sqlalchemy model)
        class or from a subclass. The object is deleted from the database.
    session: db_session
        Object of the class db_session.

    Returns
    -------
    None.

    """
    session.delete(obj)
    return

def delete_object(obj: TimeStampedModel):
    """
    Delete an entry from the database.

    Parameters
    ----------
    obj : TimeStampedModel
        Any object from the models.base.TimeStampedModel (=sqlalchemy model)
        class or from a subclass. The object is deleted from the database.

    Returns
    -------
    None.

    """
    with db_session() as session:
        session.delete(obj)

def delete_molecule(mol_id: int):
    """
    Delete an entry from the molecule table with a given molecular-id.

    Parameters
    ----------
    mol_id : int
        ID of the molecule that is to be deleted.

    Raises
    ------
    ValueError
        An error is raised if no molecule with mol_id is part of the database.

    Returns
    -------
    None.

    """
    molecule = Molecule.query.filter(Molecule.id==mol_id).first()
    if molecule is None:
        raise ValueError(f"No molecule with the ID MOL{mol_id} found.")
    delete_object(molecule)
    return

def delete_measurement(ms_id: int):
    """
    Delete an entry from the measurement table with a given measurement-id.

    Parameters
    ----------
    ms_id : int
        ID of the measurement that is to be deleted.

    Raises
    ------
    ValueError
        An error is raised if no measurement with ms_id is part of the
        database.

    Returns
    -------
    None.

    """
    measurement = Measurement.query.filter(Measurement.id==ms_id).first()
    if measurement is None:
        raise ValueError(f"No measurement with the ID M{ms_id} found.")
    delete_object(measurement)

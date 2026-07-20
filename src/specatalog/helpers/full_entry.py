import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import specatalog.data_management.measurement_management as mm
import specatalog.crud_db.create as cr
from specatalog.data_management.remote import SpecatalogArchive
from specatalog.main import db_session
from specatalog.models.measurements import Measurement
from specatalog.crud_db.delete import _delete_object
from specatalog.main import archive


@dataclass
class CreateMeasurementResult:
    """
    Result container for the creation of a full measurement.

    Attributes
    ----------
    success : bool
        Indicates whether the creation process was completed successfully.
    measurement_id : int, optional
        ID of the created measurement entry in the database. This value is
        only set if `success` is True.
    error : Exception, optional
        Exception raised during the creation process. This value is only set
        if `success` is False.
    """

    success: bool
    measurement_id: Optional[int] = None
    error: Optional[Exception] = None


@dataclass
class CreateMoleculeResult:
    """
    Result container for the creation of a full molecule.

    Attributes
    ----------
    success : bool
        Indicates whether the creation process was completed successfully.
    molecular_id : int, optional
        ID of the created molecule entry in the database. This value is
        only set if `success` is True.
    error : Exception, optional
        Exception raised during the creation process. This value is only set
        if `success` is False.
    """

    success: bool
    molecular_id: Optional[int] = None
    error: Optional[Exception] = None


def create_full_measurement(
    data: cr.measurement_model_pyd, raw_data_path: list, fmt: str
) -> CreateMeasurementResult:
    """
    Create a complete measurement entry including database and file system
    operations.

    The creation process is performed in an atomic manner with respect to
    the database. File system operations are first carried out in a temporary
    directory and are only committed to the final archive location after the
    database transaction has been completed successfully.

    The following steps are executed:
    1) Creation of the database entry
    2) Creation of the measurement directory
    3) Copying raw data into the measurement directory
    4) Conversion of raw data to HDF5 format

    Parameters
    ----------
    data: measurement_model
        Measurement creation model containing all required metadata.
    base_dir : Path
        Base directory of the measurement archive.
    raw_data_path : list
        List with the full pathes to each every raw data file that is
        associated with the measurement entry.
    fmt : str
        Format identifier of the raw data.

    Returns
    -------
    CreateMeasurementResult
        Result object indicating success or failure of the creation process.
        In case of success, the measurement ID is provided. In case of failure,
        the raised exception is included.
    """
    try:
        with db_session() as session:
            measurement = cr._create_new_measurement(data, session)
            ms_id = measurement.id

            with tempfile.TemporaryDirectory() as temp_dir:

                temp_archive = SpecatalogArchive(False, temp_dir)
                mm._create_measurement_dir(temp_archive, ms_id)

                for file in raw_data_path:
                    mm._raw_data_to_folder(temp_archive, file, fmt, measurement.id)

                mm._raw_data_to_hdf5(temp_archive, ms_id, fmt)

                src = Path(temp_dir) / str(temp_archive.measurement_path(ms_id))
                archive.copy_directory_to_archive(src, temp_archive.measurement_path(ms_id))

        return CreateMeasurementResult(success=True, measurement_id=measurement.id)

    except Exception as e:
        if archive.exists(f"data/M{ms_id}"):
            archive.delete_folder(f"data/M{ms_id}")
        return CreateMeasurementResult(success=False, error=e)


def delete_full_measurement(base_dir: Path, ms_id: int) -> CreateMeasurementResult:
    """
    Delete a complete measurement entry (with the id ms_id) including database
    and file system operations.

    The deletion process is performed in an atomic manner with respect to
    the database. Only if the database and the file deletion can be carried
    out without errors the changes are committed to the database.

    The following steps are executed:
    1) Deletion of the database entry
    2) Deletion of the measurement directory

    Parameters
    ----------
    base_dir : Path
        Base directory of the measurement archive.
    ms_id : int
        ID of the measurement.

    Returns
    -------
    CreateMeasurementResult
        Result object indicating success or failure of the creation process.
        In case of success, the former measurement ID is provided.
        In case of failure, the raised exception is included.
    """
    try:
        with db_session() as session:
            measurement = Measurement.query.filter(Measurement.id == ms_id).first()
            if measurement is None:
                raise ValueError(f"No measurement with the ID M{ms_id} found.")
            _delete_object(measurement, session)

            mm.delete_measurement(ms_id, save_delete=False)

        return CreateMeasurementResult(success=True, measurement_id=ms_id)

    except Exception as e:
        return CreateMeasurementResult(success=False, error=e)


def create_full_molecule(
    data: cr.molecule_model_pyd, base_dir: Path, molecular_formula_path: Path, fmt: str
) -> CreateMoleculeResult:
    """
    Create a complete molecule entry including database and file system
    operations.

    The creation process is performed in an atomic manner with respect to
    the database. File system operations are first carried out in a temporary
    directory and are only committed to the final archive location after the
    database transaction has been completed successfully.

    The following steps are executed:
    1) Creation of the database entry
    2) Creation of the measurement directory
    3) Copying molecular structure file into the measurement directory

    Parameters
    ----------
    data: molecule_model
        Molecule creation model containing all required metadata.
    base_dir : Path
        Base directory of the measurement archive.
    molecular_formula_path : Path
        Path to the molecular formula file without suffix.
    fmt : str
        Suffix of the molecular formula file. E.g. ".pdf" or ".cdxml"

    Returns
    -------
    CreateMoleculeResult
        Result object indicating success or failure of the creation process.
        In case of success, the molecular ID is provided. In case of failure,
        the raised exception is included.
    """
    temp_base_dir = None
    try:
        with db_session() as session:
            molecule = cr._create_new_molecule(data, session)

            temp_base_dir = Path(tempfile.mkdtemp(dir=base_dir))
            temp_path = Path(temp_base_dir / molecule.structural_formula)
            temp_path.mkdir(parents=True, exist_ok=True)

            molecular_formula_path = Path(molecular_formula_path)
            raw = molecular_formula_path.with_suffix(fmt)
            target = (temp_path / molecule.name).with_suffix(fmt)
            shutil.copy2(raw, target)

        final_dir = base_dir / molecule.structural_formula
        temp_path.rename(final_dir)
        shutil.rmtree(temp_base_dir)

        return CreateMoleculeResult(success=True, molecular_id=molecule.id)

    except Exception as e:
        if temp_base_dir and temp_base_dir.exists():
            shutil.rmtree(temp_base_dir)

        return CreateMoleculeResult(success=False, error=e)

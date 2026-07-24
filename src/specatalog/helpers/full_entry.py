import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import specatalog.data_management.measurement_management as mm
import specatalog.crud_db.create as cr
from specatalog.data_management.archive_manager import SpecatalogArchive
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
    data: cr.measurement_model_pyd,
    raw_data_path: list[str],
    fmt: str
) -> CreateMeasurementResult:
    """Create a complete measurement entry with atomic database and file operations.

    Performs all measurement creation steps in a transaction-safe manner:
    1. Creates database entry
    2. Sets up temporary directory
    3. Copies raw data files
    4. Converts to HDF5 format
    5. Commits to final archive location

    Parameters
    ----------
    data : cr.measurement_model_pyd
        Measurement metadata model
    raw_data_path : list[str]
        List of paths to raw data files
    fmt : str
        Format identifier for raw data

    Returns
    -------
    CreateMeasurementResult
        Result object containing:
        - success: bool indicating operation status
        - measurement_id: int (on success)
        - error: Exception (on failure)

    Notes
    -----
    - Uses temporary directory for atomic file operations
    - Rolls back database and file operations if any step fails
    - Cleans up temporary files on completion
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


def delete_full_measurement(ms_id: int) -> CreateMeasurementResult:
    """Delete a complete measurement entry with atomic database and file operations.

    Performs all deletion steps in a transaction-safe manner:
    1. Deletes database entry
    2. Removes measurement directory
    3. Commits changes only if both operations succeed

    Parameters
    ----------
    ms_id : int
        ID of the measurement to delete

    Returns
    -------
    CreateMeasurementResult
        Result object containing:
        - success: bool indicating operation status
        - measurement_id: int (deleted measurement ID on success)
        - error: Exception (on failure)

    Raises
    ------
    ValueError
        If measurement with given ID doesn't exist

    Notes
    -----
    - Uses database transaction for atomic operations
    - Rolls back file operations if database deletion fails
    - Skips confirmation prompt for file deletion
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
    data: cr.molecule_model_pyd,
    molecular_formula_path: list[str],
    fmt: str
) -> CreateMoleculeResult:
    """Create a complete molecule entry with atomic database and file operations.

    Performs all molecule creation steps in a transaction-safe manner:
    1. Creates database entry
    2. Sets up temporary directory
    3. Copies molecular structure files
    4. Commits to final archive location

    Parameters
    ----------
    data : cr.molecule_model_pyd
        Molecule metadata model
    molecular_formula_path : list[str]
        List of paths to structural formula files
    fmt : str
        File format suffix (e.g., ".pdf") or "all" for multiple formats

    Returns
    -------
    CreateMoleculeResult
        Result object containing:
        - success: bool indicating operation status
        - molecular_id: int (on success)
        - error: Exception (on failure)

    Notes
    -----
    - Uses temporary directory for atomic file operations
    - Supports multiple file formats when fmt="all"
    - Rolls back database and file operations if any step fails
    - Cleans up temporary files on completion
    """

    try:
        with db_session() as session:
            molecule = cr._create_new_molecule(data, session)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_archive = SpecatalogArchive(False, temp_dir)
                temp_archive.make_dir(molecule.structural_formula)

                if fmt == "all":
                    for f in [".pdf", ".cdxml", ".png", ".jpeg", ".jpg", ".svg"]:
                        for raw in molecular_formula_path:
                            raw_f = Path(raw).with_suffix(f)
                            if raw_f.exists():
                                temp_archive.copy_to_archive(raw_f, (Path(molecule.structural_formula) / molecule.name).with_suffix(f))
                                
                else:
                    for raw in molecular_formula_path:
                        raw = Path(raw).with_suffix(fmt)
                        temp_archive.copy_to_archive(raw, (Path(molecule.structural_formula)/molecule.name).with_suffix(fmt))

                src = Path(temp_dir) / molecule.structural_formula
                archive.copy_directory_to_archive(src, molecule.structural_formula)

        return CreateMoleculeResult(success=True, molecular_id=molecule.id)

    except Exception as e:
        if archive.exists(f"molecules/MOL{molecule.id}"):
            archive.delete_folder(f"molecules/MOL{molecule.id}")
        return CreateMoleculeResult(success=False, error=e)

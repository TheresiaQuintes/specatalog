import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import specatalog.data_management.measurement_management as mm
import specatalog.crud_db.create as cr
from specatalog.main import db_session



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

def _create_temp_measurement_dir(base_dir: str):
    """
    Create a temporary directory for a measurement.

    The directory is created inside the ``data`` subdirectory of the given
    base directory and is intended to hold all files related to the
    measurement during the creation process.

    Parameters
    ----------
    base_dir : str
        Base directory of the measurement archive.

    Returns
    -------
    Path
        Path to the newly created temporary directory.

    """
    path = Path(base_dir) / "data"
    temp_dir = Path(tempfile.mkdtemp(dir=path))
    return temp_dir

def _commit_measurement_dir(temp_root: Path, base_dir: Path, ms_id: int):
    """
    Move a temporary measurement directory to its final location.

    Only the directory ``data/M{ms_id}`` is moved from the temporary root
    directory to the final archive directory. The move operation is atomic
    as long as it is performed within the same filesystem.

    Parameters
    ----------
    temp_root : Path
        Root directory of the temporary measurement structure.
    base_dir : Path
        Base directory of the final measurement archive.
    ms_id : int
        ID of the measurement entry.

    """
    temp_measurement_dir = temp_root / "data" / f"M{ms_id}"
    final_measurement_dir = base_dir / "data" / f"M{ms_id}"

    final_measurement_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_measurement_dir.rename(final_measurement_dir)
    shutil.rmtree(temp_root)




def create_full_measurement(data: cr.measurement_model_pyd, base_dir: Path,
                            raw_data_path: Path, fmt:str
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
    raw_data_path : Path
        Path to the raw data file or directory.
    fmt : str
        Format identifier of the raw data.

    Returns
    -------
    CreateMeasurementResult
        Result object indicating success or failure of the creation process.
        In case of success, the measurement ID is provided. In case of failure,
        the raised exception is included.
    """
    temp_dir = None
    try:
        with db_session() as session:
            measurement = cr._create_new_measurement(data, session)

            temp_dir = _create_temp_measurement_dir(base_dir)
            mm.create_measurement_dir(temp_dir, measurement.id)
            mm.raw_data_to_folder(raw_data_path, fmt, temp_dir, measurement.id)
            mm.raw_data_to_hdf5(temp_dir, measurement.id, fmt)

        _commit_measurement_dir(temp_dir, base_dir, measurement.id)

        return CreateMeasurementResult(success=True,
                                       measurement_id=measurement.id)

    except Exception as e:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)

        return CreateMeasurementResult(success=False,
                                       error=e)

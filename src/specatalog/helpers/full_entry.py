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
from collections.abc import Callable

ProgressCallback = Callable[[float, str], None]


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
    fmt: str,
    progress: Optional[ProgressCallback] = None,
) -> CreateMeasurementResult:
    """Create a complete measurement entry with atomic database and file operations.

    Performs all measurement creation steps in a transaction-safe manner:

    1. Creates the database entry.
    2. Sets up a temporary directory.
    3. Creates the temporary measurement directory.
    4. Copies the raw data files.
    5. Converts the raw data to HDF5 format.
    6. Copies the completed measurement to the final archive location.
    7. Commits the database transaction.

    Parameters
    ----------
    data : cr.measurement_model_pyd
        Measurement metadata used to create the database entry.

    raw_data_path : list[str]
        List of paths to the raw data files that should be copied and
        processed.

    fmt : str
        Identifier of the raw data format.

    progress : ProgressCallback, optional
        Optional callback used to report the progress of the operation.
        The callback is called with two arguments:

        - ``fraction`` : float
            Progress value between ``0.0`` and ``1.0``.
        - ``message`` : str
            Human-readable description of the current processing step.

        The callback is independent of the GUI and may, for example, be
        connected to a graphical progress bar by the caller.

    Returns
    -------
    CreateMeasurementResult
        Result object containing the status of the operation.

        If the operation succeeds, ``success`` is ``True`` and
        ``measurement_id`` contains the ID of the created measurement.

        If the operation fails, ``success`` is ``False`` and ``error``
        contains the exception that caused the failure.

    Notes
    -----
    A temporary directory is used to ensure that incomplete files are not
    written directly to the final archive location.

    If an error occurs, database and file operations are rolled back where
    possible, and partially created archive data is removed.

    The ``progress`` callback is optional. If it is ``None``, no progress
    information is reported.

    The function does not depend on Qt or any other GUI framework.

    """

    def report(value: float, message: str) -> None:
        if progress is not None:
            progress(max(0.0, min(1.0, value)), message)

    ms_id = None

    try:
        report(0.0, "Creating database entry...")
        with db_session() as session:
            measurement = cr._create_new_measurement(data, session)
            ms_id = measurement.id

            report(0.10, "Creating temporary directory ...")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_archive = SpecatalogArchive(False, temp_dir)
                mm._create_measurement_dir(temp_archive, ms_id)

                for index, file in enumerate(raw_data_path, start=1):
                    mm._raw_data_to_folder(temp_archive, file, fmt, measurement.id)

                    copy_progress = index / len(raw_data_path)
                    report(
                        0.1 + 0.4 * copy_progress,
                        f"Copying raw file {index}/{len(raw_data_path)}...",
                    )

                report(0.5, "Converting raw data to HDF5...")
                mm._raw_data_to_hdf5(temp_archive, ms_id, fmt)

                report(0.6, "Copying result to archive (this may take a while)...")
                src = Path(temp_dir) / str(temp_archive.measurement_path(ms_id))
                archive.copy_directory_to_archive(
                    src, temp_archive.measurement_path(ms_id)
                )

                report(1.0, "Finished")

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
    fmt: str,
    progress: Optional[ProgressCallback] = None,
) -> CreateMoleculeResult:
    """Create a complete molecule entry with atomic database and file operations.

    Performs all molecule creation steps in a transaction-safe manner:

    1. Creates the database entry.
    2. Sets up a temporary directory.
    3. Creates the temporary molecule directory.
    4. Determines the structural formula files to copy.
    5. Copies the molecular structure files into the temporary archive.
    6. Copies the completed molecule to the final archive location.
    7. Commits the database transaction.

    Parameters
    ----------
    data : cr.molecule_model_pyd
        Molecule metadata used to create the database entry.

    molecular_formula_path : list[str]
        List of paths to structural formula files.

        If ``fmt`` is a specific format, the corresponding suffix is applied
        to each path. If ``fmt`` is ``"all"``, all supported formats are
        searched for and copied if they exist.

    fmt : str
        File format suffix, for example ``".pdf"``, or ``"all"`` to process
        all supported formats.

    progress : ProgressCallback, optional
        Optional callback used to report the progress of the operation.
        The callback is called with two arguments:

        - ``fraction`` : float
            Progress value between ``0.0`` and ``1.0``.
        - ``message`` : str
            Human-readable description of the current processing step.

        The callback is independent of the GUI and may, for example, be
        connected to a graphical progress bar by the caller.

    Returns
    -------
    CreateMoleculeResult
        Result object containing the status of the operation.

        If the operation succeeds, ``success`` is ``True`` and
        ``molecular_id`` contains the ID of the created molecule.

        If the operation fails, ``success`` is ``False`` and ``error``
        contains the exception that caused the failure.

    Notes
    -----
    A temporary directory is used to ensure that incomplete files are not
    written directly to the final archive location.

    If ``fmt`` is ``"all"``, the following file formats are searched for:

    - ``.pdf``
    - ``.cdxml``
    - ``.png``
    - ``.jpeg``
    - ``.jpg``
    - ``.svg``

    If an error occurs, database and file operations are rolled back where
    possible, and partially created archive data is removed.

    The ``progress`` callback is optional. If it is ``None``, no progress
    information is reported.

    The function does not depend on Qt or any other GUI framework.
    """

    def report(fraction: float, message: str) -> None:
        if progress is not None:
            fraction = max(0.0, min(1.0, fraction))
            progress(fraction, message)

    molecule = None
    try:
        report(0.0, "Creating database entry...")
        with db_session() as session:
            molecule = cr._create_new_molecule(data, session)

            report(0.2, "Preparing temporary directory...")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_archive = SpecatalogArchive(False, temp_dir)
                temp_archive.make_dir(molecule.structural_formula)

                if fmt == "all":
                    for f in [".pdf", ".cdxml", ".png", ".jpeg", ".jpg", ".svg"]:
                        for raw in molecular_formula_path:
                            raw_f = Path(raw).with_suffix(f)
                            if raw_f.exists():
                                report(0.6, "Copying raw structure file...")
                                temp_archive.copy_to_archive(
                                    raw_f,
                                    (
                                        Path(molecule.structural_formula)
                                        / molecule.name
                                    ).with_suffix(f),
                                )

                else:
                    for raw in molecular_formula_path:
                        raw = Path(raw).with_suffix(fmt)
                        report(0.6, "Copying raw structure file...")
                        temp_archive.copy_to_archive(
                            raw,
                            (
                                Path(molecule.structural_formula) / molecule.name
                            ).with_suffix(fmt),
                        )
                report(0.9, "Solving temporary directory...")
                src = Path(temp_dir) / molecule.structural_formula
                archive.copy_directory_to_archive(src, molecule.structural_formula)

                report(1, "Finished")

        return CreateMoleculeResult(success=True, molecular_id=molecule.id)

    except Exception as e:
        if archive.exists(f"molecules/MOL{molecule.id}"):
            archive.delete_folder(f"molecules/MOL{molecule.id}")
        return CreateMoleculeResult(success=False, error=e)

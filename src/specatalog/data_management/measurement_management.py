from pathlib import Path
from typing import Union, Optional, Literal

import h5py

import specatalog.data_management.data_loader as l
import numpy as np
from specatalog.main import archive

CATEGORIES = ["raw", "scripts", "figures", "additional_info", "literature"]


def _create_measurement_dir(archive_obj, ms_id: int) -> str:
    """
    Creates a new measurement directory structure with HDF5 file.

    Parameters
    ----------
    archive_obj
        Archive object with directory operations.
    ms_id : int
        Measurement ID number.

    Raises
    ------
    FileExistsError
        If measurement directory or HDF5 file already exists.

    Returns
    -------
    p : str
        Relative path to the new measurement directory from the archive root.

    Notes
    -----
    Creates directory structure with:
    - data/M{ms_id}/
    - Subdirectories: additional_info, figures, literature, raw, scripts
    - HDF5 file with groups: raw_data, corrected_data, evaluations
    """
    p = f"data/M{ms_id}"

    if archive_obj.exists(p):
        raise FileExistsError(f"Measurement folder {p} already exists!")

    for subdir in CATEGORIES:
        p_sub = f"{p}/{subdir}"
        archive_obj.make_dir(p_sub)

    p_measurement = f"{p}/measurement_M{ms_id}.h5"

    if archive_obj.exists(p_measurement):
        raise FileExistsError(f"HDF5 file {p_measurement} already exists!")

    with archive_obj.open_measurement_h5_file(p_measurement, "w") as f:
        f.create_group("raw_data")
        f.create_group("corrected_data")
        f.create_group("evaluations")

    print(f"Measurement directory successfully created at {p}.")
    return p


def create_measurement_dir(ms_id: int) -> str:
    """
    Creates a new measurement directory structure with HDF5 file in the
    archive root folder.

    Parameters
    ----------
    ms_id : int
        Measurement ID number.

    Returns
    -------
    p : str
        Relative path to the new measurement directory from the archive root.

    Notes
    -----
    Creates directory structure with:
    - data/M{ms_id}/
    - Subdirectories: additional_info, figures, literature, raw, scripts
    - HDF5 file with groups: raw_data, corrected_data, evaluations
    """
    return _create_measurement_dir(archive, ms_id)


def _new_file_to_archive(
    archive_obj, src: Union[str, Path], ms_id: int, category: str, update: bool = False
) -> None:
    """
    Copies a file to the archive measurement directory.

    Parameters
    ----------
    archive_obj
        Archive object with directory operations.
    src : Union[str, Path]
        Source file path to be archived.
    ms_id : int
        Measurement ID number.
    category : str
        File category (must be one of: raw, scripts, figures,
        additional_info, literature).
    update : bool, optional
        If False, raises error when file exists (default: False).

    Raises
    ------
    ValueError
        If category is invalid.
    FileNotFoundError
        If source file doesn't exist.
    FileExistsError
        If target file exists and update=False.

    Returns
    -------
    None
    """

    src = Path(src)

    # check category
    if category not in CATEGORIES:
        raise ValueError(
            f"'{category}' is no valid category. The following values are\
                valid: {', '.join(CATEGORIES)}."
        )

    # check source
    if not src.exists():
        raise FileNotFoundError(f"Source file does not exist at: {src}")

    # build target
    dst_dir = archive_obj.measurement_path(ms_id) / category

    archive_obj.make_dir(dst_dir)
    dst_file = dst_dir / src.name

    if archive_obj.exists(dst_file):
        if not update:
            raise FileExistsError(
                f"File at {dst_file} already exists! Use new name or update-function instead"
            )

    archive_obj.copy_to_archive(src, dst_file)
    print(f"Copied {src} to {dst_file}")
    return


def new_file_to_archive(
    src: Union[str, Path], ms_id: int, category: str, update: bool = False
) -> None:
    """
    Copies a file to the archive measurement directory.

    Parameters
    ----------
    src : Union[str, Path]
        Source file path to be archived.
    ms_id : int
        Measurement ID number.
    category : str
        File category (must be one of: raw, scripts, figures,
        additional_info, literature).
    update : bool, optional
        If False, raises error when file exists (default: False).

    Raises
    ------
    ValueError
        If category is invalid.
    FileNotFoundError
        If source file doesn't exist.
    FileExistsError
        If target file exists and update=False.

    Returns
    -------
    None
    """
    _new_file_to_archive(archive, src, ms_id, category, update)


def new_dataset_to_hdf5(
    data: Optional[np.ndarray], h5_file: h5py.File, group_name: str, dataset_name: str
) -> None:
    """
    Writes a new dataset to an HDF5 file.

    Parameters
    ----------
    data : Optional[np.ndarray]
        Data array to be stored. If None, no action is taken.
    h5_file : h5py.File
        Open HDF5 file object.
    group_name : str
        Name of the group where dataset will be created.
    dataset_name : str
        Name of the new dataset.

    Returns
    -------
    None
    """
    if data is None:
        return

    group = h5_file.require_group(group_name)
    group.create_dataset(dataset_name, data=data)
    return


def _raw_data_to_folder(
    archive_obj,
    raw_data_path: str,
    fmt: Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"],
    ms_id: int,
) -> None:
    """
    Copies raw data files to the archive directory. Existing data with the same
    name get overwritten. The data are saved at
    <base_dir>/data/M<ms_id>/raw/<raw_data_file_name>.
    Depending on the format (fmt) all important measurement-files are copied.

    Parameters
    ----------
    raw_data_path : str
        Base path to raw data files (without extension).
    fmt : Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"]
        Data format identifier.
    ms_id : int
        Measurement ID number.

    Raises
    ------
    FileNotFoundError
        If required raw data files are missing.
    ValueError
        If format is not supported.

    Returns
    -------
    None
    """
    # copy all relevant files for Bruker bes3t format (DSC/DTA + optional YGF)
    if fmt == "bruker_bes3t" or fmt == "cw_epr":
        raw_data_1 = Path(raw_data_path).with_suffix(".DSC")
        raw_data_2 = Path(raw_data_path).with_suffix(".DTA")
        raw_data_3 = Path(raw_data_path).with_suffix(".YGF")
        if not raw_data_1.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_1}!")
        if not raw_data_2.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_2}!")

        _new_file_to_archive(archive_obj, raw_data_1, ms_id, "raw", update=True)
        _new_file_to_archive(archive_obj, raw_data_2, ms_id, "raw", update=True)
        if raw_data_3.exists():
            _new_file_to_archive(archive_obj, raw_data_3, ms_id, "raw", update=True)

    # copy all UVvis files
    elif fmt == "uvvis_ulm" or fmt == "uvvis_freiburg":
        raw_data = Path(raw_data_path).with_suffix(".txt")
        if not raw_data.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data}!")

        _new_file_to_archive(archive_obj, raw_data, ms_id, "raw", update=True)

    else:
        raise ValueError(f"Data type: {fmt} unknown!")

    return


def raw_data_to_folder(
    raw_data_path: str,
    fmt: Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"],
    ms_id: int,
) -> None:
    """
    Copies raw data files to the archive directory. Existing data with the same
    name get overwritten. The data are saved at
    <base_dir>/data/M<ms_id>/raw/<raw_data_file_name>.
    Depending on the format (fmt) all important measurement-files are copied.

    Parameters
    ----------
    raw_data_path : str
        Base path to raw data files (without extension).
    fmt : Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"]
        Data format identifier.
    ms_id : int
        Measurement ID number.

    Raises
    ------
    FileNotFoundError
        If required raw data files are missing.
    ValueError
        If format is not supported.

    Returns
    -------
    None
    """
    _raw_data_to_folder(archive, raw_data_path, fmt, ms_id)


def _get_next_rawdata_index(
    h5_file: h5py.File, group_name: str, reference_name: str
) -> int:
    """
    Determines the next available index for a raw dataset series.

    Parameters
    ----------
    h5_file : h5py.File
        Open HDF5 file object.
    group_name : str
        Name of the group containing the datasets.
    reference_name : str
        Base name of the dataset series.

    Returns
    -------
    int
        Next available index (0 for first dataset, increments for subsequent ones).
    """

    grp = h5_file.require_group(group_name)

    i = 0
    while f"{reference_name}_{i}" in grp:
        i += 1

    return i


def _raw_data_to_hdf5(
    archive_obj,
    ms_id: Union[str, int],
    fmt: Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"],
) -> None:
    """
    Write all data from the raw data datafiles in the archive at
    <base_dir>/data/M<ms_id>/raw/
    to the hdf5-file
    <base_dir>/data/M<ms_id>/measurement.h5

    The datasets are saved as arrays in the group 'raw_data'.

    Parameters
    ----------
    archive_obj
        Archive object with file operations.
    ms_id : Union[str, int]
        Measurement ID number.
    fmt : Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"]
        Data format identifier.

    Raises
    ------
    ValueError
        If format is unknown or required files are missing.

    Returns
    -------
    None
    """
    # set the path
    path = archive_obj.measurement_path(ms_id)
    raw_path = path / "raw"
    hdf5_path = path / f"measurement_M{ms_id}.h5"

    # load and save data from Bruker bes3t format
    if fmt == "bruker_bes3t":
        files = archive_obj.list_files(raw_path)
        bases = sorted(
            Path(filename).with_suffix("")
            for filename in files
            if Path(filename).suffix == ".DSC"
        )
        if not bases:
            raise ValueError(f"No raw data at {raw_path}!")

        for base in bases:
            if not archive_obj.exists(raw_path / base.with_suffix(".DTA")):
                raise ValueError(f"{base.name}.DTA not available!")

            # load data to arrays using the loader function
            with archive_obj.temporary_path(raw_path) as data_path:
                data, x, params = l.load_bruker_bes3t(data_path / base, "DSC", "")
                # write intensities to dataset
                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "data_real")

                    new_dataset_to_hdf5(data, h5_file, "raw_data", f"data_{idx}")
                    new_dataset_to_hdf5(
                        data.real, h5_file, "raw_data", f"data_real_{idx}"
                    )
                    new_dataset_to_hdf5(
                        data.imag, h5_file, "raw_data", f"data_imag_{idx}"
                    )

                    # write axes-data
                    if type(x) is list:  # multiple axes
                        for n in range(len(x)):
                            new_dataset_to_hdf5(
                                x[n], h5_file, "raw_data", f"axis_{idx}_{n}"
                            )
                    else:  # only one xaxis
                        new_dataset_to_hdf5(x, h5_file, "raw_data", f"xaxis_{idx}")

                    # add metadata as attributes
                    grp = h5_file.require_group("raw_data")
                    for key, value in params.items():
                        grp.attrs[key] = value

    elif fmt == "cw_epr":
        files = archive_obj.list_files(raw_path)
        bases = sorted(
            Path(filename).with_suffix("")
            for filename in files
            if Path(filename).suffix == ".DSC"
        )
        if not bases:
            raise ValueError(f"No raw data at {raw_path}!")

        for base in bases:
            if not archive_obj.exists(raw_path / base.with_suffix(".DTA")):
                raise ValueError(f"{base.name}.DTA not available!")

            # load data to arrays using the loader function
            with archive_obj.temporary_path(raw_path) as data_path:
                spc_real, spc_imag, field, params = l.load_cw_epr(data_path / base)

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    # write intensities to dataset
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "data_real")
                    new_dataset_to_hdf5(
                        spc_real, h5_file, "raw_data", f"data_real_{idx}"
                    )
                    new_dataset_to_hdf5(
                        spc_imag, h5_file, "raw_data", f"data_imag_{idx}"
                    )
                    new_dataset_to_hdf5(field, h5_file, "raw_data", f"field_{idx}")

                    # add metadata from DSC-file as attributes

                    grp = h5_file.require_group("raw_data")
                    for key, value in params.items():
                        if key is None or value is None:
                            continue
                        grp.attrs[key] = value

    elif fmt == "uvvis_ulm":
        files = archive_obj.list_files(raw_path)
        bases = sorted(
            Path(filename).with_suffix("")
            for filename in files
            if Path(filename).suffix == ".txt"
        )
        if not bases:
            raise ValueError(f"No raw data at {raw_path}!")

        for base in bases:
            with archive_obj.temporary_path(raw_path) as data_path:
                wavelength, intensity, meta = l.load_uvvis_ulm(
                    data_path / base.with_suffix(".txt")
                )

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "intensity")

                    new_dataset_to_hdf5(
                        intensity, h5_file, "raw_data", f"intensity_{idx}"
                    )
                    new_dataset_to_hdf5(
                        wavelength, h5_file, "raw_data", f"wavelength_{idx}"
                    )

                    grp = h5_file.require_group("raw_data")
                    for key, value in meta.items():
                        grp.attrs[key] = value

    elif fmt == "uvvis_freiburg":
        files = archive_obj.list_files(raw_path)
        bases = sorted(
            Path(filename).with_suffix("")
            for filename in files
            if Path(filename).suffix == ".txt"
        )
        if not bases:
            raise ValueError(f"No raw data at {raw_path}!")

        for base in bases:
            with archive_obj.temporary_path(raw_path) as data_path:
                wavelength, intensity, meta = l.load_uvvis_freiburg(
                    data_path / base.with_suffix(".txt")
                )

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "intensity")

                    new_dataset_to_hdf5(
                        intensity, h5_file, "raw_data", f"intensity_{idx}"
                    )
                    new_dataset_to_hdf5(
                        wavelength, h5_file, "raw_data", f"wavelength_{idx}"
                    )

                    grp = h5_file.require_group("raw_data")
                    for key, value in meta.items():
                        grp.attrs[key] = value

    else:
        raise ValueError(f"Data type: {fmt} unknown!")

    print("Raw data were successfully added to hdf5.")
    return


def raw_data_to_hdf5(
    ms_id: Union[str, int],
    fmt: Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"],
) -> None:
    """
    Write all data from the raw data datafiles in the archive at
    <base_dir>/data/M<ms_id>/raw/
    to the hdf5-file
    <base_dir>/data/M<ms_id>/measurement.h5

    The datasets are saved as arrays in the group 'raw_data'.

    Parameters
    ----------
    ms_id : Union[str, int]
        Measurement ID number.
    fmt : Literal["bruker_bes3t", "cw_epr", "uvvis_ulm", "uvvis_freiburg"]
        Data format identifier.

    Raises
    ------
    ValueError
        If format is unknown or required files are missing.

    Returns
    -------
    None
    """
    _raw_data_to_hdf5(archive, ms_id, fmt)


def _delete_element(
    archive_obj, ms_id: int, category: str, filename: str, save_delete: bool = True
) -> None:
    """
    Deletes a file from the archive measurement directory.

    Parameters
    ----------
    archive_obj
        Archive object with file operations.
    ms_id : int
        Measurement ID number.
    category : str
        File category (must be one of: raw, scripts, figures,
        additional_info, literature).
    filename : str
        Name of the file to delete.
    save_delete : bool, optional
        If True, requires confirmation before deletion (default: True).

    Raises
    ------
    ValueError
        If category is invalid.
    FileNotFoundError
        If file doesn't exist.

    Returns
    -------
    None
    """
    if category not in CATEGORIES:
        raise ValueError(
            f"'{category}' is not valid. Allowed values are: \
                         {CATEGORIES}"
        )

    path = archive_obj.measurement_path(ms_id)
    file_path = path / category / filename

    if not archive_obj.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")

    if save_delete:
        confirm = input(f"Delete file? {file_path} (y/N): ")
        if confirm.lower() != "y":
            print("Deletion cancelled")
            return

    archive_obj.delete_file(file_path)
    print(f"Deleted: {file_path}")

    return


def delete_element(ms_id: int, category: str, filename: str, save_delete: bool = True):
    """
    Deletes a file from the archive measurement directory.

    Parameters
    ----------
    ms_id : int
        Measurement ID number.
    category : str
        File category (must be one of: raw, scripts, figures,
        additional_info, literature).
    filename : str
        Name of the file to delete.
    save_delete : bool, optional
        If True, requires confirmation before deletion (default: True).

    Raises
    ------
    ValueError
        If category is invalid.
    FileNotFoundError
        If file doesn't exist.

    Returns
    -------
    None
    """
    _delete_element(archive, ms_id, category, filename, save_delete)


def _delete_measurement(archive_obj, ms_id: int, save_delete: bool = True) -> None:
    """
    Deletes an entire measurement directory from the archive.

    Parameters
    ----------
    archive_obj
        Archive object with directory operations.
    ms_id : int
        Measurement ID number.
    save_delete : bool, optional
        If True, requires confirmation before deletion (default: True).

    Raises
    ------
    FileNotFoundError
        If measurement directory doesn't exist.

    Returns
    -------
    None
    """
    path = archive_obj.measurement_path(ms_id)
    if not archive_obj.exists(path):
        raise FileNotFoundError(f"Measurement does not exist: {path}")

    if save_delete:
        confirm = input(f"Delete WHOLE measurement directory? {path} (y/N): ")
        if confirm.lower() != "y":
            print("Deletion cancelled")
            return

    archive_obj.delete_folder(path)
    print(f"Measurement directory deleted: {path}")
    return


def delete_measurement(ms_id: int, save_delete: bool = True) -> None:
    """
    Deletes an entire measurement directory from the archive.

    Parameters
    ----------
    ms_id : int
        Measurement ID number.
    save_delete : bool, optional
        If True, requires confirmation before deletion (default: True).

    Raises
    ------
    FileNotFoundError
        If measurement directory doesn't exist.

    Returns
    -------
    None
    """
    _delete_measurement(archive, ms_id, save_delete)


def _list_files(archive_obj, ms_id: Union[str, int], category: str = "") -> list[Path]:
    """
    Lists files in a measurement directory or subdirectory.

    Parameters
    ----------
    archive_obj
        Archive object with directory operations.
    ms_id : Union[str, int]
        Measurement ID number.
    category : str, optional
        File category (must be one of: raw, scripts, figures,
        additional_info, literature) or empty for all files.
        Default is "" (all files).

    Raises
    ------
    ValueError
        If category is invalid.

    Returns
    -------
    list[Path]
        List of absolute file paths in the directory.
    """
    if category != "":
        if category not in CATEGORIES:
            raise ValueError(
                f"'{category}' no valid category.\
                             Allowed values are: {CATEGORIES}"
            )

    path = archive_obj.measurement_path(ms_id)
    folder = path / category

    if not archive_obj.exists(folder):  # return empty list
        return []

    files = archive_obj.list_files(folder)

    return files


def list_files(ms_id: Union[str, int], category: str = "") -> list[Path]:
    """
    Lists files in a measurement directory or subdirectory.

    Parameters
    ----------
    ms_id : Union[str, int]
        Measurement ID number.
    category : str, optional
        File category (must be one of: raw, scripts, figures,
        additional_info, literature) or empty for all files.
        Default is "" (all files).

    Raises
    ------
    ValueError
        If category is invalid.

    Returns
    -------
    list[Path]
        List of absolute file paths in the directory.
    """
    return _list_files(archive, ms_id, category)

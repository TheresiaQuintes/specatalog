from pathlib import Path
import specatalog.data_management.data_loader as l
import numpy as np
from specatalog.main import archive

CATEGORIES = ["raw", "scripts", "figures", "additional_info", "literature"]


def _create_measurement_dir(archive_obj, ms_id: int) -> Path:
    """
    Create a new directory for a single measurement with the measurement-ID
    ms_id in the folder of the archive (base_dir). Directory and subdirectories
    are created as well as a hdf5-file for saving the data of the measurement.
    The hdf5-file has three groups: "raw_data", "corrected_data" and
    "evaluations".

    The structure is as follows:

    .. code-block:: text

        base_dir/
        ├── data/
        │   ├── M1/
        │   ├── M2/
        │   ├── M3/
        │   ├── ...
        │   └── M{ms_id}/
        │       ├── additional_info/
        │       ├── figures/
        │       ├── literature/
        │       ├── raw/
        │       ├── scripts/
        │       └── measurement_M{ms_id}.h5
        │
        └── <other directories of the archive>


    Parameters
    ----------
    base_dir : str
        Path to the root-folder of the archive.
    ms_id : int
        Number of the measurement.

    Raises
    ------
    FileExistsError
        An error is raised if the measurement directory already exists.

    Returns
    -------
    path: Path
        Absolute path to the new measurement directory.

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


def create_measurement_dir(ms_id):
    return _create_measurement_dir(archive, ms_id)

def _new_file_to_archive(archive_obj, src: str, ms_id: int, category: str, update=False
):
    """
    Copy a file to the archive. The file is saved at:
    <base_dir>/data/M<ms_id>/<category>/<src_file_name>.

    Parameters
    ----------
    src : str or Path
        Path of the file that is to be saved in the archive.
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.
    category : str
        One of the categories: ["raw", "scripts", "figures", "additional_info",
        "literature"]. The file is copied to the corresponding subfolder.
    update : bool, optional
        If set to false an error is risen in case the file aleardy exists.
        The default is False.

    Raises
    ------
    ValueError
        An error is raised if the category is not one out of the list:
        ["raw", "scripts", "figures", "additional_info", "literature"].
    FileNotFoundError
        An error is raised if the source file does not exist.
    FileExistsError
        An error is raised if the target file exists and update=False.

    Returns
    -------
    None.
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
    dst_file = dst_dir/src.name

    if archive_obj.exists(dst_file):
        if not update:
            raise FileExistsError(
                f"File at {dst_file} already exists! Use new name or update-function instead"
            )

    archive_obj.copy_to_archive(src, dst_file)
    print(f"Copied {src} to {dst_file}")
    return


def new_file_to_archive(src: str, ms_id: int, category: str, update=False):
    _new_file_to_archive(archive, src, ms_id, category, update)

def new_dataset_to_hdf5(
    data: np.ndarray, h5_file, group_name: str, dataset_name: str
):
    """
    Write a new dataset to a hdf5-file.

    Parameters
    ----------
    data : np.ndarray
        An array of data points. If data = None nothing is written to the file.
    hdf5_path : str
        Path to the hdf5-file.
    group_name : str
        Name of the group.
    dataset_name : str
        Name of the dataset.

    Returns
    -------
    None.

    """
    if data is None:
        return


    group = h5_file.require_group(group_name)
    group.create_dataset(dataset_name, data=data)
    return

def _raw_data_to_folder(archive_obj, raw_data_path: str, fmt: str, ms_id: int):
    """
    Copy raw datafiles to the archive. Existing data with the same name get
    overwritten. The data are saved at
    <base_dir>/data/M<ms_id>/raw/<raw_data_file_name>.
    Depending on the format (fmt) all important measurement-files are copied.

    Parameters
    ----------
    raw_data_path : str
        Path to the raw data file without suffix.
    fmt : str
        Format of the raw_data. One of the supported formats ["bruker_bes3t",
        "cw_epr", "uvvis_ulm", "uvvis_freiburg"].
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.

    Raises
    ------
    FileNotFoundError
        An error is raised if the no raw data at the given path can be found.
    ValueError
        An error is raised if the fmt-string is not valid.

    Returns
    -------
    None.

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

def raw_data_to_folder(raw_data_path: str, fmt: str, ms_id: int):
    """
    Copy raw datafiles to the archive. Existing data with the same name get
    overwritten. The data are saved at
    <base_dir>/data/M<ms_id>/raw/<raw_data_file_name>.
    Depending on the format (fmt) all important measurement-files are copied.

    Parameters
    ----------
    raw_data_path : str
        Path to the raw data file without suffix.
    fmt : str
        Format of the raw_data. One of the supported formats ["bruker_bes3t",
        "cw_epr", "uvvis_ulm", "uvvis_freiburg"].
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.

    Raises
    ------
    FileNotFoundError
        An error is raised if the no raw data at the given path can be found.
    ValueError
        An error is raised if the fmt-string is not valid.

    Returns
    -------
    None.

    """
    _raw_data_to_folder(archive, raw_data_path, fmt, ms_id)


def _get_next_rawdata_index(h5_file, group_name, reference_name):
    """
    Determine next free index for a raw dataset series.

    Returns
    -------
    0 -> first dataset (no suffix)
    int  -> suffix number
    """

    grp = h5_file.require_group(group_name)

    i = 0
    while f"{reference_name}_{i}" in grp:
        i += 1

    return i


def _raw_data_to_hdf5(archive_obj, ms_id: str, fmt: str):
    """
    Write all data from the raw data datafiles in the archive at
    <base_dir>/data/M<ms_id>/raw/
    to the hdf5-file
    <base_dir>/data/M<ms_id>/measurement.h5

    The datasets are saved as arrays in the group 'raw_data'.

    Parameters
    ----------
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.
    fmt : str
        Format of the raw_data. One of the supported formats ["bruker_bes3t",
        "cw_epr", "uvvis_ulm", "uvvis_freiburg"].

    Raises
    ------
    ValueError
        An error is raised if the fileformat is not known or if not all
        necessary datafiles are available under the same name.

    Returns
    -------
    None.

    """
    # set the path
    path = archive_obj.measurement_path(ms_id)
    raw_path = path / "raw"
    hdf5_path = path / f"measurement_M{ms_id}.h5"

    # load and save data from Bruker bes3t format
    if fmt == "bruker_bes3t":
        files = archive_obj.list_files(raw_path)
        bases = sorted(Path(filename).with_suffix("") for filename in files if Path(filename).suffix == ".DSC")
        if not bases:
            raise ValueError(f"No raw data at {raw_path}!")

        for base in bases:
            if not archive_obj.exists(raw_path/base.with_suffix(".DTA")):
                raise ValueError(f"{base.name}.DTA not available!")

            # load data to arrays using the loader function
            with archive_obj.temporary_path(raw_path) as data_path:
                data, x, params = l.load_bruker_bes3t(data_path/base, "DSC", "")
                # write intensities to dataset
                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "data_real")

                    new_dataset_to_hdf5(data, h5_file, "raw_data", f"data_{idx}")
                    new_dataset_to_hdf5(data.real, h5_file, "raw_data", f"data_real_{idx}")
                    new_dataset_to_hdf5(data.imag, h5_file, "raw_data", f"data_imag_{idx}")

                    # write axes-data
                    if type(x) is list:  # multiple axes
                        for n in range(len(x)):
                            new_dataset_to_hdf5(x[n], h5_file, "raw_data", f"axis_{idx}_{n}")
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
            if not archive_obj.exists(raw_path/base.with_suffix(".DTA")):
                raise ValueError(f"{base.name}.DTA not available!")

            # load data to arrays using the loader function
            with archive_obj.temporary_path(raw_path) as data_path:
                spc_real, spc_imag, field, params = l.load_cw_epr(data_path/base)

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    # write intensities to dataset
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "data_real")
                    new_dataset_to_hdf5(spc_real, h5_file, "raw_data", f"data_real_{idx}")
                    new_dataset_to_hdf5(spc_imag, h5_file, "raw_data", f"data_imag_{idx}")
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
                wavelength, intensity, meta = l.load_uvvis_ulm(data_path/base.with_suffix(".txt"))

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "intensity")

                    new_dataset_to_hdf5(intensity, h5_file, "raw_data", f"intensity_{idx}")
                    new_dataset_to_hdf5(wavelength, h5_file, "raw_data", f"wavelength_{idx}")

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
                wavelength, intensity, meta = l.load_uvvis_freiburg(data_path/base.with_suffix(".txt"))

                with archive_obj.open_measurement_h5_file(hdf5_path, "a") as h5_file:
                    idx = _get_next_rawdata_index(h5_file, "raw_data", "intensity")

                    new_dataset_to_hdf5(intensity, h5_file, "raw_data", f"intensity_{idx}")
                    new_dataset_to_hdf5(wavelength, h5_file, "raw_data", f"wavelength_{idx}")


                    grp = h5_file.require_group("raw_data")
                    for key, value in meta.items():
                        grp.attrs[key] = value

    else:
        raise ValueError(f"Data type: {fmt} unknown!")

    print("Raw data were successfully added to hdf5.")
    return

def raw_data_to_hdf5(ms_id, fmt):
    _raw_data_to_hdf5(archive, ms_id, fmt)

def _delete_element(archive_obj, ms_id: int, category: str, filename: str, save_delete: bool = True
):
    """
    Delete a file from the archive.

    Parameters
    ----------
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.
    category : str
        One of the categories: ["raw", "scripts", "figures", "additional_info",
        "literature"]. The file is deleted from the corresponding subfolder.
    filename : str
        Name of the file to be deleted
    save_delete : bool, optional
        Ask for confirmation before deletion. The default is True.

    Raises
    ------
    ValueError
        An error is raised if the category is not one out of the list:
        ["raw", "scripts", "figures", "additional_info", "literature"].
    FileNotFoundError
        An error is raised if the file does not exist.

    Returns
    -------
    None.

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
    _delete_element(archive, ms_id, category, filename, save_delete)

def _delete_measurement(archive_obj, ms_id: int, save_delete: bool = True):
    """
    Delete a whole measurement directory from the archive.

    Parameters
    ----------
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.
    save_delete : bool, optional
        Ask for confirmation before deletion. The default is True.

    Raises
    ------
    FileNotFoundError
        An error is raised if the measurement does not exist.

    Returns
    -------
    None.

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

def delete_measurement(ms_id: int, save_delete: bool = True):
    _delete_measurement(archive, ms_id, save_delete)

def _list_files(archive_obj, ms_id: str, category: str = "") -> list:
    """
    List all files in a single measurement directory with the ID ms_id and
    all subdirectorys. If a category is chosen only files of this category
    are listed.

    Parameters
    ----------
    base_dir : str or Path
        Path to the root-folder of the archive.
    ms_id : str or int
        Number of the measurement.
    category : str, optional
        One of the categories: ["raw", "scripts", "figures", "additional_info",
        "literature"] or empty. The contents of the subdirectory is listed.
        The default is "".

    Raises
    ------
    ValueError
        An error is raised if the category is not known.

    Returns
    -------
    filelist : list
        List with absolute paths to all files in the (sub-)directory.

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

def list_files(ms_id: str, category: str = ""):
    return _list_files(archive, ms_id, category)
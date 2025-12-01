from pathlib import Path
import h5py
import shutil
from data_management.data_loader import load
import numpy as np


SUPPORTED_FORMATS = {
    "bruker_bes3t": {".dsc", ".dta"},
} # If new SUPPORTED_FORMATS are added, ad them also to the functions
  # new_raw_data_to_folder and new_raw_data_to_hdf5.


CATEGORIES = ["raw", "scripts", "figures", "additional_info", "literature"]


def create_measurement_dir(base_dir: str, ms_id: int) -> Path:
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
    path = Path(base_dir) / "data" / f"M{ms_id}"
    if path.exists():
        raise FileExistsError(f"Measurement folder {path} already exists!")


    for subdir in CATEGORIES:
        (path / subdir).mkdir(parents=True, exist_ok=True)

    measurement_path = (path / f"measurement_M{ms_id}.h5")
    if measurement_path.exists():
        raise FileExistsError(f"HDF5 file {measurement_path} already exists!")

    with h5py.File(measurement_path, "w") as f:
        f.create_group("raw_data")
        f.create_group("corrected_data")
        f.create_group("evaluations")

    return path


def measurement_path (base_dir: str, ms_id: int) -> Path:
    """
    Create the absolute path to a measurement folder with the ID ms_id.

    Parameters
    ----------
    base_dir : str
        Path to the root-folder of the archive.
    ms_id : int
        Number of the measurement.

    Raises
    ------
    FileNotFoundError
        An error is raised if the measurement folder does not exist.

    Returns
    -------
    path : Path
        Absolute path to the measurement.

    """
    ms_id = f"M{ms_id}"
    path = Path(base_dir) /"data"/ ms_id
    if not path.exists():
        raise FileNotFoundError(f"Measurement folder {path} does not exist!")
    return path


def new_file_to_archive(src: str, base_dir: str, ms_id: int, category: str,
                        update=False):
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
    path = measurement_path(base_dir, ms_id)

    # check category
    if category not in CATEGORIES:
        raise ValueError(
            f"'{category}' is no valid category. The following values are\
                valid: {', '.join(CATEGORIES)}."
        )

    # check source
    if not src.exists():
        raise FileNotFoundError(f"Sorce file does not exist at: {src}")

    # build target
    target_dir = path / category
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / src.name

    # check target_file
    if target_file.exists():
        if not update:
            raise FileExistsError(f"File at {target_file} already exists! Use new name or update-function instead")

    # Copy or update file
    shutil.copy2(src, target_file)
    return


def new_dataset_to_hdf5(data: np.ndarray, hdf5_path: str, group_name: str,
                        dataset_name: str):
    """
    Write a new dataset to a hdf5-file.

    Parameters
    ----------
    data : np.ndarray
        An array of data points.
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
    with h5py.File(hdf5_path, "a") as f:
        group = f.require_group(group_name)
        group.create_dataset(dataset_name, data=data)
        f.close()
    return

def raw_data_to_folder(raw_data_path: str, fmt: str, base_dir: str,
                           ms_id: int):
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
        Format of the raw_data. One of the supported formats ["bruker_bes3t"].
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
    if fmt == "bruker_bes3t":
        raw_data_1 = Path(raw_data_path).with_suffix(".DSC")
        raw_data_2 = Path(raw_data_path).with_suffix(".DTA")
        raw_data_3 = Path(raw_data_path).with_suffix(".YGF")
        if not raw_data_1.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_1}!")
        if not raw_data_2.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_2}!")

        new_file_to_archive(raw_data_1, base_dir, ms_id, "raw", update=True)
        new_file_to_archive(raw_data_2, base_dir, ms_id, "raw", update=True)
        if raw_data_3.exists():
            new_file_to_archive(raw_data_3, base_dir, ms_id, "raw", update=True)

    else:
        raise ValueError(f"Data type: {fmt} unknown!")

    return


def detect_supported_format(folder: Path):
    """
    Extract the format of a set of files from the suffixes of these files.

    Parameters
    ----------
    folder : Path
        Folder with the files to check for the format.

    Returns
    -------
    format_name : str
        Format string (from SUPPORTED_FORMATS). If the group of suffixes does
        not match a suppuroted format None is returned.

    """
    suffixes = {f.suffix.lower() for f in folder.iterdir() if f.is_file()}

    for format_name, required_suffixes in SUPPORTED_FORMATS.items():
        # All necessary suffixes need to be in the folder
        if required_suffixes.issubset(suffixes):
            return format_name

    return None


def raw_data_to_hdf5(base_dir: str, ms_id: str):
    """
    Write the data from the raw data datafiles in the archive at
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
    path = measurement_path(base_dir, ms_id)
    raw_path = path/"raw"
    hdf5_path = path / f"measurement_M{ms_id}.h5"
    fmt = detect_supported_format(raw_path)

    if fmt == None:
        raise ValueError("Fileformat not known.")

    # load and save data from Bruker bes3t format
    elif fmt == "bruker_bes3t":
        dsc = [p for p in raw_path.iterdir() if p.suffix == ".DSC"]
        dta = [p for p in raw_path.iterdir() if p.suffix == ".DTA"]

        if not dsc or not dta:
            raise ValueError("Exactly one .DSC and one .DTA file have to be\
                             available")
        if dsc[0].stem != dta[0].stem:
            raise ValueError("The DSC and the DTA files need to have equal\
                             basenames.")

        # load data to arrays using the loader function
        data, x, params = load(dsc[0].with_suffix(""), "DSC", "n")

        # write intensities to dataset
        new_dataset_to_hdf5(data, hdf5_path, "raw_data", "data")
        new_dataset_to_hdf5(data.real, hdf5_path, "raw_data", "data_real")
        new_dataset_to_hdf5(data.imag, hdf5_path, "raw_data", "data_imag")

        # write axes-data
        if type(x) == list:  # multiple axes
            for n in range(len(x)):
                new_dataset_to_hdf5(x[n], hdf5_path, "raw_data", f"axis_{n}")
        else:  # only one xaxis
            new_dataset_to_hdf5(x, hdf5_path, "raw_data", "xaxis")

        # add metadata from DSC-file as attributes
        with h5py.File(hdf5_path, "a") as f:
            grp = f.require_group("raw_data")
            for key, value in params.items():
                grp.attrs[key] = value

    return


def delete_element(base_dir: str, ms_id: int, category: str, filename: str,
                   save_delete: bool=True):
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
        raise ValueError(f"'{category}' is not valid. Allowed values are: \
                         {CATEGORIES}")

    path = measurement_path(base_dir, ms_id)
    file_path = path / category / filename

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")
        return False

    if save_delete:
        confirm = input(f"Delete file? {file_path} (y/N): ")
        if confirm.lower() != "y":
            print("Deletion cancelled")
            return

    file_path.unlink()
    print(f"Deleted: {file_path}")

    return

def delete_measurement(base_dir: str, ms_id: int, save_delete: bool=True):
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
    path = measurement_path(base_dir, ms_id)
    if not path.exists():
        raise FileNotFoundError(f"Measurement does not exist: {path}")
        return

    if save_delete:
        confirm = input(f"Delete WHOLE measurement directory? {path} (y/N): ")
        if confirm.lower() != "y":
            print("Deletion cancelled")
            return

    shutil.rmtree(path)
    print(f"Measurement directory deleted: {path}")
    return


def list_files(base_dir: str, ms_id: str, category: str="") -> list:
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
            raise ValueError(f"'{category}' no valid category.\
                             Allowed values are: {CATEGORIES}")

    path = measurement_path(base_dir, ms_id)
    folder = path / category

    if not folder.exists():  # return empty list
        return []

    files = list(folder.rglob("*"))
    filelist = [f for f in files if f.is_file()]  # return only files

    return filelist

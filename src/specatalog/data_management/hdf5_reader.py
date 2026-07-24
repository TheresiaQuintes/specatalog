import h5py
from specatalog.crud_db import read as r
from typing import Any, Literal
import numpy as np
from contextlib import contextmanager
from specatalog.main import archive


class H5Object:
    """
    Represents a hdf5-file with its internal structure and all attributes/
    datasets as a python object.

    Overview of the methods
    -----------------------
    Using the set_attr()- / set_dataset()-method new data can be added to the
    object or existing data are updated. Using the delete_attr()- /
    delete_dataset()- method data can be deleted. After all changes are done
    they are wirtten to the hdf5-file using the sync()-method.

    Parameters
    ----------
    h5node : h5py.File
        The object is build from the contents of the hdf5-file.
    writable : bool, optional
        The original hdf5-file is only changable if writable=True otherwise
        changes can be only done to the object but not to the file itself.
        The default is False.
    auto_flush : bool, optional
        If set to True changes are directly written to the filesystem using
        the sync()-method. If set to False the "synced"-changes are only
        written to the file when it is closed manually using f.close().
        The default is True.

    Attributes
    ----------
    The attributes of the object are set recursive as the groups of the hdf5-
    file and the attributes and datasets as stored.


    Example
    -------
    >>> # data are stored in the hdf5-file (f) in /data/raw_data/spec
    >>> dat = H5Object(f, writable=True)
    >>> x = dat.raw_data.xaxis
    >>> intensity = dat.raw_data.spec
    >>> fit = -2*(x-12000)**2 + 25000
    >>> dat.evaluations.set_dataset("fit1", fit)
    >>> dat.sync()

    """

    def __init__(
        self, h5node: h5py.File, writable: bool = False, auto_flush: bool = True
    ):
        self._node = h5node
        self._writable = writable

        # track all attributes and datasets
        self._attrs_keys = set()
        self._datasets_keys = set()
        self._attrs_to_delete = set()
        self._datasets_to_delete = set()

        self._auto_flush = auto_flush

        # load groups and datasets recursively
        for key, item in h5node.items():
            if isinstance(item, h5py.Group):
                setattr(self, key, H5Object(item, writable=writable))
            else:
                setattr(self, key, item[()])  # Dataset laden
                self._datasets_keys.add(key)

        # load attributes of the groups
        for key, value in h5node.attrs.items():
            setattr(self, key, value)
            self._attrs_keys.add(key)

    def set_attr(self, key: str, value: Any):
        """
        Set a new attribute or update an exising attribute of the H5Object.

        Parameters
        ----------
        key : str
            Name of the attribute.
        value : Any
            The value of the attribute. Should be a number or a string, for
            arrays use set_dataset.

        Example
        -------
        >>> dat = H5Object(f, writable=True)
        >>> dat.set_attr("name", "dataset name") # set to main file
        >>> dat.raw_data.set_attr("measurement_temperature", 80) # set to group
        >>> dat.sync()

        Returns
        -------
        None.

        """
        setattr(self, key, value)
        self._attrs_keys.add(key)
        if key in self._datasets_keys:
            self._datasets_keys.remove(key)

    def set_dataset(self, key: str, value: np.ndarray):
        """
        Set a new dataset or update an exising dataset of the H5Object.

        Parameters
        ----------
        key : str
            Name of the dataset.
        value : np.ndarray
            Array that contains the data. Should be an array of numbers.

        Example
        -------
        >>> dat = H5Object(f, writable=True)
        >>> corrected_data = dat.raw_data.spec - 10
        >>> dat.corrected_data.set_dataset("minus_10", corrected_data)
        >>> dat.sync()

        Returns
        -------
        None.

        """
        setattr(self, key, value)
        self._datasets_keys.add(key)
        if key in self._attrs_keys:
            self._attrs_keys.remove(key)

    def delete_attr(self, key: str):
        """
        Delete an attribute from the object and mark it to be deleted from the
        hdf5-file at the next call of the sync()-method.

        Parameters
        ----------
        key : str
            Name of the attribute.

        Returns
        -------
        None.

        """
        self._attrs_to_delete.add(key)
        self._attrs_keys.discard(key)
        if hasattr(self, key):
            delattr(self, key)

    def delete_dataset(self, key: str):
        """
        Delete a dataset from the object and mark it to be deleted from the
        hdf5-file at the next call of the sync()-method.

        Parameters
        ----------
        key : str
            Name of the dataset.

        Returns
        -------
        None.

        """
        self._datasets_to_delete.add(key)
        self._datasets_keys.discard(key)
        if hasattr(self, key):
            delattr(self, key)

    def sync(self):
        """
        Write the changes that were done to the H5Object to the corresponding
        h5-file.

        Raises
        ------
        RuntimeError
            An error is raised if the object was generated with the option
            writable=False.

        Returns
        -------
        None.

        """
        if not self._writable:
            raise RuntimeError("Object is not writable.")

        # delete attributes
        for key in self._attrs_to_delete:
            if key in self._node.attrs:
                del self._node.attrs[key]
        self._attrs_to_delete.clear()

        # delete datasets
        for key in self._datasets_to_delete:
            if key in self._node:
                del self._node[key]
        self._datasets_to_delete.clear()

        # update attributes
        for key in self._attrs_keys:
            value = getattr(self, key)
            if key in self._node.attrs:
                del self._node.attrs[key]
            self._node.attrs[key] = value

        # update datasets
        for key in self._datasets_keys:
            value = getattr(self, key)

            if key in self._node:
                del self._node[key]
            self._node.create_dataset(key, data=value)

        # sync recursively for all groups
        for key, value in self.__dict__.items():
            if isinstance(value, H5Object):
                value.sync()

        # optional: flush data to file
        if self._auto_flush:
            self._node.file.flush()


@contextmanager
def load_h5(
    filename: str, mode: Literal["r", "a", "w"] = "r"
) -> tuple[H5Object, h5py.File]:
    """
    Loads an HDF5 file and returns it as an H5Object along with the underlying h5py.File.

    Parameters
    ----------
    filename : str
        Path to the HDF5 file.
    mode : Literal["r", "a", "w"], optional
        File access mode:
        - "r": Read-only (default)
        - "a": Append to existing file
        - "w": Overwrite existing file

    Yields
    ------
    tuple[H5Object, h5py.File]
        The H5Object wrapper and the raw h5py.File object.
    """
    with archive.open_measurement_h5_file(filename, mode=mode) as f:
        obj = H5Object(f, writable=(mode != "r"))
        yield obj, f


@contextmanager
def load_from_id(
    ms_id: int, mode: Literal["r", "a"] = "r"
) -> tuple[H5Object, h5py.File]:
    """
    Load a hdf5-measurement-file from the archive as a H5Object.

    Parameters
    ----------
    ms_id : int
        Number of the measurement.
    mode : Literal["r", "a", "w"], optional
        File access mode:
        - "r": Read-only (default)
        - "a": Append to existing file
        - "w": Overwrite existing file

    Raises
    ------
    ValueError
        If no measurement with the given ID exists in the archive.

    Yields
    ------
    tuple[H5Object, h5py.File]
        The H5Object wrapper and the raw h5py.File object.

    Example
    -------
    >>> with load_from_id(222, mode="a") as (obj, f):
    >>>    obj.corrected_data.set_attr("test2", 1234)
    >>>    obj.sync()
    >>>    int = obj.raw_data.intensity_0
    >>> print(int)
    """
    find_measurement = r.MeasurementFilter(id=ms_id)
    m = r.run_query(find_measurement)
    if len(m) == 0:
        raise ValueError(f"No measurement with the id={ms_id} found.")

    with load_h5(
        archive.measurement_path(ms_id) / f"measurement_M{ms_id}.h5", mode=mode
    ) as (obj, f):
        yield obj, f

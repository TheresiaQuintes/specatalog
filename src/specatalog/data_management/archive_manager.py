from typing import Union, Iterator
from smbclient import register_session, delete_session
from pathlib import Path
import os
import smbclient as smb
from contextlib import contextmanager
import h5py
import tempfile
import smbclient.shutil as smb_shutil
import shutil
from specatalog.config import HOST, USERNAME, SHARE, PWD
import hashlib
import json
from uuid import uuid4
import smbclient


class SMBConnectionManager:
    """Manages SMB network connections for the archive."""

    def __init__(self) -> None:
        """Initialize the SMB connection manager with configuration."""
        self.host = HOST
        self.username = USERNAME
        self.password = PWD
        self.share = SHARE
        self.connection = None

    def connect(self) -> None:
        """Establish connection to the SMB server."""
        self.connection = register_session(
            self.host, username=self.username, password=self.password
        )

    def disconnect(self) -> None:
        """Close the SMB connection."""
        delete_session(self.host)

    def ensure_connection(self) -> None:
        """Ensure an active connection exists, connecting if needed."""
        if self.connection is None:
            self.connect()

    def reconnect(self) -> None:
        """Re-establish the SMB connection."""
        self.disconnect()
        self.connect()

    def remote_path(self) -> Path:
        """Get the remote base path for the archive.

        Returns
        -------
        Path
            The remote base path
        """
        return Path(f"{self.host}/{self.share}")


def create_archive(use_remote_archive: bool, local_path: str = "") -> Path:
    """Create and return an archive path.

    Parameters
    ----------
    use_remote_archive : bool
        Whether to use remote SMB archive
    local_path : str, optional
        Local path if not using remote archive

    Returns
    -------
    Path
        Path to the archive
    """
    if use_remote_archive:
        connection = SMBConnectionManager()
        connection.connect()
        return connection.remote_path()
    else:
        archive = Path(local_path)
        return archive


class SpecatalogArchive:
    """Handles file operations for the measurement archive. All file operations
    run relative to the archive root (self.archive)."""

    def __init__(self, use_remote_archive: bool, local_path: str = "") -> None:
        """Initialize the archive handler.

        Parameters
        ----------
        use_remote_archive : bool
            Whether to use remote SMB archive
        local_path : str, optional
            Local path if not using remote archive
        """
        self.archive = create_archive(use_remote_archive, local_path)
        self.use_remote_archive = use_remote_archive

    def path_to_unc(self, p: Union[str, Path]) -> str:
        """Convert local path to UNC path format.

        Parameters
        ----------
        p : Union[str, Path]
            Local path to convert

        Returns
        -------
        str
            UNC path string
        """
        path = self.archive / p
        parts = path.parts
        s = "\\".join(parts)
        return rf"\\{s}"

    def list_files(self, p: Union[str, Path]) -> list[str]:
        """List files in a directory.

        Parameters
        ----------
        p : Union[str, Path]
            Directory path

        Returns
        -------
        list[str]
            List of filenames
        """
        if self.use_remote_archive:
            return smb.listdir(self.path_to_unc(p))
        else:
            return os.listdir(self.archive / p)

    def exists(self, p: Union[str, Path]) -> bool:
        """Check if path exists.

        Parameters
        ----------
        p : Union[str, Path]
            Path to check

        Returns
        -------
        bool
            True if path exists
        """
        if self.use_remote_archive:
            return smb.path.exists(self.path_to_unc(p))
        else:
            return (self.archive / p).exists()

    def make_dir(self, p: Union[str, Path]) -> None:
        """Create directory.

        Parameters
        ----------
        p : Union[str, Path]
            Directory path to create
        """
        if self.use_remote_archive:
            smb.makedirs(self.path_to_unc(p), exist_ok=True)
        else:
            (self.archive / p).mkdir(parents=True, exist_ok=True)

    def copy_to_archive(self, src: Union[str, Path], dst_p: Union[str, Path]) -> None:
        """Copy file to archive.

        Parameters
        ----------
        src : Union[str, Path]
            Source file path
        dst_p : Union[str, Path]
            Destination path in archive
        """
        if self.use_remote_archive:
            dst = self.path_to_unc(dst_p)
            smb_shutil.copy2(str(src), dst)
        else:
            shutil.copy2(src, self.archive / dst_p)

    def delete_file(self, p: Union[str, Path]) -> None:
        """Delete file from archive.

        Parameters
        ----------
        p : Union[str, Path]
            Path of file to delete
        """
        if self.use_remote_archive:
            smb.unlink(self.path_to_unc(p))
        else:
            (self.archive / p).unlink()

    def delete_folder(self, p: Union[str, Path]) -> None:
        """Delete directory from archive.

        Parameters
        ----------
        p : Union[str, Path]
            Path of directory to delete
        """
        if self.use_remote_archive:
            smb_shutil.rmtree(self.path_to_unc(p))
        else:
            shutil.rmtree(self.archive / p)

    @contextmanager
    def open_file(self, p: Union[str, Path], mode: str = "r", encoding: str = "utf-8"):
        """Context manager for opening files.

        Parameters
        ----------
        p : Union[str, Path]
            Path of file to open
        mode : str, optional
            File opening mode
        encoding : str, optional
            File encoding

        Yields
        ------
        file
            Open file object
        """
        if self.use_remote_archive:
            remote_path = self.path_to_unc(p)
            with smb.open_file(remote_path, mode=mode, encoding=encoding) as file:
                yield file
        else:
            print(self.archive / p)
            with open(self.archive / p, mode=mode, encoding=encoding) as file:
                yield file

    @contextmanager
    def temporary_path(self, p: Union[str, Path]):
        """Context manager for temporary local copies.

        Parameters
        ----------
        p : Union[str, Path]
            Path of remote file/directory

        Yields
        ------
        Path
            Path to local temporary copy
        """
        if self.use_remote_archive:
            with tempfile.TemporaryDirectory() as tmpdir:
                local_path = Path(tmpdir) / Path(p).name

                remote_path = self.path_to_unc(p)

                if smb.path.isdir(remote_path):
                    smb_shutil.copytree(
                        remote_path,
                        str(local_path),
                    )

                elif smb.path.isfile(remote_path):
                    smb_shutil.copy2(
                        remote_path,
                        str(local_path),
                    )

                else:
                    raise FileNotFoundError(
                        f"Remote path does not exist: {remote_path}"
                    )

                yield local_path
        else:
            local_path = self.archive / p
            yield local_path

    def measurement_path(self, ms_id: Union[str, int]) -> Path:
        """Get measurement directory path 'data/M{ms_id}'.

        Parameters
        ----------
        ms_id : Union[str, int]
            Measurement ID

        Returns
        -------
        Path
            Path to measurement directory

        Raises
        ------
        FileNotFoundError
            If measurement directory doesn't exist
        """
        p = rf"data/M{ms_id}"

        if not self.exists(p):
            raise FileNotFoundError(
                f"Measurement folder {self.archive / p} does not exist!"
            )

        else:
            return Path(p)

    def copy_directory_to_archive(
        self, src: Union[str, Path], dst_p: Union[str, Path]
    ) -> None:
        """Copy directory to archive.

        Parameters
        ----------
        src : Union[str, Path]
            Source directory path
        dst_p : Union[str, Path]
            Destination path in archive
        """
        src = Path(src)

        if self.use_remote_archive:
            dst = self.path_to_unc(dst_p)

            smb_shutil.copytree(
                str(src),
                dst,
                dirs_exist_ok=False,
            )

        else:
            dst = self.archive / dst_p

            shutil.copytree(
                src,
                dst,
                dirs_exist_ok=False,
            )

    @contextmanager
    def open_measurement_h5_file(
        self,
        p: str | Path,
        mode: str,
    ) -> Iterator[h5py.File]:
        """Open an HDF5 measurement file, optionally using a local cache.

        For remote archives, the file is downloaded to a local cache before
        opening. Writable changes are uploaded atomically when the context
        exits successfully. Concurrent remote modifications are detected and
        prevent the upload.

        Parameters
        ----------
        p : str | Path
            Path to the measurement file relative to the archive root.
        mode : str
            HDF5 file access mode.

        Yields
        ------
        h5py.File
            The opened HDF5 file.
        """
        if not self.use_remote_archive:
            with h5py.File(self.archive / p, mode=mode) as file:
                yield file
            return

        remote_path = self.path_to_unc(p)
        local_path, metadata_path = _cache_paths(remote_path)

        writable = mode in {"a", "r+", "w", "w-", "x"}

        # With "w", no existing file is required.
        if mode == "w":
            remote_metadata = None
        else:
            if not self.exists(p):
                raise FileNotFoundError(remote_path)

            remote_metadata = _remote_metadata(remote_path)
            cached_metadata = _read_metadata(metadata_path)

            cache_is_valid = local_path.exists() and cached_metadata == remote_metadata

            if not cache_is_valid:
                temporary = local_path.with_suffix(".download")

                if temporary.exists():
                    temporary.unlink()

                smb_shutil.copy2(str(remote_path), str(temporary))
                os.replace(temporary, local_path)

                _write_metadata(metadata_path, remote_metadata)

        # Remember the previous local metadata
        local_stat_before = None
        if local_path.exists():
            stat = local_path.stat()
            local_stat_before = (stat.st_size, stat.st_mtime_ns)

        successful = False

        try:
            with h5py.File(local_path, mode=mode) as file:
                yield file

            successful = True

        finally:
            if successful and writable:
                stat = local_path.stat()

                local_stat_after = (stat.st_size, stat.st_mtime_ns)

                local_file_changed = (
                    mode in {"w", "w-", "x"} or local_stat_before != local_stat_after
                )

                if not local_file_changed:
                    return

                # Check whether the remote file was modified during editing.
                if remote_metadata is not None:
                    current_remote_metadata = _remote_metadata(remote_path)

                    if current_remote_metadata != remote_metadata:
                        raise RuntimeError(
                            "Die Remote-Datei wurde während der Bearbeitung "
                            "von einem anderen Prozess geändert. "
                            "Der Upload wurde abgebrochen."
                        )

                # Upload the complete file under a temporary name and then
                # replace the destination atomically.
                atomic_upload(
                    local_path=local_path,
                    remote_path=remote_path,
                )

                # Read the metadata of the updated remote file.

                new_metadata = _remote_metadata(remote_path)

                # Update the cache metadata.

                _write_metadata(
                    metadata_path,
                    new_metadata,
                )


def _cache_paths(remote_path: str) -> tuple[Path, Path]:
    """Return local cache and metadata paths for a remote file.

    Parameters
    ----------
    remote_path : str
        Remote SMB path used to derive the cache key.

    Returns
    -------
    tuple[Path, Path]
        The local HDF5 cache path and its metadata path.
    """
    cache_dir = Path.home() / ".cache" / "specatalog" / "hdf5"
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = hashlib.sha256(remote_path.encode()).hexdigest()

    local_path = cache_dir / f"{key}.h5"
    metadata_path = cache_dir / f"{key}.json"

    return local_path, metadata_path


def _remote_metadata(path: str) -> dict:
    """Retrieve metadata for a remote file.

    Parameters
    ----------
    path : str
        Remote SMB file path.

    Returns
    -------
    dict
        A dictionary containing the file size and modification timestamp.
    """
    stat = smbclient.stat(path)

    return {
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _read_metadata(path: Path) -> dict | None:
    """Read cached metadata from a local JSON file.

    Parameters
    ----------
    path : Path
        Path to the metadata file.

    Returns
    -------
    dict | None
        The parsed metadata, or ``None`` if the file is missing or invalid.
    """
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _write_metadata(path: Path, metadata: dict) -> None:
    """Write metadata atomically to a local JSON file.

    Parameters
    ----------
    path : Path
        Destination path for the metadata file.
    metadata : dict
        Metadata to serialize as JSON.
    """
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(metadata))
    os.replace(temporary, path)


def make_remote_tmp_path(remote_path: str) -> str:
    """Create a unique temporary path next to a remote SMB file.

    Parameters
    ----------
    remote_path : str
        UNC path of the target remote file.

    Returns
    -------
    str
        A unique temporary path in the same remote directory.

    Raises
    ------
    ValueError
        If ``remote_path`` is not a valid SMB path containing a separator.
    """
    parent, separator, name = remote_path.rpartition("\\")

    if not separator:
        raise ValueError(f"Ungültiger SMB-Pfad: {remote_path!r}")

    return f"{parent}\\.{name}.{uuid4().hex}.uploading"


def atomic_upload(local_path: Path, remote_path: Path) -> None:
    """Upload a local file to an SMB path using an atomic replacement.

    The file is first uploaded under a unique temporary name and then
    replaced onto the target path. The temporary file is removed if the
    operation fails.

    Parameters
    ----------
    local_path : Path
        Path to the local source file.
    remote_path : Path
        UNC path of the remote destination file.
    """
    temporary_remote_path = make_remote_tmp_path(remote_path)

    try:
        # Upload tmp-name
        smb_shutil.copy2(
            str(local_path),
            str(temporary_remote_path),
        )

        # change name after upload
        smbclient.replace(
            str(temporary_remote_path),
            str(remote_path),
        )

    except Exception:
        try:
            if smbclient.path.exists(str(temporary_remote_path)):
                smbclient.remove(str(temporary_remote_path))
        except Exception:
            pass

        raise

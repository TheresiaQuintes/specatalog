from smbclient import register_session, listdir, delete_session
from pathlib import Path
import os
import smbclient as smb
from contextlib import contextmanager
import h5py
import tempfile
import smbclient.shutil as smb_shutil
import shutil
from specatalog.config import HOST, USERNAME, SHARE, PWD


class SMBConnectionManager:
    def __init__(self):
        self.host = HOST
        self.username = USERNAME
        self.password = PWD
        self.share = SHARE
        self.connection = None

    def connect(self):
        self.connection = register_session(self.host, username=self.username, password=self.password)

    def disconnect(self):
        delete_session(self.host)

    def ensure_connection(self):
        if self.connection is None:
            self.connect()

    def reconnect(self):
        self.disconnect()
        self.connect()

    def remote_path(self):
        return Path(f"{self.host}/{self.share}")

def create_archive(use_remote_archive:bool, local_path=""):
    if use_remote_archive:
        connection = SMBConnectionManager()
        connection.connect()
        return connection.remote_path()
    else:
        archive = Path(local_path)
        return archive

class SpecatalogArchive:
    def __init__(self, use_remote_archive: bool, local_path=""):
        self.archive = create_archive(use_remote_archive, local_path)
        self.use_remote_archive = use_remote_archive

    def path_to_unc(self, p):
        path = self.archive / p
        parts = path.parts
        s = "\\".join(parts)
        return rf"\\{s}"

    def list_files(self, p):
        if self.use_remote_archive:
            return smb.listdir(self.path_to_unc(p))
        else:
            return os.listdir(self.archive / p)

    def exists(self, p):
        if self.use_remote_archive:
            return smb.path.exists(self.path_to_unc(p))
        else:
            return (self.archive / p).exists()

    def make_dir(self, p):
        if self.use_remote_archive:
            smb.makedirs(self.path_to_unc(p), exist_ok=True)
        else:
            (self.archive / p).mkdir(parents=True, exist_ok=True)

    def copy_to_archive(self, src, dst_p):
        if self.use_remote_archive:
            dst = self.path_to_unc(dst_p)
            smb_shutil.copy2(str(src), dst)
        else:
            shutil.copy2(src, self.archive / dst_p)

    def delete_file(self, p):
        if self.use_remote_archive:
            smb.unlink(self.path_to_unc(p))
        else:
            (self.archive / p).unlink()

    def delete_folder(self, p):
        if self.use_remote_archive:
            smb_shutil.rmtree(self.path_to_unc(p))
        else:
            shutil.rmtree(self.archive / p)

    @contextmanager
    def open_file(self, p, mode="r", encoding="utf-8"):
        if self.use_remote_archive:
            remote_path = self.path_to_unc(p)
            with smb.open_file(remote_path, mode=mode, encoding=encoding) as file:
                yield file
        else:
            print(self.archive /p )
            with open(self.archive / p, mode=mode, encoding=encoding) as file:
                yield file

    @contextmanager
    def open_measurement_h5_file(self, p, mode):
        if self.use_remote_archive:
            with tempfile.TemporaryDirectory() as tmpdir:
                remote_path = self.path_to_unc(p)
                local_path = Path(tmpdir) / p
                local_path.parent.mkdir(parents=True, exist_ok=True)

                if self.exists(p):
                    smb_shutil.copy2(str(remote_path), str(local_path))

                with h5py.File(local_path, mode=mode) as file:
                    yield file

                smb_shutil.copy2(str(local_path), remote_path)

        else:
            with h5py.File(self.archive / p, mode=mode) as file:
                yield file

    @contextmanager
    def temporary_path(self, p):
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
            
    def measurement_path(self, ms_id):
        p =  fr"data/M{ms_id}"

        if not self.exists(p):
            raise FileNotFoundError(f"Measurement folder {self.archive/p} does not exist!")

        else:
            return Path(p)

    def copy_directory_to_archive(self, src, dst_p):
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
    

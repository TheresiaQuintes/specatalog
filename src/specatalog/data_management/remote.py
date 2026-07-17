from smbclient import register_session, listdir, delete_session
from specatalog.main import BASE_PATH
from pathlib import Path
import os
import smbclient as smb
from contextlib import contextmanager
import h5py
import tempfile
import smbclient.shutil as smb_shutil
import shutil
from specatalog.main import HOST, USERNAME, SHARE, PWD


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

def create_archive(use_remote_archive:bool):
    if use_remote_archive:
        connection = SMBConnectionManager()
        connection.connect()
        return connection.remote_path()
    else:
        archive = Path(BASE_PATH)
        return archive

class SpecatalogContext:
    def __init__(self, use_remote_archive: bool):
        self.archive = create_archive(use_remote_archive)
        self.use_remote_archive = use_remote_archive
        # self.database = create_database()

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
            # raises SMBOSError if path exists
            smb.makedirs(self.path_to_unc(p), exist_ok=False)
        else:
            # raises FileExistsError if path exists
            (self.archive / p).mkdir(parents=True, exist_ok=False)

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
        print("ah")
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
                local_path = Path(tmpdir) / p
                local_path.parent.mkdir(parents=True, exist_ok=True)
                if self.exists(p):
                    smb_shutil.copy2(self.path_to_unc(p), str(local_path))
                yield local_path
        else:
            local_path = self.archive / p
            yield local_path
            
    def measurement_path(self, ms_id):
        p =  fr"data/M{ms_id}"

        if not self.exists(p):
            raise FileNotFoundError(f"Measurement folder {self.archive/p} does not exist!")

        else:
            return self.archive / p

    def data_loader(self):
        pass



test_remote = SpecatalogContext(True)

test_local = SpecatalogContext(False)

print(test_remote.list_files(Path("data")))
print(test_local.list_files(Path("data")))
print(test_remote.list_files(Path("data/M45")))

print(test_remote.exists("data/M45"))
print(test_local.exists("data/M45"))
print(test_remote.exists("data/M46"))
print(test_local.exists("data/M46"))

#test_remote.make_dir("data/test1")
#test_local.make_dir("data/test2")
#test_local.make_dir("data/test3/test4")
#test_remote.make_dir("data/test4/test5")

#with test_local.open_measurement_h5_file("data/test2/ms.h5", "a") as f:
#    f.create_group("raw_data")

#with test_remote.open_measurement_h5_file("data/test3/test4/ms1.h5", mode="w") as file:
#    file.create_group("raw_data1")
#    file.create_group("raw_data2")

#with test_remote.open_measurement_h5_file("data/test3/test4/ms1.h5", mode="a") as file:
#    file.create_group("raw_data3")

#a = test_remote.measurement_path(4)
#print(a)

#test_remote.copy_to_archive("/home/quintes/Dokumente/j_nn/model.py", "data/test4/test5")
#test_local.copy_to_archive("/home/quintes/Dokumente/j_nn/model.py", "data/test1")
#test_local.delete_file("data/test1/model.py")
#test_remote.delete_file("data/test4/test5/model.py")

#test_local.delete_folder("data/test2")
#test_remote.delete_folder("data/test3")

#with test_local.temporary_path("data/M4/raw/02_cPDIc-TEMPO_1-15_tol_0p1mMPDI_1mm.txt") as path:
#    with open(path) as f:
#        for line in f:
#            print(line)
#    print(path)

#with test_remote.temporary_path("data/M4/raw/02_cPDIc-TEMPO_1-15_tol_0p1mMPDI_1mm.txt") as path:
#    with open(path) as f:
#        for line in f:
#            print(line)
#    print(path)
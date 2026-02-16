from getpass import getpass
from pathlib import Path
import json
import platform
import subprocess
from typing import Literal, Dict

def print_welcome():
    from specatalog.main import BASE_PATH
    print(f"""
          Welcome to specatalog! \n
          Your archive directory can be found at: \n
          {BASE_PATH}\n
          Have fun!
          """)

def configure_db():
    user = input("Choose a username: ")
    pw = getpass("Choose a password: ")
    basepath = Path(input("Choose an absolute path for your archive base: "))
    database_url = input("Enter URL for the database (e.g.localhost:5432/specatalog: " or "localhost:5432/specatalog")
    home_defaults = Path.home() / ".specatalog" / "defaults.json"
    with home_defaults.open("r") as f:
        cfg = json.load(f)
    cfg["usr_name"] = user
    cfg["password"] = pw
    cfg["base_path"] = str(basepath)
    cfg["database_url"] = str(database_url)

    f.close()

    with home_defaults.open("w") as f:
        json.dump(cfg, f, indent=2)

    f.close()



def sync_smb(
    local_path: str,
    mount_point: str,
    direction: Literal["upload", "download"],
) -> Dict:
    """
    Temporarily mounts SMB share, performs dry-run sync, then real sync,
    and unmounts again.
    """

    system = platform.system()
    local = Path(local_path).expanduser().resolve()

    print(system)

    result = {
        "success": False,
        "stage": None,
        "log": "",
        "error": "",
    }

    try:
        if system == "Windows":
            print("Windows")
            """
            # -------------------------
            # WINDOWS
            # -------------------------
            drive_letter = "Z:"

            # 1️⃣ Mount
            result["stage"] = "mount"
            mount_cmd = [
                "net", "use", drive_letter,
                remote_url,
                f"/user:{remote_user}",
                remote_password
            ]
            mount = subprocess.run(mount_cmd, capture_output=True, text=True)
            if mount.returncode != 0:
                result["error"] = mount.stderr
                return result

            remote_path = Path(drive_letter)

            # Determine source and target
            if direction == "download":
                src = str(remote_path)
                dst = str(local)
            else:
                src = str(local)
                dst = str(remote_path)

            # 2️⃣ Dry-run
            result["stage"] = "dry-run"
            dry_cmd = ["robocopy", src, dst, "/MIR", "/L"]
            dry = subprocess.run(dry_cmd, capture_output=True, text=True)

            if dry.returncode >= 8:
                result["error"] = dry.stderr
                return result

            result["log"] += dry.stdout

            # 3️⃣ Real sync
            result["stage"] = "sync"
            real_cmd = ["robocopy", src, dst, "/MIR"]
            real = subprocess.run(real_cmd, capture_output=True, text=True)

            result["log"] += real.stdout

            if real.returncode >= 8:
                result["error"] = real.stderr
                return result

            # 4️⃣ Unmount
            result["stage"] = "unmount"
            subprocess.run(["net", "use", drive_letter, "/delete", "/y"])
            """
        else:
            # -------------------------
            # LINUX / MAC
            # -------------------------

            # 1️⃣ Mount
            result["stage"] = "mount"
            mount_cmd = [
                "mount",
                str(mount_point)]


            mount = subprocess.run(mount_cmd, capture_output=True, text=True)

            if mount.returncode != 0:
                result["error"] = mount.stderr
                return result


            if direction == "download":
                src = str(mount_point) + "/"
                dst = str(local)
            else:
                src = str(local) + "/"
                dst = str(mount_point)

            # 2️⃣ Dry-run
            result["stage"] = "dry-run"
            dry_cmd = [
                "rsync", "-rtv",
                "--delete",
                "--no-perms",
                "--no-owner",
                "--no-group",
                "--modify-window=1",
                "--dry-run",
                src, dst
            ]
            dry = subprocess.run(dry_cmd, capture_output=True, text=True)

            if dry.returncode != 0:
                result["error"] = dry.stderr
                subprocess.run(["umount", str(mount_point)])
                return result

            result["log"] += dry.stdout


            # 3️⃣ Real sync
            result["stage"] = "sync"
            real_cmd = [
                "rsync", "-rtv",
                "--delete",
                "--no-perms",
                "--no-owner",
                "--no-group",
                "--modify-window=1",
                src, dst
            ]
            real = subprocess.run(real_cmd, capture_output=True, text=True)

            result["log"] += real.stdout

            if real.returncode != 0:
                result["error"] = real.stderr
                subprocess.run(["umount", str(mount_point)])
                return result

            # 4️⃣ Unmount
            result["stage"] = "unmount"
            subprocess.run(["umount", str(mount_point)])


        result["success"] = True
        return result

    except Exception as e:
        result["error"] = str(e)
        if result["stage"] == "sync" or result["stage"] == "dry-run":
            subprocess.run(["umount", str(mount_point)])
        return result

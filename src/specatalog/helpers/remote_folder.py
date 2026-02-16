import platform
import subprocess
from typing import Literal, Dict
from pathlib import Path
import json

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

    result = {
        "success": False,
        "stage": None,
        "log": "",
        "error": "",
    }

    try:
        if system == "Windows":

            # -------------------------
            # WINDOWS
            # -------------------------
            drive_letter = "P:"

            # Mount
            result["stage"] = "mount"
            mount_cmd = [
                "net", "use", drive_letter,
                 mount_point,
                "/persistent:no"
            ]

            mount = subprocess.run(mount_cmd, capture_output=True)

            if mount.returncode != 0:
                result["error"] = mount.stderr
                return result



            if direction == "download":
                src = drive_letter
                dst = local
            elif direction == "upload":
                src = local
                dst = drive_letter

            # Dry-run
            result["stage"] = "dry-run"
            dry_cmd = ["robocopy", src, dst, "/MIR", "/L"]
            dry = subprocess.run(dry_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if dry.returncode >= 8:
                result["error"] = dry.stderr.decode("cp850", errors="replace")
                subprocess.run(["net", "use", drive_letter, "/delete", "/y"])

                return result

            result["log"] += dry.stdout.decode("cp850", errors="replace")

            # Real sync
            result["stage"] = "sync"
            real_cmd = ["robocopy", src, dst, "/MIR"]
            real = subprocess.run(real_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if real.returncode >= 8:
                result["error"] = real.stderr.decode("cp850", errors="replace")
                subprocess.run(["net", "use", drive_letter, "/delete", "/y"])

                return result

            result["log"] += real.stdout.decode("cp850", errors="replace")

            # Unmount
            result["stage"] = "unmount"
            subprocess.run(["net", "use", drive_letter, "/delete", "/y"])

        else:
            # -------------------------
            # LINUX / MAC
            # -------------------------

            # Mount
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
            elif direction == "upload":
                src = str(local) + "/"
                dst = str(mount_point)

            # Dry-run
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


            # Real sync
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

            # Unmount
            result["stage"] = "unmount"
            subprocess.run(["umount", str(mount_point)])


        result["success"] = True
        return result

    except Exception as e:
        result["error"] = str(e)
        if result["stage"] == "sync" or result["stage"] == "dry-run":
            if system == "Windows":
                subprocess.run(["net", "use", drive_letter, "/delete", "/y"])
            else:
                subprocess.run(["umount", str(mount_point)])
        return result


def cli_upload():
    home_defaults = Path.home() / ".specatalog" / "defaults.json"
    with home_defaults.open("r") as f:
        defaults = json.load(f)
    f.close()

    local = Path(defaults["base_path"]).resolve()
    remote = defaults["mount_point"]

    confirm = input(
        f"Are you sure you want to synchronise\n"
        f"  FROM: {local}\n"
        f"  TO:   {remote} (= remote folder)\n"
        f"[y/N]: "
    )

    if confirm.lower() != "y":
        print("Upload cancelled.")
        return

    result = sync_smb(local, remote, "upload")

    return result


def cli_download():
    home_defaults = Path.home() / ".specatalog" / "defaults.json"
    with home_defaults.open("r") as f:
        defaults = json.load(f)
    f.close()

    local = Path(defaults["base_path"]).resolve()
    remote = defaults["mount_point"]

    confirm = input(
        f"Are you sure you want to synchronise\n"
        f"  FROM: {remote} (= remote folder)\n"
        f"  TO:   {local}\n"
        f"[y/N]: "
    )

    if confirm.lower() != "y":
        print("Download cancelled.")
        return

    result = sync_smb(local, remote, "download")

    return result

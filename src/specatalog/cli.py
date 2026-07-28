import argparse
import datetime
import shutil
import subprocess
import tempfile
from getpass import getpass
from pathlib import Path
import json


def print_welcome():
    try:
        from specatalog.main import archive

        if archive.exists(""):
            print(f"""
                  Welcome to specatalog! \n
                  Your archive directory can be found at: \n
                  {archive.archive}\n
                  Have fun!
                  """)
        else:
            raise FileNotFoundError(f"Archive directory not found at {archive.archive}")

    except Exception as e:
        full_message = input(
            "Specatalog could not be loaded! Please run the postinstall first ('specatalog-configuration')\n"
            "If this error persists press 'y' to see the full error message... "
        )
        if full_message == "y":
            print(e)


def configure_defaults():
    # Path to the JSON file
    home_defaults = Path.home() / ".specatalog" / "defaults.json"

    # Step 1: Load existing values from JSON file
    try:
        with home_defaults.open("r") as f:
            result_dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, start with empty values
        result_dict = {
            "remote_archive": False,
            "archive_path": "",
            "host": "",
            "share": "",
            "archive_usr_name": "",
            "archive_password": "",
            "database_url": "",
            "db_usr_name": "",
            "db_password": "",
        }

    # Step 2: Get user input for each key with current values in messages
    # First handle remote_archive since it affects other fields
    current_remote = result_dict.get("remote_archive", False)
    remote_input = input(
        f"Use remote archive? (True/False) [Current: {current_remote}]: "
    ).strip()

    if remote_input.lower() in ["true", "yes", "y"]:
        result_dict["remote_archive"] = True
    elif remote_input.lower() in ["false", "no", "n"]:
        result_dict["remote_archive"] = False
    elif remote_input:  # Non-empty but invalid input
        print(f"Invalid input. Keeping current value: {current_remote}")

    # Now handle other fields based on remote_archive setting
    if not result_dict.get("remote_archive", False):
        # Handle archive_path
        current_path = result_dict.get("archive_path", "")
        path_input = input(f"Enter archive path [Current: {current_path}]: ").strip()
        if path_input:  # Only update if user provided new input
            result_dict["archive_path"] = path_input

    else:
        # Handle host, share, archive_usr_name, archive_password
        fields = [
            ("host", "Enter host name"),
            ("share", "Enter share name"),
            ("archive_usr_name", "Enter archive username"),
            ("archive_password", "Enter archive password"),
        ]

        for field, message in fields:
            current_value = result_dict.get(field, "")
            user_input = input(f"{message} [Current: {current_value}]: ").strip()
            if user_input:  # Only update if user provided new input
                result_dict[field] = user_input

    # Always ask for database fields
    db_fields = [
        ("database_url", "Enter database URL"),
        ("db_usr_name", "Enter database username"),
        ("db_password", "Enter database password"),
    ]

    for field, message in db_fields:
        current_value = result_dict.get(field, "")
        user_input = input(f"{message} [Current: {current_value}]: ").strip()
        if user_input:  # Only update if user provided new input
            result_dict[field] = user_input

    # Step 3: Save the updated configuration to JSON file
    # Ensure the directory exists
    home_defaults.parent.mkdir(parents=True, exist_ok=True)

    # Write the updated configuration
    with home_defaults.open("w") as f:
        json.dump(result_dict, f, indent=2)

    return result_dict

def build_backup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specatalog-backup",
        description="Backup specatalog archive and database",
    )

    parser.add_argument("--destination",
                        type=str,
                        required=True,
                        help="destination for backup")

    parser.add_argument("--db_admin",
                        type=str,
                        default="",
                        help="database admin username")

    parser.add_argument("--db_name",
                        type=str,
                        default="specatalog",
                        help="database name")

    return parser

def call_backup():
    import specatalog.config as c
    from specatalog.main import archive
    parser = build_backup_parser()
    args = parser.parse_args()

    if args.db_admin:
        admin_password = getpass(prompt="Specatalog admin password: ")
        admin_name = args.db_admin
    else:
        admin_name = c.USR_NAME
        admin_password = c.PASSWORD

    if not archive.use_remote_archive:

        create_backup(args.destination,
                      archive,
                      c.database,
                      admin_name,
                      admin_password)

    else:
        create_backup(args.destination,
                      archive,
                      c.database,
                      admin_name,
                      admin_password,
                      c.USERNAME,
                      c.PWD)
    print("BACKUP!")


def create_backup(
    backup_root: Path,
    archive: Path,
    database_url: str,
    admin_name: str,
    admin_password: str,
    archive_usr_name=None,
    archive_password=None
) -> Path:

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_root = Path(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix=f".{timestamp}.",
            dir=backup_root,
        )
    )

    final_directory = backup_root / timestamp

    database_dump = temporary_directory / "database.dump"
    archive_backup = temporary_directory / "archive.tar.zst"

    try:
        # PostgreSQL-Dump im Custom-Format
        subprocess.run(
            [
                "pg_dump",
                "--dbname",
                f"postgresql://{admin_name}:{admin_password}@{database_url}",
                "--format",
                "custom",
                "--file",
                str(database_dump),
            ],
            check=True,
        )
        if archive.use_remote_archive:
            mount_point = Path("/mnt")
            mount_smb(archive.path_to_unc(""), mount_point, str(archive_usr_name), str(archive_password))
            try:
                subprocess.run(
                    [
                        "tar",
                        "--verbose",
                        "--zstd",
                        "--create",
                        "--file",
                        str(archive_backup),
                        "--directory",
                        f"{mount_point}", ".",
                    ],
                    check=True,
                )
            finally:
                print("unmount")
                subprocess.run(
                    ["sudo","umount", str(mount_point)],
                    check=True,
                )
        else:
            subprocess.run(
                [
                    "tar",
                    "--verbose",
                    "--zstd",
                    "--create",
                    "--file", str(archive_backup),
                    "--directory", str(archive.archive.parent),
                    archive.archive.name,
                ],
                check=True,
            )

        manifest = {
            "created_at": timestamp,
            "database": {
                "db_url" : database_url,
                "format": "custom",
            },
            "archive_directory": str(archive.archive),
            "files": {
                "database_dump": database_dump.name,
                "archive_backup": archive_backup.name,
            },
        }

        (temporary_directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )

        # Atomisches Fertigstellen des Backups
        temporary_directory.rename(final_directory)

        return final_directory

    except Exception:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

def mount_smb(
    remote: str,
    mount_point: Path,
    username: str,
    password: str,
) -> None:
    mount_point.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "sudo",
            "mount",
            "-t",
            "cifs",
            remote,
            str(mount_point),
            "-o",
            f"username={username},password={password}",
        ],
        check=True,
    )
    print("MOUNT!")
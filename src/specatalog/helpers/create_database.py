""" run only once to create the databases """

import sys
from pathlib import Path
import subprocess
from alembic.config import Config
from alembic import command
from specatalog.main import DATABASE_URL_ADMIN

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# create archive directory
def create_archive_directory():
    from specatalog.main import  BASE_PATH, MOLECULES_PATH, MEASUREMENTS_PATH
    import os
    import shutil

    try:
        os.makedirs(BASE_PATH / MOLECULES_PATH, exist_ok=True)
        print(f"Molecules folder created. at {BASE_PATH} / {MOLECULES_PATH}")

        os.makedirs(BASE_PATH / MEASUREMENTS_PATH, exist_ok=True)
        print(f"Measurements folder created. at {BASE_PATH} / {MEASUREMENTS_PATH}")
    except Exception as e:
        print(f"Directory could not be created: {e}.")
        return False

    try:
        if not (BASE_PATH / "allowed_values.py").exists():
            shutil.copy(CURRENT_DIR / "allowed_values_not_adapted.py",
                        BASE_PATH / "allowed_values.py")
            print(f"{BASE_PATH / 'allowed_values.py'} created.")
        else:
            print(f"{BASE_PATH / 'allowed_values.py'} exists.")
    except Exception as e:
        print(f"allowed_values.py could not be created: {e}.")
        return False

    return True


def run_alembic_upgrade():
    """
    Apply all migrations (initial schema)
    """
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL_ADMIN)
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    command.upgrade(alembic_cfg, "head")
    print("Database is up to date.")
    return



def specatalog_init_db():
    from specatalog.main import BASE_PATH
    exist = input(f"Does the archive and database already exist at {BASE_PATH}? y/n?")

    if exist == "n":
        create_archive_directory()
        run_alembic_upgrade()

    else:
        print("No new archive created.")

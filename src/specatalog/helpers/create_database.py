"""run only once to create the databases"""

from pathlib import Path
from alembic.config import Config
from alembic import command
from specatalog.main import archive

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# create archive directory
def create_archive_directory():
    """
    Creates the archive directory structure using the provided SpecatalogArchive object.

    Returns:
        bool: True if successful, False otherwise
    """
    # Define path definitions
    measurements_path = "data"
    molecules_path = "molecules"

    try:
        # Create molecules folder
        archive.make_dir(molecules_path)
        print(f"Molecules folder created at {archive.archive}/{molecules_path}")

        # Create measurements folder
        archive.make_dir(measurements_path)
        print(f"Measurements folder created at {archive.archive}/{measurements_path}")

    except Exception as e:
        print(f"Directory could not be created: {e}")
        return False

    try:
        # Create allowed_values.py if it doesn't exist
        allowed_values_path = "allowed_values.py"
        if not archive.exists(allowed_values_path):
            # Get the path to the template file
            template_path = CURRENT_DIR / "allowed_values_not_adapted.py"

            # Copy the template file to the archive
            archive.copy_to_archive(template_path, allowed_values_path)
            print(f"{archive.archive}/{allowed_values_path} created.")
        else:
            print(f"{archive.archive}/{allowed_values_path} exists.")

    except Exception as e:
        print(f"allowed_values.py could not be created: {e}")
        return False

    return True


def run_alembic_upgrade():
    """
    Apply all migrations (initial schema)
    """
    from specatalog.config import DATABASE_URL_ADMIN

    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL_ADMIN)
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    command.upgrade(alembic_cfg, "head")
    print("Database is up to date.")
    return


def specatalog_init():
    from specatalog.config import BASE_PATH

    exist = input(f"Does the archive and database already exist at {BASE_PATH}? y/n?")

    if exist == "n":
        create_archive_directory()
        run_alembic_upgrade()

    else:
        print("No new archive created.")

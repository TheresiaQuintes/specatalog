"""run only once to create the databases"""

from pathlib import Path
from alembic.config import Config
from alembic import command
from specatalog.main import archive

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# create archive directory
def create_archive_directory() -> bool:
    """Create the basic archive directory structure.

    Creates the required directory structure and configuration files
    for the measurement archive.

    Returns
    -------
    bool
        True if directory creation was successful, False otherwise

    Notes
    -----
    Creates:
    - data/ directory for measurements
    - molecules/ directory for molecule data
    - allowed_values.py configuration file
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


def run_alembic_upgrade() -> None:
    """Apply all database migrations to bring schema to current version.

    Uses Alembic to upgrade the database schema to the latest version
    defined in the migration scripts.

    Notes
    -----
    - Requires valid database connection configuration
    - Will create all tables and apply all migrations
    - Prints confirmation message upon completion
    """
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


def specatalog_init() -> None:
    """Initialize the Specatalog system.

    Checks if archive and database already exist, and if not,
    creates them by:
    1. Setting up the directory structure
    2. Applying database migrations

    Notes
    -----
    - Prompts user to confirm if existing setup should be used
    - Only creates new setup if user answers 'n'
    - Prints status messages during initialization
    """
    from specatalog.config import BASE_PATH

    exist = input(f"Does the archive and database already exist at {BASE_PATH}? y/n?")

    if exist == "n":
        create_archive_directory()
        run_alembic_upgrade()

    else:
        print("No new archive created.")

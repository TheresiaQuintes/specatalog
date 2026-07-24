import json
from pathlib import Path
import shutil
from importlib.resources import files, as_file


home_defaults = Path.home() / ".specatalog" / "defaults.json"
if not home_defaults.exists():
    home_defaults.parent.mkdir(exist_ok=True)
    src_trav = files("specatalog.user") / "defaults.json"
    with as_file(src_trav) as src:
        shutil.copy(src, home_defaults)

with home_defaults.open("r") as f:
    defaults = json.load(f)
f.close()

# set path definitions
BASE_PATH = Path(defaults["archive_path"]).resolve()
MEASUREMENTS_PATH = Path("data")
MOLECULES_PATH = Path("molecules")

REMOTE_ARCHIVE = defaults["remote_archive"]

# remote login
HOST = defaults["host"]
SHARE = defaults["share"]
USERNAME = defaults["archive_usr_name"]
PWD = defaults["archive_password"]

# create database postgre
USR_NAME = defaults["db_usr_name"]
PASSWORD = defaults["db_password"]
database = defaults["database_url"]
DATABASE_URL_USR = f"postgresql+psycopg2://{USR_NAME}:{PASSWORD}@{database}"
DATABASE_URL_ADMIN = (
    f"postgresql+psycopg2://specatalog_admin:administration_of_specatalog@{database}"
)

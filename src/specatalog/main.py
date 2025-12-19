import sqlalchemy as alc
import sqlalchemy.orm as orm
import json
from pathlib import Path
import shutil
from importlib.resources import files

home_defaults = Path.home() / ".specatalog" / "defaults.json"
if not home_defaults.exists():
    home_defaults.parent.mkdir(exist_ok=True)
    shutil.copy(files("specatalog.user") / "defaults.json", home_defaults)

with home_defaults.open("r") as f:
    defaults = json.load(f)
f.close()

# set path defintions
BASE_PATH = Path(defaults["base_path"]).resolve()
MEASUREMENTS_PATH = Path("data")
MOLECULES_PATH = Path("molecules")

# create database postgre
USR_NAME = defaults["usr_name"]
PASSWORD = defaults["password"]
database = defaults["database_url"]
DATABASE_URL_USR = (
    f"postgresql+psycopg2://{USR_NAME}:{PASSWORD}@{database}"
    )
DATABASE_URL_ADMIN = (
    f"postgresql+psycopg2://specatalog_admin:administration_of_specatalog@{database}"
    )


engine = alc.create_engine(
    DATABASE_URL_USR,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# initialise session and connect to engine
Session = orm.scoped_session(
    orm.sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
        )
    )

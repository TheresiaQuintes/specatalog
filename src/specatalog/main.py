import sqlalchemy as alc
import sqlalchemy.orm as orm
import json
from pathlib import Path
import shutil
from importlib.resources import files, as_file
from contextlib import contextmanager
import importlib.util
import sys

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
BASE_PATH = Path(defaults["base_path"]).resolve()
MEASUREMENTS_PATH = Path("data")
MOLECULES_PATH = Path("molecules")

# create database postgre
USR_NAME = defaults["usr_name"]
PASSWORD = defaults["password"]
database = defaults["database_url"]
DATABASE_URL_USR = f"postgresql+psycopg2://{USR_NAME}:{PASSWORD}@{database}"
DATABASE_URL_ADMIN = (
    f"postgresql+psycopg2://specatalog_admin:administration_of_specatalog@{database}"
)


engine = alc.create_engine(
    DATABASE_URL_USR, echo=True, pool_size=10, max_overflow=20, pool_pre_ping=True
)

# initialise session and connect to engine
Session = orm.scoped_session(
    orm.sessionmaker(
        autoflush=False, autocommit=False, bind=engine, expire_on_commit=False
    )
)


@contextmanager
def db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        Session.remove()


# Import external allowed_values
_ALLOWED_VALUES_MODULE = None


def load_allowed_values(path: Path):
    global _ALLOWED_VALUES_MODULE

    if _ALLOWED_VALUES_MODULE is not None:
        return _ALLOWED_VALUES_MODULE

    spec = importlib.util.spec_from_file_location("allowed_values", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")

    module = importlib.util.module_from_spec(spec)

    sys.modules[spec.name] = module

    spec.loader.exec_module(module)

    _ALLOWED_VALUES_MODULE = module
    return module


try:
    ALLOWED_VALUES = load_allowed_values(BASE_PATH / "allowed_values.py")
except FileNotFoundError:
    print("Please run postinstall to generate your own allowed_values.py.")
    import specatalog.helpers.allowed_values_not_adapted as module
    ALLOWED_VALUES = module

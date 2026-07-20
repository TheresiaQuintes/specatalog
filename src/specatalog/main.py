import sqlalchemy as alc
import sqlalchemy.orm as orm
from pathlib import Path
from contextlib import contextmanager
import importlib.util
import sys

from specatalog.config import DATABASE_URL_USR, BASE_PATH, REMOTE_ARCHIVE
from specatalog.data_management.remote import SpecatalogArchive

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

if REMOTE_ARCHIVE == "True":
    remote = True
else:
    remote = False

archive = SpecatalogArchive(remote, BASE_PATH)

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

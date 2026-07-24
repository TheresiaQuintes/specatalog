"""
Database and Archive Management Module for Specatalog

This module provides:
- Database connection management
- Archive file system access
- Allowed values configuration loading
- Session handling for database operations

Key Components:
1. Database Connection:
   - SQLAlchemy engine with connection pooling
   - Scoped session factory for thread-safe operations
   - Context manager for database sessions

2. Archive Access:
   - SpecatalogArchive instance for file operations
   - Support for both local and remote archives

3. Configuration:
   - Allowed values loading from external module
   - Fallback to default values if configuration missing

Configuration:
- DATABASE_URL_USR: Database connection URL
- BASE_PATH: Base path for archive
- REMOTE_ARCHIVE: Flag for remote archive usage

Usage:
- Use db_session() context manager for database operations
- Access archive through the 'archive' instance
- Access allowed values through ALLOWED_VALUES
"""

import sqlalchemy as alc
import sqlalchemy.orm as orm
from pathlib import Path
from contextlib import contextmanager
import importlib.util
import sys

from specatalog.config import DATABASE_URL_USR, BASE_PATH, REMOTE_ARCHIVE
from specatalog.data_management.archive_manager import SpecatalogArchive

# Database Engine Configuration
engine = alc.create_engine(
    DATABASE_URL_USR, echo=True, pool_size=10, max_overflow=20, pool_pre_ping=True
)

# Session Factory with Connection Pooling
Session = orm.scoped_session(
    orm.sessionmaker(
        autoflush=False, autocommit=False, bind=engine, expire_on_commit=False
    )
)

@contextmanager
def db_session():
    """Context manager for database sessions with automatic commit/rollback.

    Provides a transactional scope around a series of operations.
    Commits on successful completion, rolls back on exception.

    Yields
    ------
    Session
        SQLAlchemy session object

    Raises
    ------
    Exception
        Any exception raised during the session operations
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        Session.remove()

# Archive Configuration
if REMOTE_ARCHIVE:
    remote = True
else:
    remote = False

archive = SpecatalogArchive(remote, BASE_PATH)

# Allowed Values Configuration
_ALLOWED_VALUES_MODULE = None


def load_allowed_values(path: Path):
    """Load allowed values configuration from external module.

    Parameters
    ----------
    path : Path
        Path to the allowed_values.py module

    Returns
    -------
    module
        Loaded module containing allowed values

    Raises
    ------
    ImportError
        If module cannot be loaded from specified path
    """
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


# Load allowed values configuration
if archive.exists("allowed_values.py"):
    with archive.temporary_path("allowed_values.py") as pt:
        ALLOWED_VALUES = load_allowed_values(pt)

else:
    print("Please run postinstall to generate your own allowed_values.py.")
    import specatalog.helpers.allowed_values_not_adapted as module

    ALLOWED_VALUES = module
import os
import sqlalchemy as alc
import sqlalchemy.orm as orm
import json
from pathlib import Path


defaults_path = Path(__file__).resolve().parent / "user" / "defaults.json"

with open(defaults_path, "r") as f:
    defaults = json.load(f)

BASE_PATH = Path(defaults["base_path"])
MEASUREMENTS_PATH = Path("data")
MOLECULES_PATH = Path("molecules")

# initialise engine
engine = alc.create_engine(f"sqlite:///{BASE_PATH}/spektro.db", echo=True)

# initialise session and connect to engine
Session = orm.scoped_session(
    orm.sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
        )
    )

# parameter fürs erstellen neuer engines (im Fall von sqlite)
@alc.event.listens_for(alc.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

import os
import sqlalchemy as alc
import sqlalchemy.orm as orm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# initialise engine
engine = alc.create_engine(f"sqlite:///{BASE_DIR}/spektro.db", echo=True)

# initialise session and connect to engine
session = orm.scoped_session(
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

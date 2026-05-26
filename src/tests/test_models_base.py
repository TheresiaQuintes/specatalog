from specatalog.models.base import Model
import time
from sqlalchemy import Column, Integer, String
from specatalog.models.base import TimeStampedModel
from datetime import datetime


class Dummy(TimeStampedModel):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String)


def test_table_exists(engine):
    assert "dummy" in Model.metadata.tables


def test_created_at_is_set(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    assert obj.created_at is not None
    assert isinstance(obj.created_at, datetime)


def test_updated_at_initial(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    assert obj.updated_at is None


def test_updated_at_on_update(db_session):
    obj = Dummy(name="test")

    db_session.add(obj)
    db_session.commit()

    first_created = obj.created_at

    time.sleep(0.01)  # wichtig für Timestamp-Differenz

    obj.name = "changed"
    db_session.commit()

    assert obj.updated_at is not None
    assert obj.updated_at >= first_created


def test_no_update_does_not_change_timestamp(db_session):
    obj = Dummy(name="test")
    db_session.add(obj)
    db_session.commit()

    created_updated = obj.updated_at

    db_session.commit()  # kein change

    assert obj.updated_at == created_updated




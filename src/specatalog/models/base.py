import datetime

import sqlalchemy as alc
import sqlalchemy.orm as orm
from sqlalchemy import event

from specatalog.main import Session


Model = orm.declarative_base()
Model.query = Session.query_property()


class TimeStampedModel(Model):
    """
    Abstract base class providing automatic timestamp fields for all
    inheriting SQLAlchemy models.

    This class adds two metadata fields, ``created_at`` and
    ``updated_at``, which are populated automatically whenever an object is
    created or modified.

    Attributes
    ----------
    created_at : datetime.datetime
        Timestamp indicating when the record was first created.
        Automatically assigned at insert time using
        ``datetime.now(datetime.UTC)``.
    updated_at : datetime.datetime or None
        Timestamp indicating when the record was last modified.
        Automatically updated before any SQL UPDATE operation.
        May be ``None`` if the record has not been changed since creation.

    Notes
    -----
    * The class is declared ``__abstract__`` and therefore does not create
      its own database table.
    * ``updated_at`` is updated using a SQLAlchemy ``before_update`` event
      listener attached to ``TimeStampedModel`` with ``propagate=True``.
    * ``Model.query`` is set to ``Session.query_property()``, allowing
      models inheriting from ``TimeStampedModel`` to use ``Model.query``
      in a Flask-style query interface (``MyModel.query.filter(...)``).

    Examples
    --------
    Creating a new model with timestamps:

    >>> class Molecule(TimeStampedModel):
    ...     __tablename__ = "molecules"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String)

    >>> m = Molecule(name="Water")
    >>> session.add(m)
    >>> session.commit()

    Accessing timestamps:

    >>> m.created_at
    datetime.datetime(2025, 4, 12, 14, 30, tzinfo=datetime.UTC)

    >>> m.updated_at
    None

    After modification:

    >>> m.name = "Heavy Water"
    >>> session.commit()

    >>> m.updated_at
    datetime.datetime(2025, 4, 12, 14, 32, tzinfo=datetime.UTC)
    """
    __abstract__ = True

    created_at = alc.Column(alc.DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = alc.Column(alc.DateTime, onupdate=datetime.datetime.now(datetime.UTC))



@event.listens_for(TimeStampedModel, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.datetime.now(datetime.UTC)

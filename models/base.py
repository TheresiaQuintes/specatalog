import datetime

import sqlalchemy as alc
import sqlalchemy.orm as orm
from sqlalchemy import event

from main import Session


Model = orm.declarative_base()
Model.query = Session.query_property()


class TimeStampedModel(Model):
    __abstract__ = True

    created_at = alc.Column(alc.DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = alc.Column(alc.DateTime, onupdate=datetime.datetime.now(datetime.UTC))



@event.listens_for(TimeStampedModel, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.datetime.now(datetime.UTC)

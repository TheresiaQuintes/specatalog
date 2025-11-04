import datetime

import sqlalchemy as alc
import sqlalchemy.orm as orm

from main import session


Model = orm.declarative_base()
Model.query = session.query_property()


class TimeStampedModel(Model):
    __abstract__ = True

    created_at = alc.Column(alc.DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = alc.Column(alc.DateTime, onupdate=datetime.datetime.now(datetime.UTC))

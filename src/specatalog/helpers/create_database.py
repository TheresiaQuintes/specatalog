""" run only once to create the databases """

from specatalog.main import engine
from specatalog.models.base import Model
from specatalog.models.measurements import *
from specatalog.models.molecules import *


Model.metadata.create_all(engine)

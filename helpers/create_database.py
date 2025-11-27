""" run only once to create the databases """

from main import engine
from models.base import Model
from models.measurements import *
from models.molecules import *


Model.metadata.create_all(engine)

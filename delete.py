from models.measurements import Measurement
from models.molecules import Molecule
from main import session

ms = Measurement.query.filter(Measurement.id==1).first() # ID wird gelöscht, wird nicht neu vergeben = Lücken in ID-Liste können existieren. Wenn ID die letzte war, wird sie neu vergeben

session.delete(ms)
session.commit()

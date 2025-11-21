from crud_db import read as r
from crud_db import update as up

measurement = r.run_query(r.MeasurementFilter(id=1))[0]

updates = up.CWEPRUpdate(frequency_band="Q", temperature=80, solvent="toluene", evaluated=True)

up.update_model(measurement, updates)

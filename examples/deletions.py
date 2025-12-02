import specatalog.data_management.hdf5_reader as hf
import numpy as np
from specatalog.crud_db import delete as de
from specatalog.data_management import measurement_management as mm
from specatalog.main import BASE_PATH


# attributes / datasets from hdf5
dat, file = hf.load_from_id(11, mode="a")

dat.set_attr("test", 5)
dat.set_dataset("test_set", np.zeros(5))
dat.sync()

print(vars(dat))

dat.delete_attr("test")
dat.delete_dataset("test_set")
dat.sync()
print(vars(dat))





# measurements
# de.delete_measurement(ms_id=14)
# mm.delete_measurement(BASE_PATH, 14)

# molecules (all connected measurements are also deleted!! Only delete new molecules)
#de.delete_molecule(mol_id=2)

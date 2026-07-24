import numpy as np

from specatalog.data_management import hdf5_reader as hf


# Attributes und Datasets einer HDF5-Messdatei bearbeiten
with hf.load_from_id(4, mode="a") as (dat, h5_file):
    dat.set_attr("test", 5)
    dat.set_dataset("test_set", np.zeros(5))

    # Änderungen in die HDF5-Datei schreiben
    dat.sync()

    print(vars(dat))

    # Attribute und Dataset wieder löschen
    dat.delete_attr("test")
    dat.delete_dataset("test_set")

    # Löschungen in die HDF5-Datei schreiben
    dat.sync()

    print(vars(dat))


# measurements
# delete_full_measurement(ms_id=14)

# molecules (all connected measurements are also deleted!! Only delete new molecules)
# de.delete_molecule(mol_id=2)

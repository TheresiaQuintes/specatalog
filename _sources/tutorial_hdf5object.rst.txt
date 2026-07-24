Measurement.h5 file
===================

To enable clean archiving of the processing and analysis of raw data, a measurement_{ms_id}.h5 file is created
for each measurement. The file has the following structure::

	measurement_{ms_id}.h5
	├── raw_data
	│   ├── data
	│   ├── data_imag
	│   ├── data_real
	│   └── xaxis
	├── corrected_data
	│   └── <can be added>
	└── evaluations
		└── <can be added>


When a new measurement is created using the ``data_management``-package, the file is automatically created and
the raw data are added to the ``raw_data``-group. When you work with the data and correct them or do analysis,
like fitting, it is advised to add the results to the groups of the measurement.h5-file, so that they are systematically
archived.

.. hint::
	As the file is a HDF5-file, it can be inspected by any reader for HDF5-files e.g. the online tool `myHDF5 <https://myhdf5.hdfgroup.org/>`_.
	The data can be loaded to python by the `h5py package <https://docs.h5py.org/en/stable/>`_ and to matlab using the `HDF5 Functions <https://de.mathworks.com/help/matlab/import_export/import-hdf5-files.html>`_.

For easy interactions with the HDF5-file in python specatalog provides the
:class:`HDF5Object <specatalog.data_management.hdf5_reader.H5Object>`.
In the following, the usage of this class is explained.


HDF5Object
----------

open
^^^^
It is possible to load the data to an HDF5Object by using the function
:func:`load_from_id <specatalog.data_management.hdf5_reader.load_from_id>`.
All datasets are attributes to the data-object and can be easily called as shown in the example below.
Set the optional argument ``mode`` to ``"a"`` if you want to change the contens of the file and to ``"r"`` if you only want
to read the file::

	from specatalog.data_management.hdf5_reader import load_from_id
	import matplotlib.pyplot as plt
	import numpy as np

	# load data from ms_id=1 (UV-vis)
	with load_from_id(1, mode="a") as (dat, file):
		# raw data
		x = dat.raw_data.xaxis
		intensity = dat.raw_data.data

		# plot data
		plt.plot(x, np.real(intensity))
		plt.xlabel("x")
		plt.ylabel("intensity")
		plt.title("raw measurement")
		plt.show()

update
^^^^^^
If you have new data and want to add them or want to update existing attributes you can use the
``set_attr`` method for attributes (= numbers / strings) and the ``set_dataset`` method for datasets (= arrays)::
	
	with load_from_id(1, mode="a") as (dat, file):
		# Load original data
		x = dat.raw_data.xaxis
		intensity = dat.raw_data.data

		# Perform correction
		offset = 2.3
		corrected = x - offset

		# Calculate fit function
		fit = -2*(x-12000)**2 + 2500

		# Store new data
		dat.corrected_data.set_attr("x-offset", offset)  # Store offset as attribute
		dat.corrected_data.set_dataset("xaxis", corrected)  # Store corrected axis as dataset
		dat.evaluations.set_dataset("fit1", fit)  # Store fit result as dataset

		# Immediately write changes to file
		dat.sync()

delete
^^^^^^ 
If you want to delete attributes you can use the ``delete_attr`` method, for datasets you can use the ``delete_dataset``::

	with load_from_id(1, mode="a") as (dat, file):
		# Delete an imaginary data dataset from raw_data group
		dat.raw_data.delete_dataset("data_imag")

		# Immediately write changes to file
		dat.sync()

sync
^^^^
All changes are written to the file using the ``sync`` method. Call this method ath the end of your script::
	
	dat.sync()

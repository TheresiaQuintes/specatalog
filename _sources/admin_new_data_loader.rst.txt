Adding new loaders
==================

If your group uses a new file format that is not implemented to specatalog you can contribute to the code and adding a new loader function.

1. Write a function, that loads your data::

	def load_xyz(path_to_data):
		...
		return data, abscissa, meta
	
``data`` and ``abscissa`` should be of type ``numpy.ndarray``, ``meta`` should be a dictionary that contains the metadata as key-value pairs.

2. Copy the functions to the file ``data_management/data_loader.py``.

3. Open the file ``data_management/measurement_management.py``. Add the new file format to the dictionary ``SUPPORTED_FORMATS`` at the top of the file.

4. Add a new ``elif``-statement for the new format to the functions ``raw_data_to_folder`` and ``raw_data_to_hdf5``. Don't forget to adapt the docstring of ``raw_data_to_folder`` and add the new format.

5. Update the documentation ``tutorial_measurements.rst`` and add the new format in the ``..note``  of No.5 in the section *Creation of a new entry*.


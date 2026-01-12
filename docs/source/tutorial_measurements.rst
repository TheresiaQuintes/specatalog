Measurements
============

The measurements table contains a row for each measurement, which shows the relevant metadata. All measurements are referenced by an unique ID (ms_id) and are correlated with a molecule from the molecules table. Further each measurement entry belongs to a subtable which is classified by the method chosen for the measurement (e.g. cwEPR or trEPR...). The subtable contains metadata that is specific for the method and is referenced by the same ms_id as the main table. In the archive folder at ``/data/M{ms_id}`` a directory with all files concerning the measurement (e.g. raw data, scripts...) are saved. In the following you will learn how to set up a new measurement in the database and how to create the correlated directory, how to find and work with a specific measurement, update it or delete an existing measurement.


Creation of a new entry
-----------------------

First of all a new entry shall be added to the measurements table and the data-archive. As an example we will add a transient EPR spectra of our example molecule :ref:`PER-TEMPO <tutorial-molecules-new-entry>`. 

1. Store your raw data at any folder. Save the path without suffix to a variable::

	raw_data = "/path/to/your/folder/trEPR_PER_TEMPO

2. Find the ID of the corresponding molecule::
	
	from specatalog.crud_db import read as r
	
	per_tempo_filter = r.TDPFilter(name="PER-co-NO1")
	per_tempo_molecule = r.run_query(per_tempo_filter)[0]
	print(per_tempo_molecule.id)
	>>> 2

3. Set up the MeasurementModel dependent on the method.

	The required fields for each method can be found in the documentation of the module :ref:`models-creation-pydantic-measurements`.::
	
		from specatalog.models import creation_pydantic_measurements as ms
		from datetime import date
		
		new_measurement = ms.TREPRModel(molecular_id=1,
						temperature=80,
						solvent="toluene",
						date=date(2025, 12, 24),
						measured_by="your_name",
						device="ELEXSYS",
						frequenc_band="Q",
						attenuation="20dB",
						exciation_wl=530)
	
	.. note::
	
		Some of the fields have a special type which is neiter a number nor a string but a class from ``allowed_values.py``. For example the parameter ``solvent`` needs to be from the class ``Solvents``. In that case only the values that are specified in ``allowed_values.py`` will be accepted. For more details see the documentation about :doc:`tutorial_allowed_values`.

4. Use the function :func:`create_new_measurement <specatalog.crud_db.create.create_new_measurement>` to add the entry to the table of the database::

	from specatalog.crud_db import create
	
	measurement = create.create_new_measurement(new_measurement)

5. Use the information from the variable ``measurement`` to set up the directory in the database.
	
	The ``measurement`` object contains the attribute ``measurement.id``. The ID of the measurement can be used to name the directory correctly. It is recommended to use the functions from the module :ref:`measurement_management <data-management-measurement-management>`::
		
		import specatalog.data_management.measurement_management as mm
		from specatalog.main import BASE_PATH
		
		mm.create_measurement_dir(BASE_PATH, measurement.id)  # create new directory with subfolders
		mm.raw_data_to_folder(raw_data, "bruker_bes3t", BASE_PATH, measurement.id)  # raw data are copied to /data/M{ms_id}/raw
		mm.raw_data_to_hdf5(BASE_PATH, measurement.id, "bruker_bes3t")  # The raw spectra are added to the measurement.h5-file as arrays
		
	.. note::
	
		The functions ``raw_data_to_foler`` and ``raw_data_to_hdf5`` can be used only to specific formats. At the moment the following formats are supported:
			
			- ``"bruker_bes3t"``: for sets of Bruker files with the suffixes ``.DSC`` and ``.DTA`` and optional ``.YGF``.
			- ``"uvvis_ulm"``: for UVvis files measured at the spectrometer located at Ulm with the suffix ``.txt``.
			- ``"uvvis_freiburg"``: for UVvis files measured at the spectrometer located at Freiburg with the suffix ``.txt``.
		
		For all other formats the functions will not work. The files for the measurement have to be copied manually to ``/data/M{ms_id}/raw`` and have to be loaded and stored in the ``measurement.h5``-file (for more information see the documentation about :doc:`tutorial_hdf5object`).
		
	
Query the database
------------------
It is possible to filter the database for measurements with specific properties. This may become necessary in order to get an overview over the measurements that have been done or for finding out the ms_id of a specific measurement to work with. As an example we want to query the database for all trEPR measurements that have been done so far in frozen solution for the molecule with mol_id = 1 by you.

1. Set up a filter model
	
	An empty filter model includes all possible fields. You can fill the model with your desired properties. All possible FilterModels and an explanation of their fields can be found :ref:`here <crud-db-filtermodels>`.::
		
		from specatalog.crud_db import read as r
		
		filter_model = r.TREPRFilter(molecular_id=1, temperature__le=80, measured_by="your name")

2. (Optional) Set up an ordering model
	
	If you want to sort your results you can construct an :ref:`ordering model <crud-db-orderingmodels>`, where you can choose for each parameter if the list of results shall be ordered ascending (``"asc"``) or descending (``"descending"```). An OrderingModel is not required but in our example we sort the results with respect to the measurement data::
		
		ordering_model = r.TREPROrdering(date="asc")
	

3. Run the query using the function :func:`run_query <specatalog.crud_db.read.run_query>`.
	
	Now you can run the query and print the results. The printed results have the structure: (name of the data folder: method, name of the molecule)::
		
		results = r.run_query(filter_model, ordering_model)
		
		print(results)  # print the list with all results
		>>> (M2: TREPR; PDI4-co-NO4)
		
		print(results[0].id)
		>>> 2
		
		print(results[0].molecule.name
		>>> PER-co-NO1
	
	The function returns a list of measurement objects. You cann call the values of the attributes like the ID or the molecule. The molecule is again an object where you can call all attributes.

Update measurements
-------------------

If you have to change information on a measurement it is possible to update the database entries. As an example you have done some some analysis on your spectral data of the measurement with the ms_id=1 that you have saved in the archive folder. Now you can set the entry for evaluated to true in order to mark the dataset as evaluated.

1. Load the measurement.
	
	We will load the entry with the ID=1 by querying the database for the measurement with id=1 and choosing the first (and only) result from the list.::
	
		from specatalog.crud_db import read as r
		ms_1 = r.run_query(r.MeasurementFilter(id=1))[0]  

2. Build an update filter
	
	Analoguos to the models for filtering :ref:`UpdateModels <crud-db-updatemodels>` exist. Each attribute of an object of the class UpdateModel can be set to a new attribute (of the correct type)::
	
		from specatalog.crud_db import update as up
		update_evaluated = up.MeasurementUpdate(evaluated=True)

3. Update the database entry by using the function :func:`update_model <specatalog.crud_db.update.update_model>`.::
	
	up.update_model(ms_1, update_evaluated)

Delete measurements
-------------------

A measurement with the ID ms_id, can be easily deleted. Make sure to delete the database entry **and** the corresponding folder in the archive directory::

	from specatalog.crud_db import delete as de
	from specatalog.data_management import measurement_management as mm
	from specatalog.main import BASE_PATH
	
	# deletion from database
	de.delete_measurement(ms_id=14) 
	
	# deletion from directory
	mm.delete_measurement(BASE_PATH, 14)

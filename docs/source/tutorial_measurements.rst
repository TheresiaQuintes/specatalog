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
		mm.raw_data_to_hdf5(BASE_PATH, measurement.id)  # The raw spectra are added to the measurement.h5-file as arrays
		
	.. note::
	
		The functions ``raw_data_to_foler`` and ``raw_data_to_hdf5`` can be used only to specific formats. At the moment the following formats are supported:
			
			- ``"bruker_bes3t"``: for sets of Bruker files with the suffixes ``.DSC`` and ``.DTA`` and optional ``.YGF``.
		
		For all other formats the functions will not work. The files for the measurement have to be copied manually to ``/data/M{ms_id}/raw`` and have to be loaded and stored in the ``measurement.h5``-file (for more information see the documentation about :doc:`tutorial_hdf5object`).
		
	
Query the database
------------------

Update measurements
-------------------

Delete measurements
-------------------


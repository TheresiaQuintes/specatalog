The organisation of the archive
===============================

The archive directory
---------------------

When using specatalog, your data are organised systematically in an archive directory. It hast the following structure::

	base_dir/
	├── data/
	│   ├── M1/
	│   ├── M2/
	│   ├── M3/
	│   ├── ...
	│   └── M{ms_id}/
	│       ├── additional_info/
	│       ├── figures/
	│       ├── literature/
	│       ├── raw/
	│       ├── scripts/
	│       └── measurement_M{ms_id}.h5
	├── molecules/
	│   ├── MOL1/
	│   ├── MOL2/
	│   ├── MOL3/
	│   ├── ...
	│   └── MOL{mol_id}/
	│       ├── file_with_structure.cdxml
	│       └── file_with_structure.pdf
	│
	├── allowed_values.py
	└── specatalog.db


base_dir/
^^^^^^^^^
This is the basis folder in which all data are stored. The absolute path to the folder can be set by the user in ``~/.specatalog/defaults.json``. The whole directory can be created by ``specatalog-init-db``.

data/
^^^^^
The data-directory contains all files that are related to measurements. The measurements are organised in subdirectories (one directory for each measurement) and are allocated to a number. The subdirectory is named M{ms_id}, where ms_id is the number of the measurement.

In the directory of a measurement the files are organised:

- **raw/ :** save files with raw data as returned by the spectrometer here
- **scripts/ :** save important scripts for data correction and evaluation here
- **figures/ :** save figures of your data here
- **additional_info/ :** save additional information like metadata
- **literature/ :** save literature concerning the measurement here

In each Folder you will find an automatically generated hdf5-file: **measurement_M{ms_id}.h5**. This file contains the raw data as arrays. They can be easilly loaded from this file and evaluations and corrections can also be saved in the hdf5-file using the HDF5Object-class. Find more details at the documentation of the :class:`HDF5Object <specatalog.data_management.hdf5_reader.H5Object>`.


molecules/
^^^^^^^^^^
The molecules-directory contains a folder for each molecule named MOL{mol_id} where mol_id is a unique number, which references the molecule. You should place an image of the structural formula of the molecule inside this folder.

allowed_values.py
^^^^^^^^^^^^^^^^^
This file is created, when the archive-directory is set up by specatalog for the first time. It contains allowed values for several metadata, that are stored in the database. If it is necessary these lists of allowed values can be adapted. This is explained in detail in :doc:`tutorial_allowed_values`.

specatalog.db
^^^^^^^^^^^^^
This is the main database file, which is created when the archive directory is set up by specatalog for the first time.




The database
------------

The SQLite database is stored in the archive folder. It consists of two main tables *molecules* and *measurements*.

.. note::

   The database can be queried using the :ref:`crud-db-read` module. Additionally the file specatalog.db can be opened by any programm that is able to read SQLite databases (e.g. *DB Browser for SQLite*). It is not recommended to change entries in the database using external programms but to add and update entries only using specatalog to avoid inconsistencies.
   

molecules table
^^^^^^^^^^^^^^^
The table contains the main information on the molecules. Each molecule belongs to a subgroup with specific additional information included. For the fields of the molecule table see the documentation of the :ref:`models-molecules` module. Each molecule gets an unique ID which references the molecule folder in the archive.

measurements table
^^^^^^^^^^^^^^^^^^
Each entry in the measurements table corresponds to a single measurement. In the table important metadata like the concentration, the date of the measurement or the temperature are stored. The measurement belongs to a method (= epxerimental method, e.g. TREPR). In this addtional table metatdata that are specific to the method are stored. For detaild information on the fields of the table have a look at the documentation of the :ref:`models-measurements` module. Each measurement getas an unique ID which references the measurement directory in the archive (at `/data/M{ms_id}`). 

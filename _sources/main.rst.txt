main
====

The database is referenced in main and the session is opened.


Path definitions
----------------
The following global pathes are defined in main:

``BASE_PATH``
  This is the root path of the archive-directory as defined in ``~/.specatalog/defaults.json``.
  
``MEASUREMENTS_PATH``	
  This is the foldername in the archive containing all measurement data: ``"data"``.
  
``MOLECULES_PATH`` 		
  This is the foldername in the archive containing all molecule structural formulas: ``"molecules"``.


The pathes can be imported and used by:
::

   from specatalog.main import BASEPATH, MEASUREMENTS_PATH
   
   # e.g. path to the measurement_1-directory in the archive
   measurement_1 = BASEPATH / MEASUREMENTS_PATH / "M1"
  
  
Session
-------
The SQLAlchemy-session is started in main and can be imported and used by::

   from specatalog.main import Session
   session = Session()


.. hint::
   The session is necessary for adding and commiting new or updated entries to the database.
   It is recommended to use the function ``safe_commit`` from :doc:`helpers`.

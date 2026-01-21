helpers
=======

This package contains functions that make the workflow more easy for the user:
- ``create_database`` can be used for the first setup of a new database.
- ``allowed_values_not_adapted.py`` contains the file with allowed values as it is copied to the archive root during the installation process.
- The functions in ``helper_functions`` are internally used for the dynamic  cration of models
- The module ``full_measurement`` provides functions that combine the workflow for the creation or deletion of a new measurement entry and the creation/deletion of the corresponding directory in the archive folder.


full_measurement
----------------

.. currentmodule:: specatalog.helpers.full_measurement

.. autosummary::
   :toctree: generated/
   :recursive:
   
   create_full_measurement
   delete_full_measurement



helper_functions
----------------

.. currentmodule:: specatalog.helpers.helper_functions

.. autosummary::
   :toctree: generated/
   :recursive:
   
   make_filter_model
   make_ordering_model
   make_update_model

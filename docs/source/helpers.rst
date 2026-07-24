helpers
=======

This package contains utility functions that simplify the workflow for users:

- ``create_database``: Handles initial database setup and configuration
- ``allowed_values_not_adapted.py``: Contains predefined allowed values that are copied to the archive during installation
- ``helper_functions``: Provides internal utility functions for dynamic model creation
- ``full_entry``: Combines database and file operations for complete measurement and molecule entries


create_database
---------------
This module handles the initial setup of the database and archive directory structure. It includes functions for:

- Creating the basic directory structure
- Applying database migrations
- Initializing the complete system

.. currentmodule:: specatalog.helpers.create_database

.. autosummary::
   :toctree: generated/
   :recursive:

   create_archive_directory
   run_alembic_upgrade
   specatalog_init



allowed_values_not_adapted.py
-----------------------------

This module contains predefined enumerations of allowed values for various measurement parameters.
These values are used for data validation and are copied to the archive during installation.

full_entry
----------
This module provides atomic operations for creating and deleting complete measurement and molecule entries.
It ensures that both database and file operations are performed in a transaction-safe manner.

.. currentmodule:: specatalog.helpers.full_entry

.. autosummary::
   :toctree: generated/
   :recursive:

   create_full_measurement
   delete_full_measurement
   create_full_molecule



helper_functions
----------------
This module contains internal utility functions that dynamically create Pydantic models for:

- Filtering database queries
- Ordering query results
- Updating database records

.. currentmodule:: specatalog.helpers.helper_functions

.. autosummary::
   :toctree: generated/
   :recursive:

   make_filter_model
   make_ordering_model
   make_update_model


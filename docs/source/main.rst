.. _main_module:

Main Module
===========

The `main` module provides core functionality for database and archive management in Specatalog. It handles database connections, archive file system access, and configuration loading.

Database and Archive Management
-------------------------------

This module provides:

- Database connection management
- Archive file system access
- Allowed values configuration loading
- Session handling for database operations

Key Components
^^^^^^^^^^^^^^

Database Connection
"""""""""""""""""""

- SQLAlchemy engine with connection pooling (10-30 connections)
- Scoped session factory for thread-safe database operations
- Automatic connection health checking
- Context manager for transaction handling

Archive Access
""""""""""""""

- SpecatalogArchive instance for file operations
- Support for both local and remote archive configurations
- Temporary file handling through context managers

Configuration
"""""""""""""

- Allowed values loading from external module
- Fallback to default values if configuration missing
- Remote/local archive selection based on configuration

Configuration Parameters
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Parameter
     - Description
   * - ``DATABASE_URL_USR``
     - Database connection URL from configuration
   * - ``BASE_PATH``
     - Base path for archive from configuration
   * - ``REMOTE_ARCHIVE``
     - Flag for remote archive usage from configuration

Usage Examples
^^^^^^^^^^^^^^

Database Operations
"""""""""""""""""""

.. code-block:: python

   from specatalog.main import db_session

   with db_session() as session:
       # Perform database operations
       result = session.query(MyModel).all()

Archive Operations
""""""""""""""""""

.. code-block:: python

   from specatalog.main import archive

   # List files in archive
   files = archive.list_files("data/M1")

   # Create temporary path
   with archive.temporary_path("data/M1/measurement.h5") as temp_path:
       # Work with temporary file
       process_file(temp_path)

Allowed Values
""""""""""""""

.. code-block:: python

   from specatalog.main import ALLOWED_VALUES

- Graceful fallback for missing configurations

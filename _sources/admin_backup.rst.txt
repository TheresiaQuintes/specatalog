Backup
======

The ``specatalog-backup`` command creates a backup of the Specatalog database
and archive directory.

The backup contains:

* a PostgreSQL database dump in custom format
* a compressed archive of the archive directory
* a ``manifest.json`` file containing metadata about the backup

Requirements
------------

``specatalog-backup`` has currently only been tested on Linux.

The following requirements must be met:

* Access to the complete Specatalog database
* ``pg_dump`` installed
* A ``pg_dump`` version compatible with the PostgreSQL server
  (preferably the same major version)
* ``tar`` installed
* Zstandard support for ``tar`` installed
* Sufficient permissions to read the complete archive directory
* Sufficient free disk space for the temporary and final backup files

For remote archives, the following additional requirements apply:

* CIFS/SMB support must be installed
* The user must be allowed to mount and unmount the remote archive
* ``sudo`` permissions may be required for ``mount`` and ``umount``

Creating a backup
-----------------

Specify the directory in which the backup should be stored:

.. code-block:: console

    specatalog-backup --destination /path/to/backup

The command creates a timestamped subdirectory inside the destination
directory. For example::

    /path/to/backup/
    └── 2026-07-30_14-25-10/
        ├── database.dump
        ├── archive.tar.zst
        └── manifest.json

The database credentials configured for Specatalog are used by default.

If a different database administrator should be used, specify the username
with ``--db_admin``. The password is then requested interactively:

.. code-block:: console

    specatalog-backup \
        --destination /path/to/backup \
        --db_admin DATABASE_ADMIN

The database administrator must have sufficient permissions to dump the
complete database.

Restoring the database
----------------------

The database dump is stored as ``database.dump`` in the timestamped backup
directory. Create the target database first, if necessary, and restore the
dump with ``pg_restore``:

.. code-block:: console

    pg_restore \
        -h HOST \
        -p PORT \
        -U USER \
        -d TARGET_DATABASE \
        /path/to/backup/DATE/database.dump

Depending on the target database, it may be necessary to create the database
with the appropriate owner and permissions before running ``pg_restore``.

Restoring the archive
---------------------

The archive backup is stored as ``archive.tar.zst``. Extract it into the
desired parent directory:

.. code-block:: console

    tar \
        --zstd \
        --extract \
        --file /path/to/backup/DATE/archive.tar.zst \
        --directory /path/to/restore

For a local archive, the archive backup contains the configured archive
directory. For a remote archive, it contains the contents of the mounted SMB
share.

Backup manifest
---------------

The ``manifest.json`` file contains metadata about the backup, including:

* the creation timestamp
* the database connection URL
* the database dump format
* the original archive directory
* the names of the backup files

The backup is first created in a temporary directory. After all files and the
manifest have been written successfully, the temporary directory is renamed to
the final timestamped directory. In case of an error, the incomplete temporary
backup is removed.
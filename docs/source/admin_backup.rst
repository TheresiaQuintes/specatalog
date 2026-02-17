Backup
======

Backup the database
-------------------

1. Open your terminal and navigate to the folder where you want to save the backup

2. Create the backup file::
	
	pg_dump -h HOST -p PORT -U USER -d specatalog -F c -f backup_$(date +%F).dump
	


You can restore the database from the backup-file if you need to::

	pg_restore -h HOST -p PORT -U USER -d neue_datenbank backup_DATE.dump



Backup the archive directory
----------------------------

You should always backup the archive directory following the backup of the database. Compress your archive folder and copy the compressed folder to an external place::

	tar -I zstd -cf backup_$(date +%F).tar.zst archive_directory/


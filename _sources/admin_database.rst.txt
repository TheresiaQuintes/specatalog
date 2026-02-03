Database administration
=======================

First setup
-----------

.. admonition:: Prerequisites

	In order to set up the database of specatalog for the first time you need a postgresql database running. If you have such a database you will need the following information:

	- HOST
	- PORT
	- USER
	- PASSWORD

	Make sure that postgresql is installed on your system e.g. via::

		sudo apt install postgresql


1. Open your terminal and log into the database::
	
	psql -h HOST -p PORT -U USER


2. Create the specatalog admin role::
	
	CREATE ROLE specatalog_admin WITH LOGIN PASSWORD 'administration_of_specatalog' CREATEDB CREATEROLE;

3. Create the database::
	
	CREATE DATABASE specatalog OWNER specatalog_admin ENCODING 'UTF8';

4. Change to the new database::
	
	\c specatalog

5. Set the permissions for the specatalog_admin. Run the commands one after the other::
	
	ALTER SCHEMA public OWNER TO specatalog_admin;
	
	GRANT USAGE, CREATE ON SCHEMA public TO specatalog_admin;

	REVOKE ALL ON DATABASE specatalog FROM PUBLIC;
	
	REVOKE CREATE ON SCHEMA public FROM PUBLIC;

6. Create your user account and run the steps 1 and 2 from the section :ref:`create-new-users`.

7. Create an empty folder where all datafiles will be organised and stored. Note the <absolute_path>.

7. Open a new terminal and download and install specatalog as described in :doc:`installation`.
	
	- username: the new user <user_name> (not the admin!)
	- password: password of the new user
	- path: <absolute_path>
	- url: <HOST>:<PORT>/specatalog

8. Copy the allowed_values.py-file to the root of the new archive-folder (run the command from the specatalog-root-folder where you have already installed specatalog)::
	
	cp ./src/specatalog/helpers/allowed_values_not_adapted.py <absolute_path>/allowed_values.py

9. Setup the database and the archive::
	
	specatalog-init-db

10. Run steps 2 (again) and 3 of the section :ref:`create-new-users` for your new user.

11. You can create new users for the members of your group. Make sure to give them username, password, the path to the archive-folder and the url of the database (see step 7).

12. Quit via::
	
	\q
	
	
.. _create-new-users:

Create new users
----------------

0. Log in to the postgresdatabase and change to specatalog::
	
	psql -h HOST -p PORT -U USER
	\c specatalog

1. Create a new database user::
	
	CREATE ROLE <user_name> WITH LOGIN PASSWORD '<password>';

2. Set permissions. Run the commands one after the other::
	GRANT CONNECT ON DATABASE specatalog TO <user_name>;
	
	GRANT USAGE ON SCHEMA public TO <user_name>;
	
	GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO <user_name>;
	
	ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO <user_name>;

3. Set DB-specific permissions. Run the commands one after the other::
	

	GRANT USAGE, SELECT, UPDATE ON SEQUENCE molecules_id_seq TO <user_name>;
	
	GRANT USAGE, SELECT, UPDATE ON SEQUENCE measurements_id_seq TO <user_name>;
	
	ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO <user_name>;

4. Exit via::
	
	\q
	


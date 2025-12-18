Database administration
=======================

- allowed_values nur admin hat schreibrechte?


PostgreSQL (lokal)
------------------

::
   sudo apt install postgresql
   sudo -u postgres psql
   
   CREATE ROLE specatalog_admin
     WITH
       LOGIN
       PASSWORD 'administration_of_specatalog'
       CREATEDB
       CREATEROLE;

   
   CREATE DATABASE specatalog
     OWNER specatalog_admin
     ENCODING 'UTF8';

   \c specatalog
   
   ALTER SCHEMA public OWNER TO specatalog_admin;
   GRANT USAGE, CREATE ON SCHEMA public TO specatalog_admin;

   REVOKE ALL ON DATABASE specatalog FROM PUBLIC;
   REVOKE CREATE ON SCHEMA public FROM PUBLIC;


   CREATE ROLE theresia
     WITH
       LOGIN
       PASSWORD 'th_pwd';
       
   GRANT USAGE ON SCHEMA public TO theresia;

   GRANT SELECT, INSERT, UPDATE, DELETE
   ON ALL TABLES IN SCHEMA public
   TO theresia;

   ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT SELECT, INSERT, UPDATE, DELETE
   ON TABLES TO theresia;


   \q



adapt in alembic.ini
--------------------
sqlalchemy.url = postgresql+psycopg2://admin:admin@localhost:5432/specatalog

adapt in main
-------------
DATABASE_URL = (
    f"postgresql+psycopg2://{USR_NAME}:{PASSWORD}@localhost:5432/specatalog"
    )

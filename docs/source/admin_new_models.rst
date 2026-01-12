Adding new models
=================

If your group uses a new method that is not implemented to specatalog you can contribute to the code and add a new Modelclass for the database.

1. Add the new Model classes to ``specatalog.models.creation_pydantic_measurements`` and ``specatalog.models.measurements``. Orient yourself at the existing models.
2. Add the new class to the mapping-dictionaries ``specatalog.crud_db.read.model_mapping_filters``, ``specatalog.crud_db.read.model_mapping_ordering`` and ``specatalog.crud_db.update.model_mapping_update``.
3. Run the following commands in the specatalog-root-folder::
	
	alembic revision --autogenerate -m "add uvvis measurement"
	alembic upgrade head

4. Give permission to write to the table to your DB-Users::
	
	sudo -u postgres psql
	\c specatalog
	GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE new_table TO db_usr;
	GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO db_usr;
	
5. Run an :doc:`update`.
6. In the documentation you have to add the new model in the files ``models.rst`` and ``crud_db.rst``.


Molecules
=========

The molecules table shall be filled with all molecules which have been measured. Therefore, the following tutorialpage focusses on the creation of molecule entries and the work with them.

Creation of a new entry
-----------------------
First of all a new entry shall be added to the molecules table.
As an example we will add anthracene and a covalently bonded pair of perylene and TEMPO.

1. Choose a group to which the molecule belongs

    Each molecule in the database has to be part of a group. Available are: radical pairs (RP), triplet-doublet pairs (TDP), triplet-triplet pairs (TTP) and all others (SingleMolecule). The chosen group decides which extra information are necessary for the entry. In our case anthracene is a **SingleMolecule**, while PER-TEMPO is a **TDP**.

2. Design and store the files with the structural formulas. 

3. Set up the MoleculeModel dependent on the chosen group from 1.

	The required fields for each group can be found in the documentation of the module :ref:`models-creation-pydantic-molecules`.::
      
		from specatlog.models import creation_pydantic_molecules as mol

		anthracene = mol.TDP(molecular_formula="C14H10",
						     name="anthracene")
						   
		per_tempo = mol.TDPModel(molecular_formula="C29H30NO",
				                 doublet = "NO1",     # name from allowed_values.py for TEMPO
				                 linker = "co",       # name from allowed_values.py for a covalent bond
				                 chromophore = "PER"  # name from allowed_values.py for perylene
				                 )  
	
	The field ``molecular_formula`` is necessary in all cases. The other fields are dependent on the group. The name for a SingleMolecule is freely choosable but should be unique. For the molecules of the other groups (which are always composed of two components) the names for the components have to be from the lists in allowed values to assure consistency. You should name your compounds systematically and add the names to the ``allowed_values.py`` as described in :doc:`tutorial_allowed_values`. The name of the molecule is then automatically build from the names of the compounds.

4. Use the function :func:`create_new_molecule <specatalog.crud_db.create.create_new_molecule>` to add the entry to the table of the database::

		from specatalog.crud_db import create
		
		anthracene_db = create.create_new_molecule(anthracene)
		per_tempo_db = create.create_new_molecule(per_tempo)

5. Use the information from the variable ``molecule_db`` to copy the structural formula files to the right directory
	
	The ``molecule`` object contains the attributes ``molecule.structural_formula`` (= relative path to the folder in the archive with the structural formulas) and ``molecule.name`` (= name of the molecule), which can be used to save the files with the structural formulas systematically::
		
		from specatalog.main import BASE_PATH
		import shutil
		
		struct_anthracene = <path/to/your/image/anthracene.cdxml>
		target_anthracene = f"{BASE_PATH}/{anthracene.structural_formula}/{anthracene.name}.cdxml"
		target_anthracene.parent.mkdir(parents=Ture, exist_ok=True)  # create directory
		shutil.copy2(struct_anthracene, target_anthracene)
		
		struct_per_tempo = <path/to/your/image/per_tempo.cdxml
		target_per_tempo = f"{BASE_PATH}/{per_tempo.structural_formula}/{per_tempo.name}.cdxml"
		target_per_tempo.parent.mkdir(parents=Ture, exist_ok=True) 
		shutil.copy2(struct_per_tempo, target_per_tempo)
		

Query molecules
---------------
It is possible to filter the database for molecules with specific properties. As an example we want to query the database for all triplet-doublet pairs with covalent linkers.

1. Set up a filter model
	
	An empty filter model includes all possible fields. You can fill the model with your desired properties. All possible FilterModels and an explanation of their fields can be found :ref:`here <crud-db-filtermodels>`.::
		
		from specatalog.crud_db import read as r
		
		covalent_linker_filter = r.TDPFilter(linker="co")

2. (Optional) Set up an ordering model
	
	If you want to sort your results you can construct an :ref:`ordering model <crud-db-orderingmodels>`, where you can choose for each parameter if the list of results shall be ordered ascending (``"asc"``) or descending (``"descending"```). An OrderingModel is not required but in our example we sort the molecules with respect to the name of the chromophore in ascending order::
		
		ordering_model = r.TDPOrdering(chromophore="asc")
	

3. Run the query using the function :func:`run_query <specatalog.crud_db.read.run_query>`.
	
	Now you can run the query and print the results. The printed results have the structure: (molecular group: name, mol_id)::
		
		results = r.run_query(covalent_linker_filter, ordering_model)
		
		print(results)  # print the list with all results
		print(results[0].id)  # print the mol_id of the first result
		print(results[0].structural_formula)  # print the path to the structural formula of the first result
	
	The function returns a list of molecule objects. You cann call the values of the attributes like the ID or the path to the structural formula.
	

Update molecules
----------------
If you have to change information on molecules it is possible to update the database entries. As an example you have for mistake commited the wrong structural formula to the database for the molecule with the mol_id=3 and would like to correct the entry.

1. Load the molecule
	
	We will load the entry with the ID=3 by querying the database for the molecule with id=1 and choosing the first (and only) result from the list.::
	
		from specatalog.crud_db import read as r
		mol_3 = r.run_query(r.MoleculeFilter(id=3))[0]  

2. Build an update filter
	
	Analoguos to the models for filtering :ref:`UpdateModels <crud-db-updatemodels>` exist. Each attribute of an object of the class UpdateModel can be set to a new attribute (of the correct type)::
	
		from specatalog.crud_db import update as up
		update_mol_form = up.MoleculeUpdate(molecular_formula="corrected formula"

3. Update the database entry by using the function :func:`update_model <specatalog.crud_db.update.update_model>`.::
	
	up.update_model(mol_3, update_mol_form)
	
.. note::

	In case of molecules consisting of two compounds the name-property is updated automatically if the name of one or more of the compounds changes.
	
Delete molecules
----------------

.. danger::
	
	It is possible to delete molecules using the function :func:`delete_molecule <specatalog.crud_db.delete.delete_molecule>`. But it is not advised to do so! If you delete a molecule entry from a database **all** measurements which are assigned to this molecule will be also deleted. If you have to delete a molecule don't forget to delete the corresponding folder in the archive directory aswell.



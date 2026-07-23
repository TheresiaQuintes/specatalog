Installation and Setup
======================

.. admonition:: Requirements for installation

   - Python 3.11 installation
   - pip
   - Open a terminal
   
   - Make sure that your database admin has given you the following information: username, password and the url of the database.
   - If you want to use a remote archive you will further need: address of the server (open SMB-port), share-path, username and password



#. Optional but recommended: Create and activate a virtual environment

    - via python-venv::

          python -m venv ./.specatalog_venv
          source ./.specatalog_venv/bin/activate

    - via anaconda::

          conda create -n specatalog_venv python=3.11
          conda activate specatalog_venv
 
#. Install the package

    Use pip::

          pip install specatalog

    Alternatively: Clone the repository from GitHub::

          git clone https://github.com/TheresiaQuintes/specatalog.git

    Navigate into the cloned directory::

          cd specatalog

    Install the package via pip::

          pip install .

#. Configure your database::

	  specatalog-configuration


#. Only if no archive-folder and no database exist::

    specatalog-init

#. Only if no archive-folder exists and the database exists::

    specatalog-init-dir

#. Check the installation::

      specatalog-welcome

.. admonition:: What's next?
	
	After the installation and setup of specatalog you have the initial archive directory and an empty database file. Now it is recommended to read the tutorial. Here, you will learn how to use this base structure with the help of specatalogs functions and classes using a script. If you like to follow the step-by-step instructions you should have an empty python-script open in an IDE of your choice (if automatic code completion is supported, things get easier).

.. tip::
	
	A GUI is available via::
	
		specatalog-gui

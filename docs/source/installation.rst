Installation and Setup
======================

.. admonition:: Requirements for installation

   - Python 3.11 installation
   - pip
   - Open a terminal

1. Clone the repository from GitHub::

      git clone https://github.com/TheresiaQuintes/specatalog.git

2. Navigate into the cloned directory::

      cd specatalog

3. Optional but recommended: Create and activate a virtual environment

- via python-venv::

      python -m venv ./.specatalog_venv
      source ./.specatalog_venv/bin/activate
      
- via anaconda::
	  
	  conda create -n specatalog_venv python=3.11
	  conda activate specatalog_venv
 
4. Install the package via pip::

      pip install .

5. Check the installation::
     
      specatalog-welcome

6. Configure your database by defining a root-path for your archive folder and a username/password::

	  specatalog-configuration


7. Only if the archive directory and the database do **not** exist run::

      specatalog-init-db



.. admonition:: What's next?
	
	After the installation and setup of specatalog you have the initial archive directory and an empty database file. Now it is recommended to read the tutorial. Here, you will learn how to use this base structure with the help of specatalogs functions and classes using a script. If you like to follow the step-by-step instructions you should have an empty python-script open in an IDE of your choice (if automatic code completion is supported, things get easier).

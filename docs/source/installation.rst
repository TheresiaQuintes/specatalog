Installation and Setup
======================

.. admonition:: Requirements for installation

   - Python3 installation
   - pip
   - Open a terminal

1. Clone the repository from GitHub::

      git clone https://github.com/TheresiaQuintes/specatalog.git

2. Navigate into the cloned directory::

      cd specatalog

3. Optional but recommended: Create and activate a virtual environment::

      python -m venv ./.specatalog_venv
      source ./.specatalog_venv/bin/activate
 
4. Install the package via pip::

      pip install .

5. Check the installation::
     
      specatalog-welcome

6. Adapt the defaults file at: ``~/.specatalog/defaults.json`` and add the absoute path to the archive directory to ``base_path``. You can check the changes via ``specatalog-welcome``.


7. Only if the archive directory and the database do **not** exist run::

      specatalog-init-db



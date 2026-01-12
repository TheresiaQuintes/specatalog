models
======

The package models includes all modules that describe the SQLAlchemy classes for the tables in the database and the Pydantic-classes that are used for the creation of new entries.


base
----
.. currentmodule:: specatalog.models.base

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst

   TimeStampedModel

.. _models-measurements:

measurements
------------
.. currentmodule:: specatalog.models.measurements

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst

   Measurement
   CWEPR
   TREPR
   PulseEPR
   UVVis
   Fluorescence
   TA
   

.. _models-creation-pydantic-measurements:

creation_pydantic_measurements
------------------------------
.. currentmodule:: specatalog.models.creation_pydantic_measurements

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst

   MeasurementModel
   CWEPRModel
   TREPRModel
   PulseEPRModel
   UVVisModel
   FluorescenceModel
   TAModel


.. _models-molecules:

molecules
---------
.. currentmodule:: specatalog.models.molecules

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst

   Molecule
   SingleMolecule
   RP
   TDP
   TTP


.. _models-creation-pydantic-molecules:

creation_pydantic_molecules
---------------------------
.. currentmodule:: specatalog.models.creation_pydantic_molecules

.. autosummary::
   :toctree: generated/
   :recursive:
   :nosignatures:
   :template: class_docstring_only.rst

   MoleculeModel
   SingleMoleculeModel
   RPModel
   TDPModel
   TTPModel

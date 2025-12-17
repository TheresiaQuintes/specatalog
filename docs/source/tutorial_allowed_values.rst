Allowed values
==============

In the root folder of the archive directory the file ``allowed_values.py`` is created. This file creates classes that generate the permitted values for specific columns in the database in order to keep them consistent and enable searchability for specific terms.
For example, uniform abbreviations should always be used for chromophores, or water as a solvent should always be referred to as "water" and not "H20".

This file is placed in the root of the archive directory in order to make it available to all users. The file should be adapted once by the admin in the beginning to set the initial values. Later all members of the team may add allowed values to the classes. For example, a new chormophore is measured or a new solvent is used.

.. danger::
	
	Existing values should never be deleted or changed, as this would result in inconsistencies in the database!

The syntax of a class is as follows::

	class ClassName(str, Enum):
		allowed_value_1 = "allowed_value_1"
		allowed_value_2 = "allowed_value_2"
		allowed_value_n = "allowed_value_n"

The string name is the value that can be added to the database as an attribute.

The following classes exist:

.. list-table:: Allowed values classes
   :header-rows: 1
   :widths: 30 100

   * - Class
     - Used for
   * - Names
     - ``measured_by`` attribute in the ``Measurement`` class.
        Add the names of your team.
   * - Solvents
     - ``solvent`` attribute in the ``Measurement`` class.
     	Add all solvents used.
   * - Devices
     - ``device`` attribute in the ``Measurement`` class. 
     	Add abbreviations for your measuring devices.
   * - FrequencBands
     - ``frequency_band`` attribute in all ``EPR`` classes. 
     	Add the letter of the frequency band used.
   * - PulseExperiments
     - ``pulse_experiment`` attribute in the ``PulseEPR`` class. 
     	Add abbreviations for the names of pulse experiments.
   * - Chromophores
     - ``chromophore`` attribute in the ``TDP`` and ``TTP`` classes. 
     	Add a systematic nomenclature for the chromophores of the molecules
     	
     	in your measurements.
   * - Doublets
     - ``doublet`` attribute in the ``TDP`` class. 
     	Add a systematic nomenclature for the doublets of the molecules
     	
     	in your measurements.
   * - Linker
     - ``linker`` attribute in the ``TDP``, ``TTP`` and ``RP`` classes. 
     	Add a systematic nomenclature for the linkers of the molecules
     	
     	in your measurements. You may also define "linker" names for
     	
     	molecules that are covalently linked without a linker,
     	
     	or that are linked by supramolecular interactions.
   * - Radicals
     - ``radical`` attribute in the ``RP`` class.
     	Add a systematic nomenclature for the radicals of the molecules
     	
     	in your measurements.

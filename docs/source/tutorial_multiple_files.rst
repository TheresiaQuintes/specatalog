Workflow: Multiple Raw Data Measurements
========================================

This tutorial demonstrates how to create a measurement entry, import multiple raw
data files belonging to the same experiment, and attach processed datasets to the
corresponding HDF5 file. The workflow is shown for multiple bruker_bes3t format
files. The script is only exemplary and can be adapted for other formats or name
conventions.

The workflow is controlled by several switches, allowing the same script to be
used for creating new measurements as well as extending existing entries.

Workflow switches
-----------------

At the beginning of the script, the following options define which parts of the
workflow are executed::

    create = True
    multidata = True
    corrected_data = True
    log = False
    origin = False
    manual_id = 45


#. ``create``

    Controls whether a new measurement entry is created.

    * `True`: Creates a new database entry, imports the first raw data file, and
      creates the HDF5 file.
    * `False`: No new entry is created. The existing measurement defined by
      `manual_id` is used instead.

#. ``corrected_data``

    Controls importing processed datasets.

    * `True`: Processed files (`.dat` files) are loaded and stored
      in the `corrected_data` section of the HDF5 file.
    * `False`: No processed data are imported.

#. ``log``

    Controls importing processing parameters from a log file.

    * `True`: Values stored as `parameter = value` in a `.log` file are added
      as HDF5 attributes.
    * `False`: Log files are ignored.

#. ``origin``

    Controls importing Origin-exported datasets.

    * `True`: Columns from an Origin text export are stored as individual datasets
      in the HDF5 file.
    * `False`: Origin files are ignored.

#. ``manual_id``

    Defines the measurement ID used when `create=False`.

    In this case, the workflow modifies measurement entry with the given ID instead of
    creating a new measurement.

Creating the database measurement
---------------------------------

The first step is to define the measurement metadata using the corresponding
Pydantic model. In this example, a trEPR measurement is created::
    from datetime import date
    import numpy as np
    from pathlib import Path
    from specatalog.models import creation_pydantic_measurements as ms
    from specatalog.helpers.full_entry import create_full_measurement
    from specatalog.main import BASE_PATH
    import specatalog.data_management.measurement_management as mm
    from specatalog.data_management.hdf5_reader import load_from_id

    measurement_model = ms.TREPRModel(
        molecular_id=31,
        temperature=80,
        solvent="toluene",
        date=date(2026, 4, 3),
        measured_by="redman",
        location="freiburg",
        series="nmis",
        corrected=True,
        frequency_band="x",
        excitation_wl=355,
        excitation_energy=0.8,
        attenuation="20dB",
    )

If ``create=True``, the measurement entry and the raw datasets are created
using::

    raw_data = [p.with_suffix("") for p in Path("/path/to/folder/with/raw/data").glob("*.DSC")]

    new_measurement_created = create_full_measurement(
        measurement_model,
        BASE_PATH,
        raw_data
        fmt="bruker_bes3t",
    )

This function creates the database entry, creates the corresponding measurement
directory and HDF5 file, and imports all raw data files.

The measurement ID is stored for all following operations::

    if create:
        ms_id = new_measurement_created.measurement_id
    else:
        ms_id = manual_id


Adding processed datasets
-------------------------

Processed data can be stored in the same HDF5 file as the raw data.

The existing measurement file is opened and all processed data files are loaded
and added as datasets. This part of the code has to be adapted to your personal
needs (e.g. file format / file structure/ file name). Make sure that loading
of the right data works properly::

    dat_files = [
        str(f.resolve())
        for f in Path(raw_data_path).glob("*.dat")
    ]

    if corrected_data:
        d, file = load_from_id(ms_id)

        All processed data files are loaded and added as datasets:

        for file_name in dat_files:
            set_name = file_name.split("__")[-1].split(".")[0]
            data = np.loadtxt(file_name)

            d.corrected_data.set_dataset(
                set_name,
                data,
            )

    d.sync()
    file.close()

The dataset name is generated from the filename, allowing multiple processed
datasets to be stored within the same measurement.

Adding processing parameters
----------------------------

If a processing log file is available, its parameters can also be stored.

The script reads all entries in the form parameter=value and stores them as
HDF5 attributes::

    if log:
        d, file = load_from_id(ms_id)
        log_files = list(Path(raw_data_path).glob("*.log"))

        if len(log_files) != 1:
            raise ValueError(
                f"There are {len(log_files)} .log-files in your folder. Exactly one is expected."
            )

        log_file = str(log_files[0].resolve())
        with open(log_file) as f:
            for line in f.readlines():
                if "=" in line:
                    key, value = line.split("=")

                    d.corrected_data.set_attr(
                        key.strip(),
                        value.strip(),
                    )

This keeps processing information together with the corresponding datasets.

Adding supplementary analysis files
-----------------------------------

The workflow stores raw data, processed data, and metadata automatically.
Additional files such as analysis scripts, notebooks, figures, or fitting
results can be copied manually into the measurement directory.

Keeping these files together ensures that the complete analysis workflow
remains reproducible.

Complete workflow
-----------------

A typical workflow therefore consists of the following steps:

#. Define the measurement metadata.
#. Create the measurement entry and import the raw datasets.
#. Import processed datasets into the HDF5 file.
#. Store processing parameters if available.
#. Add supplementary analysis files.

The result is a single Specatalog measurement entry containing the complete
experimental information: raw data, processed data, metadata, and analysis
files.

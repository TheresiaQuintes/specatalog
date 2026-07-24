import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from specatalog.crud_db import read as r
from specatalog.data_management import hdf5_reader as hf
from specatalog.data_management import measurement_management as mm


measurement_id = 1

with hf.load_from_id(measurement_id, mode="a") as (dat, h5_file):
    # Datensätze aus der HDF5-Datei laden.
    # Für Bruker-BES3T-Daten werden die Datensätze nummeriert gespeichert.
    x = dat.raw_data.xaxis_0
    intensity_real = dat.raw_data.data_real_0
    intensity_imag = dat.raw_data.data_imag_0

    fit = -2 * (x - 12000) ** 2 + 25000

    fig, ax = plt.subplots()

    ax.plot(x, np.real(intensity_real), label="Real part")
    ax.plot(x, np.real(intensity_imag), label="Imaginary part")
    ax.plot(x, fit, label="Fit")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Intensity")
    ax.legend()
    fig.tight_layout()

    # Fit im HDF5-File speichern
    dat.evaluations.set_dataset("fit_1", fit)
    dat.sync()

    # Abbildung zunächst lokal speichern
    with tempfile.TemporaryDirectory() as temp_dir:
        local_figure = Path(temp_dir) / f"fit_{measurement_id}.pdf"
        fig.savefig(local_figure)

        # Abbildung in das Archiv unter figures/ kopieren
        mm.new_file_to_archive(
            src=local_figure,
            ms_id=measurement_id,
            category="figures",
            update=True,
        )

    plt.close(fig)
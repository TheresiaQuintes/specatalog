from specatalog.models import creation_pydantic_measurements as ms
from datetime import date
from specatalog.crud_db import create
import specatalog.data_management.measurement_management as mm


def create_measurement_with_raw_data(
    measurement_data,
    raw_data_path: str,
    fmt: str = "bruker_bes3t",
):
    """Create a database entry and archive the corresponding raw data."""

    measurement = create.create_new_measurement(measurement_data)

    try:
        mm.create_measurement_dir(measurement.id)
        mm.raw_data_to_folder(
            raw_data_path=raw_data_path,
            fmt=fmt,
            ms_id=measurement.id,
        )
        mm.raw_data_to_hdf5(
            ms_id=measurement.id,
            fmt=fmt,
        )

    except Exception:
        # Remove the database entry if the archive operation fails.
        create.delete_measurement(measurement.id)
        raise

    return measurement


# CW-EPR
raw_data = (
    "/home/quintes/Downloads/pdihtzetempo/"
    "01_Q_Bsw_PDI-H-TZ-eTEMPO_tol_dark_9dB_VG12_n2h4_80K"
)

new_measurement = ms.CWEPRModel(
    molecular_id=1,
    temperature=80.0,
    solvent="toluene",
    date=date(2024, 3, 4),
    measured_by="maylaender",
    device="elexsys",
    frequency_band="q",
    attenuation="9 dB",
    corrected=False,
    evaluated=False,
)

measurement = create_measurement_with_raw_data(
    measurement_data=new_measurement,
    raw_data_path=raw_data,
    fmt="bruker_bes3t",
)

print(f"CW-EPR measurement created: M{measurement.id}")

# trEPR
raw_data = (
    "/home/quintes/Downloads/pdihtzetempo/"
    "20_Q_trEPR_PDI-H-TZ-eTEMPO_tol_530nm_05mJ_20dB_gain5_av100_80K"
)

new_measurement = ms.TREPRModel(
    molecular_id=1,
    temperature=80.0,
    solvent="toluene",
    date=date(2024, 3, 4),
    measured_by="maylaender",
    device="elexsys",
    frequency_band="q",
    excitation_wl=530.0,
    attenuation="20 dB",
    corrected=False,
    evaluated=False,
)

measurement = create_measurement_with_raw_data(
    measurement_data=new_measurement,
    raw_data_path=raw_data,
    fmt="bruker_bes3t",
)

print(f"trEPR measurement created: M{measurement.id}")

# Pulsed EPR
raw_data = (
    "/home/quintes/Downloads/pdihtzetempo/"
    "26_Q_Esenut_PDI-H-TZ-eTEMPO_tol_530nm_05mJ_15dB_"
    "VG12_n3h4_80K_11880G"
)

new_measurement = ms.PulseEPRModel(
    molecular_id=1,
    temperature=80.0,
    solvent="toluene",
    date=date(2024, 3, 5),
    measured_by="maylaender",
    device="elexsys",
    frequency_band="q",
    pulse_experiment="esenut",
    attenuation="15 dB",
    excitation_wl=530.0,
    corrected=False,
    evaluated=False,
)

measurement = create_measurement_with_raw_data(
    measurement_data=new_measurement,
    raw_data_path=raw_data,
    fmt="bruker_bes3t",
)

print(f"Pulsed-EPR measurement created: M{measurement.id}")

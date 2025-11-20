from models import creation_pydantic_measurements as ms
from datetime import date
from crud_db import create
import data_management.measurement_management as mm
from main import MEASUREMENTS_PATH, BASE_PATH

ms_path = BASE_PATH / MEASUREMENTS_PATH

raw_data = "/home/quintes/Downloads/pdihtzetempo/01_Q_Bsw_PDI-H-TZ-eTEMPO_tol_dark_9dB_VG12_n2h4_80K"
new_measurement = ms.CWEPRModel(molecular_id=1,
                                temperature=80,
                                solvent="toluene",
                                date=date(2024, 3, 4),
                                measured_by="maylaender",
                                device="ELEXSYS",
                                frequency_band="Q",
                                attenuation="9dB")

measurement = create.create_new_measurement(new_measurement)


mm.create_measurement_dir(ms_path, measurement.id)
mm.new_raw_data_to_folder(ms_path, measurement.id, raw_data, "bruker_bes3t")
mm.new_raw_data_to_hdf5(ms_path, measurement.id)



# %%
raw_data = "/home/quintes/Downloads/pdihtzetempo/20_Q_trEPR_PDI-H-TZ-eTEMPO_tol_530nm_05mJ_20dB_gain5_av100_80K"
new_measurement = ms.TREPRModel(molecular_id=1,
                                temperature=80,
                                solvent="toluene",
                                date=date(2024, 3, 4),
                                measured_by="maylaender",
                                device="ELEXSYS",
                                frequency_band="Q",
                                attenuation="20dB",
                                excitation_wl=530)

measurement = create.create_new_measurement(new_measurement)


mm.create_measurement_dir(ms_path, measurement.id)
mm.new_raw_data_to_folder(ms_path, measurement.id, raw_data, "bruker_bes3t")
mm.new_raw_data_to_hdf5(ms_path, measurement.id)


# %%
raw_data = "/home/quintes/Downloads/pdihtzetempo/26_Q_Esenut_PDI-H-TZ-eTEMPO_tol_530nm_05mJ_15dB_VG12_n3h4_80K_11880G"
new_measurement = ms.PulseEPRModel(molecular_id=1,
                                temperature=80,
                                solvent="toluene",
                                date=date(2024, 3, 5),
                                measured_by="maylaender",
                                device="ELEXSYS",
                                frequency_band="Q",
                                pulse_experiment="esenut")

measurement = create.create_new_measurement(new_measurement)


mm.create_measurement_dir(ms_path, measurement.id)
mm.new_raw_data_to_folder(ms_path, measurement.id, raw_data, "bruker_bes3t")
mm.new_raw_data_to_hdf5(ms_path, measurement.id)

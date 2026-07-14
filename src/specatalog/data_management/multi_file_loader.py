import measurement_management as mm
from specatalog.main import BASE_PATH


def multiple_files_to_folder(list_raw_data, fmt, ms_id):
    for entry in list_raw_data:
        mm.raw_data_to_folder(entry, fmt, BASE_PATH, ms_id)

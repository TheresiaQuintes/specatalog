import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import specatalog.data_management.measurement_management as mm
import specatalog.crud_db.create as cr
from specatalog.main import Session
session = Session()


@dataclass
class CreateMeasurementResult:
    success: bool
    measurement_id: Optional[int] = None
    error: Optional[Exception] = None

def _create_temp_measurement_dir(base_dir: str):
    """
    Erzeugt temporäres Verzeichnis für Measurement.
    """
    path = Path(base_dir) / "data"
    temp_dir = Path(tempfile.mkdtemp(dir=path))
    return temp_dir

def _commit_measurement_dir(temp_root: Path, base_dir: Path, ms_id: int):
    """
    Verschiebt nur data/M{ms_id} aus dem Temp-Verzeichnis
    in das finale Archivverzeichnis.
    """
    temp_measurement_dir = temp_root / "data" / f"M{ms_id}"
    final_measurement_dir = base_dir / "data" / f"M{ms_id}"

    # Elternordner sicherstellen
    final_measurement_dir.parent.mkdir(parents=True, exist_ok=True)

    # atomar verschieben (innerhalb desselben Filesystems!)
    temp_measurement_dir.rename(final_measurement_dir)

    # optional: leeres temp_root aufräumen
    shutil.rmtree(temp_root)




def create_full_measurement(data, base_dir, raw_data_path, fmt):
    """
    Führt alle Schritte atomar aus:
    1) DB-Eintrag
    2) Measurement-Ordner
    3) raw_data_to_folder
    4) raw_data_to_hdf5
    """
    temp_dir = None
    try:
        with session.begin():
            measurement = cr.create_new_measurement(data, transaction=True)

            temp_dir = _create_temp_measurement_dir(base_dir)
            mm.create_measurement_dir(temp_dir, measurement.id)
            mm.raw_data_to_folder(raw_data_path, fmt, temp_dir, measurement.id)
            mm.raw_data_to_hdf5(temp_dir, measurement.id, fmt)

        _commit_measurement_dir(temp_dir, base_dir, measurement.id)

        return CreateMeasurementResult(success=True,
                                       measurement_id=measurement.id)

    except Exception as e:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)

        return CreateMeasurementResult(success=False,
                                       error=e)

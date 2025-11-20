from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Type, Optional
import models.measurements as ms
import datetime

from main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)

class MeasurementModel(BaseModel):
    molecular_id: int
    temperature: float = Field(..., gt=0)
    solvent: av.Solvents
    concentration: Optional[str]=None
    date: datetime.date
    measured_by : av.Names
    location: Optional[str]=None
    device: Optional[av.Devices]=None
    series: Optional[str]=None
    corrected: bool=False
    evaluated: bool=False

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class CWEPRModel(MeasurementModel):
    measurement_class: Type=ms.CWEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.CWEPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: av.FrequencyBands
    attenuation: str


class TREPRModel(MeasurementModel):
    measurement_class: Type=ms.TREPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.TREPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: av.FrequencyBands
    excitation_wl: float
    excitation_energy: Optional[float]=None
    attenuation: str
    number_of_scans: Optional[int]=None
    repetitionrate: Optional[float]=None
    mode: Optional[str]=None


class PulseEPRModel(MeasurementModel):
    measurement_class: Type=ms.PulseEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.PulseEPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: Optional[av.FrequencyBands]=None
    attenuation: Optional[str]=None
    excitation_wl: Optional[float]=None
    pulse_experiment: av.PulseExperiments

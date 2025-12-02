from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Type, Optional
import specatalog.models.measurements as ms
import datetime

from specatalog.main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)


class MeasurementModel(BaseModel):
    """
    Pydantic data model for creating new :class:`ms.Measurement` entries.

    This model defines the validated input structure used by the application
    to create SQLAlchemy ``Measurement`` instances. Only the minimal and
    user-provided metadata are included here; database-managed fields such as
    ``id`` or timestamps are not part of this schema.

    Attributes
    ----------
    molecular_id : int
        Foreign key referring to the associated molecule.
    temperature : float
        Measurement temperature in Kelvin; must be strictly positive.
    solvent : av.Solvents
        Enumeration specifying the solvent used during the measurement.
    concentration : str or None
        Optional textual concentration information (units or descriptive label).
    date : datetime.date
        Date on which the measurement was performed.
    measured_by : av.Names
        Enumeration specifying who performed the experiment.
    location : str or None
        Optional description of the laboratory or facility.
    device : av.Devices or None
        Optional enumeration indicating the device used for data acquisition.
    series : str or None
        Optional series or batch label for grouping related measurements.
    corrected : bool
        Whether the measurement has been baseline- or artefact-corrected.
    evaluated : bool
        Whether the measurement has been analysed or processed.

    Notes
    -----
    * Additional fields are forbidden (``extra='forbid'``).
    * Assignment is validated on set (``validate_assignment=True``).

    """
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
    """
    Pydantic model for creating new :class:`ms.CWEPR` measurements.

    This subclass of :class:`MeasurementModel` adds cwEPR-specific fields
    required to create a continuous-wave EPR measurement in the database.
    The ``measurement_class`` attribute is fixed to :class:`ms.CWEPR` and
    cannot be changed.

    Attributes
    ----------
    measurement_class : Type
        Always set to :class:`ms.CWEPR`. Attempting to assign a different class
        raises a validation error.
    frequency_band : av.FrequencyBands
        Microwave frequency band used for the CW-EPR measurement (e.g. ``X``).
    attenuation : str
        Microwave attenuation setting applied during acquisition.

    Notes
    -----
    * Additional fields are forbidden (``extra='forbid'``).
    * Assignment is validated on set (``validate_assignment=True``).
    * All further attributes are inherited from :class:`MeasurementModel`.

    """
    measurement_class: Type=ms.CWEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.CWEPR:
            raise ValueError("measurement_class must not be changed.")
        return v

    frequency_band: av.FrequencyBands
    attenuation: str


class TREPRModel(MeasurementModel):
    """
    Pydantic model for creating new :class:`ms.TREPR` measurements.

    This subclass of :class:`MeasurementModel` adds TREPR-specific fields
    required to create a time-resolved EPR measurement in the database.
    The ``measurement_class`` attribute is fixed to :class:`ms.TREPR` and
    cannot be changed.

    Attributes
    ----------
    measurement_class : Type
        Always set to :class:`ms.TREPR`. Attempting to assign a different class
        raises a validation error.
    frequency_band : av.FrequencyBands
        Microwave frequency band used for the TREPR experiment.
    excitation_wl : float
        Excitation wavelength in nanometres.
    excitation_energy : float or None
        Excitation energy in appropriate units; optional.
    attenuation : str
        Microwave attenuation setting.
    number_of_scans : int or None
        Number of scans acquired; optional.
    repetitionrate : float or None
        Repetition rate of the experiment; optional.
    mode : str or None
        Experimental mode descriptor; optional.

    Notes
    -----
    * Additional fields are forbidden (``extra='forbid'``).
    * Assignment is validated on set (``validate_assignment=True``).
    * All further attributes are inherited from :class:`MeasurementModel`.

    """
    measurement_class: Type=ms.TREPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.TREPR:
            raise ValueError("measurement_class must not be changed.")
        return v

    frequency_band: av.FrequencyBands
    excitation_wl: float
    excitation_energy: Optional[float]=None
    attenuation: str
    number_of_scans: Optional[int]=None
    repetitionrate: Optional[float]=None
    mode: Optional[str]=None


class PulseEPRModel(MeasurementModel):
    """
    Pydantic model for creating new :class:`ms.PulseEPR` measurements.

    This subclass of :class:`MeasurementModel` adds Pulse-EPR-specific fields
    required to create a pulsed EPR measurement in the database.
    The ``measurement_class`` attribute is fixed to :class:`ms.PulseEPR` and
    cannot be changed.

    Attributes
    ----------
    measurement_class : Type
        Always set to :class:`ms.PulseEPR`. Attempting to assign a different
        class raises a validation error.
    pulse_experiment : av.PulseExperiments
        Type of pulsed EPR experiment (e.g., PELDOR, TN, ...).
    frequency_band : av.FrequencyBands or None
        Microwave frequency band used; optional.
    attenuation : str or None
        Microwave attenuation setting; optional.
    excitation_wl : float or None
        Excitation wavelength in nanometres; optional.

    Notes
    -----
    * Additional fields are forbidden (``extra='forbid'``).
    * Assignment is validated on set (``validate_assignment=True``).
    * All further attributes are inherited from :class:`MeasurementModel`.

    """
    measurement_class: Type=ms.PulseEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.PulseEPR:
            raise ValueError("measurement_class must not be changed.")
        return v

    frequency_band: Optional[av.FrequencyBands]=None
    attenuation: Optional[str]=None
    excitation_wl: Optional[float]=None
    pulse_experiment: av.PulseExperiments

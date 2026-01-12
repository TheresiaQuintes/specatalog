from specatalog.models.base import TimeStampedModel

from sqlalchemy import Column, Integer, ForeignKey, String, Float,  Date, Text, Boolean
from sqlalchemy.orm import Relationship
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from specatalog.main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)



class Measurement(TimeStampedModel):
    """
    Base class representing a single measurement.

    This model defines the core metadata shared by all measurement types in the
    system (e.g., TREPR, CWEPR, PulseEPR). It serves as the root of a
    polymorphic SQLAlchemy hierarchy, with ``method`` acting as the
    discriminator. Subclasses inherit these fields and may define additional,
    technique-specific information.

    The measurement belongs to exactly one :class:`Molecule` instance, and
    contains essential experiment metadata.

    Polymorphism
    ------------
    SQLAlchemy polymorphic behaviour is used to distinguish different
    measurement techniques:

    * ``polymorphic_on`` – the ``method`` column
    * ``polymorphic_identity`` – ``"base"`` for this class

    Subclasses should set their own ``polymorphic_identity`` value.

    Relationships
    -------------
    molecule : Molecule
        The molecule to which the measurement belongs. Configured as a required
        foreign key with cascade delete behaviour.

    Attributes
    ----------
    id : int
        Primary key identifying the measurement.
    molecular_id : int
        Foreign key referencing ``molecules.id``. Required.
    method : str
        Polymorphic discriminator describing the measurement technique (e.g.,
        ``"trepr"``, ``"cwepr"``, ``"pulse_epr"``).
    temperature : float
        Measurement temperature in Kelvin (or laboratory-specific units).
    solvent : Solvents
        Solvent used in the experiment. Enum from ``allowed_values.Solvents``.
    concentration : str or None
        Concentration of the sample, if provided.
    date : datetime.date
        Date on which the measurement was performed.
    measured_by : Names
        The operator who performed the measurement. Enum from
        ``allowed_values.Names``.
    location : str or None
        Laboratory or instrument location of the measurement.
    device : Devices or None
        Device/instrument identifier. Enum from ``allowed_values.Devices``.
    series : str or None
        Optional series identifier grouping related measurements.
    path : str
        Absolute path to the associated measurement directory in the archive.
        Must be unique.
    corrected : bool
        ``True`` if the measurement has been corrected.
    evaluated : bool
        ``True`` if the measurement has been analysed.

    Notes
    -----
    * The tablename is ``measurements``
    * All measurement subclasses inherit timestamps
      from :class:`TimeStampedModel`.
    * The ``path`` field is unique, ensuring that individual measurements are
      not duplicated.

    Examples
    --------
    Creating a measurement:

    >>> from measurements import Measurement
    >>> from molecules import Molecule
    >>> mol = Molecule(...)
    >>> m = Measurement(
    ...     molecule=mol,
    ...     method="TREPR",
    ...     temperature=295.0,
    ...     solvent="Toluene",
    ...     date=date(2025, 1, 4),
    ...     measured_by="Alice",
    ...     path="/data/M12/",
    ...     corrected=False,
    ...     evaluated=False,
    ... )
    >>> session.add(m)
    >>> session.commit()
    """
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # molecule
    molecular_id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                              nullable=False, index=True)
    molecule = Relationship("Molecule", back_populates="measurements")

    # method
    method = Column(String(64), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": method,
        "polymorphic_identity": "base",
        }

    # metadata
    temperature = Column(Float, nullable=False)
    solvent = Column(SAEnum(av.Solvents), nullable=False)
    concentration = Column(String(512))
    date = Column(Date, nullable=False)
    measured_by = Column(SAEnum(av.Names), nullable=False)
    location = Column(String(512))
    device = Column(SAEnum(av.Devices))
    series = Column(String(512))
    path = Column(Text, nullable=False, unique=True)
    corrected = Column(Boolean, nullable=False)
    evaluated = Column(Boolean, nullable=False)


    def __repr__(self):
        return f"(M{self.id}: {self.__class__.__name__}; {self.molecule.name})"



class TREPR(Measurement):
    """
    Time-resolved electron paramagnetic resonance (trEPR) measurement.

    This subclass of :class:`Measurement` describes a trEPR experiment.
    The class extends the base measurement metadata by adding method-specific
    parameters such as excitation wavelength, microwave frequency band,
    and repetition rate.

    The model participates in the SQLAlchemy polymorphic hierarchy using
    ``"trepr"`` as its ``polymorphic_identity``. Database rows with
    ``method='trepr'`` will therefore be loaded as :class:`TREPR` objects.

    Attributes
    ----------
    id : int
        Primary key bound to the underlying entry in ``measurements``.
    frequency_band : FrequencyBands
        Microwave frequency band used for detection (e.g., X-band, Q-band).
        Enum provided by ``allowed_values.FrequencyBands`` e.g. ``X`` or ``Q``.
    excitation_wl : float
        Laser excitation wavelength in nanometres.
    excitation_energy : float or None
        Pulse energy of the excitation source, typically in microjoules.
    attenuation : str
        Microwave attenuation setting used during acquisition.
    number_of_scans : int or None
        Number of accumulated scans used for signal averaging.
    repetitionrate : float or None
        Laser repetition rate in Hertz.
    mode : str or None
        Optional acquisition mode or instrument configuration string.

    Notes
    -----
    * The tablename is ``trepr``
    * All generic attributes such as temperature, solvent, operator, path,
      and timestamps are inherited from :class:`Measurement`.

    Examples
    --------
    Creating a TREPR measurement:

    >>> from measurements import TREPR
    >>> from molecules import Molecule
    >>> mol = Molecule(name="PDI-Br")
    >>> m = TREPR(
    ...     molecule=mol,
    ...     method="trepr",
    ...     temperature=298.0,
    ...     solvent="Toluene",
    ...     date=date(2025, 2, 15),
    ...     measured_by="Alice",
    ...     path="/data/M42",
    ...     corrected=False,
    ...     evaluated=False,
    ...     frequency_band="X",
    ...     excitation_wl=532.0,
    ...     excitation_energy=25.0,
    ...     attenuation="20 dB",
    ...     number_of_scans=100,
    ...     repetitionrate=1000.0,
    ...     mode="FID"
    ... )
    >>> session.add(m)
    >>> session.commit()

    Polymorphic loading:

    >>> m = session.query(Measurement).filter_by(id=42).one()
    >>> type(m)
    <class 'models.TREPR'>
    """
    __tablename__ = "trepr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "trepr",}

    frequency_band = Column(SAEnum(av.FrequencyBands), nullable=False)
    excitation_wl = Column(Float, nullable=False)
    excitation_energy = Column(Float)
    attenuation = Column(String(32), nullable=False)
    number_of_scans = Column(Integer)
    repetitionrate = Column(Float)
    mode = Column(String(128))



class CWEPR(Measurement):
    """
    Continuous-wave electron paramagnetic resonance (cw-EPR) measurement.

    This subclass of :class:`Measurement` represents a continuous-wave EPR
    experiment. This model adds method-specific parameters such as
    microwave frequency band and attenuation, while all general metadata
    (temperature, solvent, operator, timestamps, etc.) are inherited from
    :class:`Measurement`.

    The model participates in SQLAlchemy polymorphism using the
    ``"cwepr"`` ``polymorphic_identity``. Any row in ``measurements`` where
    ``method='cwepr'`` will therefore be loaded as a :class:`CWEPR` instance.

    Attributes
    ----------
    id : int
        Primary key linked to ``measurements.id`` with cascading delete.
    frequency_band : FrequencyBands
        Microwave frequency band used for the CW-EPR measurement (e.g. X-band).
        Enum defined in ``allowed_values.FrequencyBands``, e.g. ``X``.
    attenuation : str
        Microwave attenuation setting applied during signal acquisition.

    Notes
    -----
    * The tablename is ``cwepr``
    * All shared metadata fields are inherited and documented in
      :class:`Measurement`.
    * The ``id`` of a :class:`CWEPR` object corresponds directly to the
      associated row in the main ``measurements`` table.

    Examples
    --------
    Creating a CW-EPR measurement:

    >>> from measurements import CWEPR
    >>> from molecules import Molecule
    >>> mol = Molecule(name="TEMPO1")
    >>> m = CWEPR(
    ...     molecule=mol,
    ...     method="cwepr",
    ...     temperature=295.0,
    ...     solvent="Water",
    ...     date=date(2025, 3, 10),
    ...     measured_by="Alice",
    ...     path="/data/M17",
    ...     corrected=True,
    ...     evaluated=False,
    ...     frequency_band="X",
    ...     attenuation="10 dB",
    ... )
    >>> session.add(m)
    >>> session.commit()

    Polymorphic loading:

    >>> m = session.query(Measurement).filter_by(id=17).one()
    >>> type(m)
    <class 'models.CWEPR'>
    """
    __tablename__ = "cwepr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "cwepr",}

    frequency_band = Column(SAEnum(av.FrequencyBands), nullable=False)
    attenuation = Column(String(32), nullable=False)



class PulseEPR(Measurement):
    """
    Pulsed electron paramagnetic resonance (pulsed EPR) measurement.

    This subclass of :class:`Measurement` represents any pulsed EPR experiment,
    e.g. transient nutations, PELTOR, saturation recovery...
    This model adds pulsed-EPR-specific parameters such as the experiment type
    (e.g. Hahn Echo, ESEEM), frequency band, and optional excitation wavelength
    for optically triggered sequences.

    The model participates in SQLAlchemy polymorphism using the
    ``"pulse_epr"`` ``polymorphic_identity``. Any row in ``measurements`` where
    ``method='pulse_epr'`` is therefore automatically loaded as a
    :class:`PulseEPR` instance.

    Attributes
    ----------
    id : int
        Primary key linked to ``measurements.id`` with cascading delete.
    pulse_experiment : PulseExperiments
        Type of pulsed EPR sequence used (e.g. Hahn Echo, Rabi, ESEEM).
        Enum defined in ``allowed_values.PulseExperiments``.
    frequency_band : FrequencyBands or None
        Microwave frequency band of the experiment (e.g. X, Q, W-band).
        Optional because certain pulsed setups define frequency elsewhere.
    attenuation : str or None
        Microwave attenuation setting applied during the pulse sequence.
    excitation_wl : float or None
        Excitation wavelength in nanometres for optically triggered pulsed EPR
        experiments. Optional and only used for light-induced sequences.

    Notes
    -----
    * The tablename is ``pulse_epr``.
    * All shared measurement metadata (temperature, solvent, operator,
      timestamps, file path, etc.) are inherited from :class:`Measurement`.
    * The ``id`` corresponds directly to the entry in the main
      ``measurements`` table via single-table inheritance.
    * Pulse-experiments usually have many metadata that are important. A
      file containing the metadata (e.g. a .DSC-file) should be saved with
      the raw data at ``/data/Mxy/raw``.

    Examples
    --------
    Creating a pulsed EPR measurement:

    >>> from measurements import PulseEPR
    >>> from molecules import Molecule
    >>> mol = Molecule(name="PDI-TEMPO")
    >>> m = PulseEPR(
    ...     molecule=mol,
    ...     method="pulse_epr",
    ...     temperature=80.0,
    ...     solvent="Toluene",
    ...     date=date(2025, 4, 12),
    ...     measured_by="Bob",
    ...     path="/data/M21/measurement_M21.h5",
    ...     corrected=False,
    ...     evaluated=False,
    ...     pulse_experiment="HahnEcho",
    ...     frequency_band="X",
    ...     attenuation="20 dB",
    ...     excitation_wl=532.0,
    ... )
    >>> session.add(m)
    >>> session.commit()

    Loading via polymorphism:

    >>> m = session.query(Measurement).filter_by(id=21).one()
    >>> type(m)
    <class 'models.PulseEPR'>
    """


    __tablename__ = "pulse_epr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "pulse_epr",}

    pulse_experiment = Column(SAEnum(av.PulseExperiments), nullable=False)
    frequency_band = Column(SAEnum(av.FrequencyBands))
    attenuation = Column(String(32))
    excitation_wl = Column(Float)


class UVVis(Measurement):
    """
    UVvis  measurement.

    This subclass of :class:`Measurement` represents an UVvis experiment.
    This model adds the UVvis-specific parameter dim_cuvette.

    The model participates in SQLAlchemy polymorphism using the
    ``"uvvis"`` ``polymorphic_identity``. Any row in ``measurements`` where
    ``method='uvvis'`` is therefore automatically loaded as a
    :class:`UVVis` instance.

    Attributes
    ----------
    id : int
        Primary key linked to ``measurements.id`` with cascading delete.
    dim_cuvette: str
        Dimension of the cuvette.

    Notes
    -----
    * The tablename is ``uvvis``.
    * All shared measurement metadata (temperature, solvent, operator,
      timestamps, file path, etc.) are inherited from :class:`Measurement`.
    * The ``id`` corresponds directly to the entry in the main
      ``measurements`` table via single-table inheritance.

    Examples
    --------
    Creating an UVvis measurement:

    >>> from measurements import UVVis
    >>> from molecules import Molecule
    >>> mol = Molecule(name="PDI-TEMPO")
    >>> m = UVVis(
    ...     molecule=mol,
    ...     method="uvvis",
    ...     temperature=298,
    ...     solvent="Toluene",
    ...     date=date(2025, 4, 12),
    ...     measured_by="Bob",
    ...     path="/data/M21/measurement_M21.h5",
    ...     corrected=False,
    ...     evaluated=False,
    ...     dim_cuvette = "1cm"
    ... )
    >>> session.add(m)
    >>> session.commit()

    Loading via polymorphism:

    >>> m = session.query(Measurement).filter_by(id=21).one()
    >>> type(m)
    <class 'models.UVVis'>
    """


    __tablename__ = "uvvis"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "uvvis",}


    dim_cuvette = Column(String(64), nullable=False)


class Fluorescence(Measurement):
    """
    Fluorescence measurement.

    This subclass of :class:`Measurement` represents an Fluorescence experiment.
    This model adds the Fluorescence-specific parameters excitation,
    excitation_wl and od.

    The model participates in SQLAlchemy polymorphism using the
    ``"fluorescence"`` ``polymorphic_identity``. Any row in ``measurements``
    where ``method='fluorescence'`` is therefore automatically loaded as a
    :class:`Fluorescence` instance.

    Attributes
    ----------
    id : int
        Primary key linked to ``measurements.id`` with cascading delete.
    excitation: boolean
        Indicate wheather the data are an excitation (True) or
        emission (False) spectrum.
    excitation_wl : str
        Excitation wavelength incl. unit.
    od : str or None
        Optical density / absorbance.


    Notes
    -----
    * The tablename is ``fluorescence``.
    * All shared measurement metadata (temperature, solvent, operator,
      timestamps, file path, etc.) are inherited from :class:`Measurement`.
    * The ``id`` corresponds directly to the entry in the main
      ``measurements`` table via single-table inheritance.

    Examples
    --------
    Creating a Fluorescence measurement:

    >>> from measurements import Fluorescence
    >>> from molecules import Molecule
    >>> mol = Molecule(name="PDI-TEMPO")
    >>> m = Fluorescence(
    ...     molecule=mol,
    ...     method="uvvis",
    ...     temperature=298,
    ...     solvent="Toluene",
    ...     date=date(2025, 4, 12),
    ...     measured_by="Bob",
    ...     path="/data/M21/measurement_M21.h5",
    ...     corrected=False,
    ...     evaluated=False,
    ...     excitation=True,
    ...     excitation_wl="560nm"
    ... )
    >>> session.add(m)
    >>> session.commit()

    Loading via polymorphism:

    >>> m = session.query(Measurement).filter_by(id=21).one()
    >>> type(m)
    <class 'models.Fluorescence'>
    """


    __tablename__ = "fluorescence"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "fluorescence",}

    excitation = Column(Boolean, nullable=False)
    excitation_wl = Column(String(64), nullable=False)
    od = Column(String(64))

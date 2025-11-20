from models.base import TimeStampedModel

from sqlalchemy import Column, Integer, ForeignKey, String, Float,  Date, Text, Boolean
from sqlalchemy.orm import Relationship
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)



class Measurement(TimeStampedModel):
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
    __tablename__ = "cwepr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "cwepr",}

    frequency_band = Column(SAEnum(av.FrequencyBands), nullable=False)
    attenuation = Column(String(32), nullable=False)



class PulseEPR(Measurement):
    __tablename__ = "pulse_epr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "pulse_epr",}

    pulse_experiment = Column(SAEnum(av.PulseExperiments), nullable=False)
    frequency_band = Column(SAEnum(av.FrequencyBands))
    attenuation = Column(String(32))
    excitation_wl = Column(Float)

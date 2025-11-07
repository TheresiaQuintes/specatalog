from models.base import TimeStampedModel
from sqlalchemy.orm import validates
from models.allowed_values import Solvents, Devices, FrequencyBands
from helper_functions import validate_enum

from sqlalchemy import Column, Integer, ForeignKey, String, Float, Enum, Date, Text, Boolean
from sqlalchemy.orm import Relationship



class Measurement(TimeStampedModel):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # molecule
    molecular_id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                              nullable=False, index=True)
    molecule = Relationship("Molecule", back_populates="measurements")

    # method
    method = Column(String(20), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": method,
        "polymorphic_identity": "base",
        }

    # metadata
    temperature = Column(Float, nullable=False)
    solvent = Column(Enum(Solvents), nullable=False)
    concentration = Column(String(512))
    date = Column(Date, nullable=False)
    location = Column(String(512))
    device = Column(Enum(Devices))
    series = Column(String(512))
    path = Column(Text, nullable=False, unique=True)
    corrected = Column(Boolean, nullable=False)
    evaluated = Column(Boolean, nullable=False)

    @validates("solvent")
    def validate_solvent(self, key, value):
        return validate_enum(value, Solvents, key)

    @validates("device")
    def validate_device(self, key, value):
        return validate_enum(value, Devices, key)

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.molecule.name}, {self.method}, {self.temperature} K)"




class TREPR(Measurement):
    __tablename__ = "trepr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "trepr",}

    frequency_band = Column(Enum(FrequencyBands), nullable=False)
    excitation_wl = Column(Float, nullable=False)
    excitation_energy = Column(Float)
    attenuation = Column(Float, nullable=False)
    number_of_scans = Column(Integer)
    repetitionrate = Column(Float)
    mode = Column(String(256))

    @validates("frequency_band")
    def validate_frequency_band(self, key, value):
        return validate_enum(value, FrequencyBands, key)

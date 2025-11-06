from models.base import TimeStampedModel
from sqlalchemy.orm import validates
from models.allowed_values import Solvents
from helper_functions import validate_enum

from sqlalchemy import Column, Integer, ForeignKey, String, Float, Enum
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
    measurement_set = Column(String(60))

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.molecule.name}, {self.method}, {self.temperature} K)"




class TREPR(Measurement):
    __tablename__ = "trepr"

    id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "trepr",}

    frequency = Column(Float, nullable=False)
    excitation_wl = Column(Float, nullable=False)
    solvent = Column(Enum(Solvents))
    @validates("solvent")
    def validate_solvent(self, key, value):
        return validate_enum(value, Solvents, key)

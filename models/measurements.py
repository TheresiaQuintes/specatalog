from models.base import TimeStampedModel
from models.molecules import Molecule
from enum import Enum as eEnum
from sqlalchemy.orm import validates


from sqlalchemy import Column, Integer, ForeignKey, String, Float, Enum
from sqlalchemy.orm import Relationship


def validate_enum(value, enum_cls, field_name="unknown"):
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except ValueError:
        allowed = [e.value for e in enum_cls]
        raise ValueError(f"Ungültiger Wert '{value}' für {field_name}. Erlaubt: {allowed}")


class Solvents(str, eEnum):
    toluene = "toluene"
    water = "water"


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

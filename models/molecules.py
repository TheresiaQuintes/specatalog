from models.base import TimeStampedModel

from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import Relationship

class Molecule(TimeStampedModel):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)

    name = Column(String(124), nullable=False)
    summenformel = Column(String(124))

    measurements = Relationship("Measurement", back_populates="molecule",
                                    passive_deletes=True)

    group = Column(String(20), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": group,
        "polymorphic_identity": "base",
        }

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.name}, {self.id})"



class TDP(Molecule):
    __tablename__ = "tdp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "tdp",}

    doublet = Column(String, nullable=False)
    linker = Column(String)
    chromophore = Column(String, nullable=False)


class SingleMolecule(Molecule):
    __tablename__ = "single"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "single",}

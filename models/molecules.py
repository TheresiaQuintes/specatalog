from models.base import TimeStampedModel
from models.allowed_values import Doublets, Chromophores, Linker, Radicals
from helper_functions import validate_enum
from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Text
from sqlalchemy.orm import Relationship


class Molecule(TimeStampedModel):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(512), nullable=False, unique=True)
    molecular_formula = Column(String(124), nullable=False)
    structural_formula = Column(Text, unique=True, nullable=False)
    smiles = Column(Text, unique=True, nullable=False)

    measurements = Relationship("Measurement", back_populates="molecule",
                                    passive_deletes=True)

    group = Column(String(20), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": group,
        "polymorphic_identity": "base",
        }

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.name}, {self.id})"


class Single(Molecule):
    __tablename__ = "single"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    additional_info = Column(Text)

    __mapper_args__ = {"polymorphic_identity": "single",}


class RP(Molecule):
    __tablename__ = "rp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "rp",}

    radical_1 = Column(Enum(Radicals), nullable=False)
    linker = Column(Enum(Linker), nullable=False)
    radical_2 = Column(Enum(Radicals), nullable=False)

    @validates("radical_1")
    def validate_radical_1(self, key, value):
        return validate_enum(value, Radicals, key)

    @validates("linker")
    def validate_linker(self, key, value):
        return validate_enum(value, Linker, key)

    @validates("radical_2")
    def validate_radical_2(self, key, value):
        return validate_enum(value, Radicals, key)


class TDP(Molecule):
    __tablename__ = "tdp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "tdp",}

    doublet = Column(Enum(Doublets), nullable=False)
    linker = Column(Enum(Linker), nullable=False)
    chromophore = Column(Enum(Chromophores), nullable=False)

    @validates("doublet")
    def validate_doublet(self, key, value):
        return validate_enum(value, Doublets, key)

    @validates("linker")
    def validate_linker(self, key, value):
        return validate_enum(value, Linker, key)

    @validates("chromophore")
    def validate_chromophore(self, key, value):
        return validate_enum(value, Chromophores, key)


class TTP(Molecule):
    __tablename__ = "ttp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "ttp",}

    triplet_1= Column(Enum(Chromophores), nullable=False)
    linker = Column(Enum(Linker), nullable=False)
    triplet_2 = Column(Enum(Chromophores), nullable=False)

    @validates("triplet_1")
    def validate_triplet_1(self, key, value):
        return validate_enum(value, Chromophores, key)

    @validates("linker")
    def validate_linker(self, key, value):
        return validate_enum(value, Linker, key)

    @validates("triplet_2")
    def validate_triplet_2(self, key, value):
        return validate_enum(value, Chromophores, key)

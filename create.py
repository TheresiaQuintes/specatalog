import models.measurements as ms
import models.molecules as mol
from main import session
from helper_functions import safe_commit


def create_single(name, molecular_formula, structural_formula, smiles, additional_info=""):
    m = mol.Single()
    m.name = name
    m.molecular_formula = molecular_formula
    m.structural_formula = structural_formula
    m.smiles = smiles
    m.additional_info = additional_info

    session.add(m)
    safe_commit(session)

def create_rp(radical_1, linker, radical_2, molecular_formula, structural_formula, smiles):
    m = mol.RP()
    m.radical_1 = radical_1
    m.linker = linker
    m.radical_2 = radical_2
    m.name = f"{radical_1}-{linker}-{radical_2}"
    m.molecular_formula = molecular_formula
    m.structural_formula = structural_formula
    m.smiles = smiles

    session.add(m)
    safe_commit(session)

def create_tdp(chromophore, linker, doublet, molecular_formula, structural_formula, smiles):
    m = mol.TDP()
    m.doublet = doublet
    m.linker = linker
    m.chromophore = chromophore
    m.name = f"{chromophore}-{linker}-{doublet}"
    m.molecular_formula = molecular_formula
    m.structural_formula = structural_formula
    m.smiles = smiles

    session.add(m)
    safe_commit(session)

def create_ttp(triplet_1, linker, triplet_2, molecular_formula, structural_formula, smiles):
    m = mol.TTP()
    m.triplet_1 = triplet_1
    m.linker = linker
    m.triplet_2 = triplet_2
    m.name = f"{triplet_1}-{linker}-{triplet_2}"
    m.molecular_formula = molecular_formula
    m.structural_formula = structural_formula
    m.smiles = smiles

    session.add(m)
    safe_commit(session)

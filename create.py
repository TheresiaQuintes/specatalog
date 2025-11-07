import models.measurements as ms
import models.molecules as mol
from main import session
from helper_functions import safe_commit
import datetime


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

def create_trepr(molecule_id, temperature, solvent, path, corrected, evaluated, frequency_band, excitation_wl, date, attenuation, concentration="", location="", device="", series="",  excitation_energy=-1,  number_of_scans=-1, repetitionrate=-1, mode=""):
    m = ms.TREPR()
    molecule = mol.Molecule.query.filter(mol.Molecule.id == molecule_id).first()
    m.molecule = molecule
    m.temperature = temperature
    m.solvent = solvent
    m.concentration = concentration
    m.date = datetime.date(date[0], date[1], date[2])
    m.location = location
    m.device = device
    m.series = series
    m.path = path
    m.corrected = corrected
    m.evaluated = evaluated
    m.frequency_band = frequency_band
    m.excitation_wl = excitation_wl
    m.excitation_energy = excitation_energy
    m.attenuation = attenuation
    m.number_of_scans = number_of_scans
    m.repetitionrate = repetitionrate
    m.mode = mode

    session.add(m)
    safe_commit(session)

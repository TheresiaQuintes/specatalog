import models.measurements as ms
import models.molecules as mol
from main import session

# new molecule
#mol1 = mol.SingleMolecule()
#mol1.id = 1
#mol1.name = "toluene"
#mol1.summenformel = "C7H8"

#mol2 = mol.TDP()
#mol2.id = 2
#mol2.name = "PDI-TEMPO"
#mol2.summenformel = "CNOH"
#mol2.doublet = "TEMPO"
#mol2.chromophore = "PDI"


#session.add(mol1)
#session.add(mol2)


# new measurement
mol1 = mol.Molecule.query.filter(mol.Molecule.name == "toluene").first()
mol2 = mol.Molecule.query.filter(mol.Molecule.name == "BDP-co-NO1").first()


exp1 = ms.TREPR()
exp1.temperature = 80
exp1.molecule = mol1
exp1.excitation_wl = 765
exp1.frequency = 9.75
exp1.solvent = "water"

session.add(exp1)

"""
exp2 = ms.TREPR()
exp2.temperature = 80
exp2.molecule = mol2
exp2.excitation_wl = 765
exp2.frequency = 9.75


session.add(exp2)

session.commit()
"""

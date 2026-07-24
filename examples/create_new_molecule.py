from specatalog.helpers.full_entry import create_full_molecule
from specatalog.models import creation_pydantic_molecules as mol


# Beide Strukturdateien müssen denselben Dateinamen-Stamm besitzen.
# Die Dateiendungen werden von create_full_molecule() automatisch ergänzt.
structural_formula_src = (
    "/home/quintes/NAS/Theresia/praesentationen/doktorarbeit/"
    "Abbildungen/eigene/strukturformeln/PDI-H-TZ-eTEMPO"
)

new_molecule = mol.TDPModel(
    molecular_formula="C...H...N...O...",
    doublet="no4",
    linker="co",
    chromophore="pdi4",
)

result = create_full_molecule(
    data=new_molecule,
    molecular_formula_path=[structural_formula_src],
    fmt="all",
)

if result.success:
    print("Molecule successfully created.")
    print(f"Molecule ID: MOL{result.molecular_id}")
else:
    print("Molecule creation failed.")
    print(result.error)

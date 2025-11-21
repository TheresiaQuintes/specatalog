from models import creation_pydantic_molecules as mol
from crud_db import create
import shutil
from pathlib import Path
from main import BASE_PATH

# %%
structural_formula_src_pdf = "/home/quintes/NAS/Theresia/praesentationen/doktorarbeit/Abbildungen/eigene/strukturformeln/PDI-H-TZ-eTEMPO.pdf"

structural_formula_src_cdxml = "/home/quintes/NAS/Theresia/praesentationen/doktorarbeit/Abbildungen/eigene/strukturformeln/PDI-H-TZ-eTEMPO.cdxml"

new_molecule = mol.TDPModel(molecular_formula="get from chemdraw2",
                            smiles = "get from chemdraw2",
                            doublet = "NO4",
                            linker = "co",
                            chromophore = "PDI4"
                            )


# %%
molecule = create.create_new_molecule(new_molecule)

target_path_pdf = f"{BASE_PATH}/{molecule.structural_formula}/{molecule.name}.pdf"
target_path_cdxml = f"{BASE_PATH}/{molecule.structural_formula}/{molecule.name}.cdxml"

Path(target_path_pdf).parent.mkdir(parents=True, exist_ok=True)

shutil.copy2(structural_formula_src_pdf, target_path_pdf)
shutil.copy2(structural_formula_src_cdxml, target_path_cdxml)

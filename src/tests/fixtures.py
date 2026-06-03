import specatalog.models.molecules as mol
import specatalog.models.measurements as ms
import specatalog.models.creation_pydantic_molecules as pymol
from specatalog.main import ALLOWED_VALUES as av
from datetime import date

# Example setup for all Molecule classes for iteration in tests
MOLECULE_CASES = [
    (
        mol.Molecule,
        dict(
            name="Mol",
            molecular_formula="C10H10",
            structural_formula="/tmp/mol",
            group="base",
        ),
    ),
    (
        mol.SingleMolecule,
        dict(
            name="SingleMolecule",
            molecular_formula="C10H10",
            structural_formula="/tmp/single",
            group="single",
        ),
    ),
    (
        mol.RP,
        dict(
            name="RP1",
            molecular_formula="C10H10",
            structural_formula="/tmp/rp",
            group="rp",
            radical_1="A",
            linker="B",
            radical_2="C",
        ),
    ),
    (
        mol.TDP,
        dict(
            name="TDP1",
            molecular_formula="C10H10",
            structural_formula="/tmp/tdp",
            group="tdp",
            doublet="A",
            linker="B",
            chromophore="C",
        ),
    ),
    (
        mol.TTP,
        dict(
            name="TTP1",
            molecular_formula="C10H10",
            structural_formula="/tmp/ttp",
            group="ttp",
            triplet_1="A",
            linker="B",
            triplet_2="C",
        ),
    ),
]

# Example setup for all Measurement classes for iteration in tests
MEASUREMENT_CASES = [
    (
        ms.Measurement,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
        ),
    ),
    (
        ms.TREPR,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            frequency_band="x",
            excitation_wl=345,
            attenuation="20dB",
        ),
    ),
    (
        ms.CWEPR,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            frequency_band="x",
            attenuation="20dB"
        ),
    ),
    (
        ms.PulseEPR,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            pulse_experiment="DEER",
        ),
    ),
    (
        ms.UVVis,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            dim_cuvette="1x1x1",
        ),
    ),
    (
        ms.Fluorescence,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            excitation=False,
            excitation_wl="345nm"
        ),
    ),
    (
        ms.TA,
        dict(
            temperature=298,
            solvent="toluene",
            date=date(2026, 5, 5),
            measured_by="me",
            path="/tmp/ms1",
            corrected=True,
            evaluated=True,
            timedomain="ns",
            excitation_energy="high",
            excitation_wl="345nm",
        ),
    ),
]


MODEL_SPECS = {
    "RP": {
        "model": mol.RP,
        "class": pymol.RPModel,
        "factory": lambda suffix=None: dict(
            radical_1=av.Radicals.trp,
            linker=av.Linker.co,
            radical_2=av.Radicals.trp,
            name_suffix=suffix,
        ),
        "expected_base_name": "trp-co-trp",
    },
    "TDP": {
        "model": mol.TDP,
        "class": pymol.TDPModel,
        "factory": lambda suffix=None: dict(
            doublet=av.Doublets.no1,
            linker=av.Linker.co,
            chromophore=av.Chromophores.per,
            name_suffix=suffix,
        ),
        "expected_base_name": "per-co-no1",
    },
    "TTP": {
        "model": mol.TTP,
        "class": pymol.TTPModel,
        "factory": lambda suffix=None: dict(
            triplet_1=av.Chromophores.per,
            linker=av.Linker.co,
            triplet_2=av.Chromophores.per,
            name_suffix=suffix,
        ),
        "expected_base_name": "per-co-per",
    },
}

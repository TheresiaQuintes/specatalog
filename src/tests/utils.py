import pytest
from fixtures import MOLECULE_CASES, MEASUREMENT_CASES

def parametrize_molecules():
    return pytest.mark.parametrize(
        "model_class, kwargs",
        MOLECULE_CASES,
        ids=[cls.__name__ for cls, _ in MOLECULE_CASES],
    )

def parametrize_measurements():
    return pytest.mark.parametrize(
        "model_class, kwargs",
        MEASUREMENT_CASES,
        ids=[cls.__name__ for cls, _ in MEASUREMENT_CASES],
    )

import pytest
from fixtures import MOLECULE_CASES, MEASUREMENT_CASES, MODEL_SPECS

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


@pytest.fixture(params=list(MODEL_SPECS.keys()))
def model_spec(request):
    return MODEL_SPECS[request.param]

@pytest.fixture
def model_instance(model_spec):
    return model_spec["class"](**model_spec["factory"]())

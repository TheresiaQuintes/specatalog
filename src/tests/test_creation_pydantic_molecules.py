import pytest
import specatalog.models.molecules as mol
from fixtures import MODEL_SPECS


def test_model_class(model_spec, model_instance):
    assert model_instance.model_class is model_spec["model"]


def test_base_name(model_spec, model_instance):
    expected = model_spec["expected_base_name"]
    assert model_instance.name == expected


@pytest.mark.parametrize("suffix", ["A", "test"])
def test_name_with_suffix(model_spec, suffix):
    if model_spec["model"] is not mol.SingleMolecule:
        instance = model_spec["class"](**model_spec["factory"](suffix=suffix))
        expected = model_spec["expected_base_name"] + f"-{suffix}"
        assert instance.name == expected


@pytest.mark.parametrize(
    "model_key,missing_field",
    [
        ("SingleMolecule", "name"),
        ("RP", "radical_1"),
        ("RP", "linker"),
        ("RP", "radical_2"),
        ("TDP", "doublet"),
        ("TDP", "linker"),
        ("TDP", "chromophore"),
        ("TTP", "triplet_1"),
        ("TTP", "linker"),
        ("TTP", "triplet_2"),
    ],
)
def test_missing_required_fields(model_key, missing_field):
    spec = MODEL_SPECS[model_key]
    data = spec["factory"]()

    data.pop(missing_field)

    with pytest.raises(Exception):
        spec["class"](**data)


@pytest.mark.parametrize("model_key", MODEL_SPECS.keys())
def test_extra_fields_forbidden(model_key):
    spec = MODEL_SPECS[model_key]
    data = spec["factory"]()
    data["not_allowed_field"] = "x"

    with pytest.raises(Exception):
        spec["class"](**data)


@pytest.mark.parametrize(
    "model_key,enum_field",
    [
        ("RP", "radical_1"),
        ("RP", "linker"),
        ("RP", "radical_2"),
        ("TDP", "doublet"),
        ("TDP", "linker"),
        ("TDP", "chromophore"),
        ("TTP", "triplet_1"),
        ("TTP", "linker"),
        ("TTP", "triplet_2"),
    ],
)
def test_forbidden_enum_values(model_key, enum_field):
    spec = MODEL_SPECS[model_key]
    data = spec["factory"]()

    data[enum_field] = "not allowed"

    with pytest.raises(Exception):
        spec["class"](**data)


def test_model_class_immutable(model_instance):
    with pytest.raises(Exception):
        model_instance.model_class = "new"

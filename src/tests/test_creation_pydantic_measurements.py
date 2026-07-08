import pytest
import specatalog.models.measurements as ms
from fixtures import MEASUREMENT_SPECS


def test_measurement_class(measurement_spec, measurement_instance_pyd):
    if measurement_spec["model"] is not ms.Measurement:
        assert measurement_instance_pyd.measurement_class is measurement_spec["model"]


@pytest.mark.parametrize(
    "measurement_key,missing_field",
    [
        ("Measurement", "molecular_id"),
        ("Measurement", "temperature"),
        ("Measurement", "solvent"),
        ("Measurement", "date"),
        ("Measurement", "measured_by"),
        ("Measurement", "corrected"),
        ("Measurement", "evaluated"),
        ("CWEPR", "frequency_band"),
        ("CWEPR", "attenuation"),
        ("TREPR", "frequency_band"),
        ("TREPR", "attenuation"),
        ("TREPR", "excitation_wl"),
        ("PulseEPR", "pulse_experiment"),
        ("UVVis", "dim_cuvette"),
        ("Fluorescence", "excitation"),
        ("Fluorescence", "excitation_wl"),
        ("TA", "timedomain"),
        ("TA", "excitation_wl"),
        ("TA", "excitation_energy"),
    ],
)
def test_missing_required_fields(measurement_key, missing_field):
    spec = MEASUREMENT_SPECS[measurement_key]
    data = spec["factory"]()

    data.pop(missing_field)

    with pytest.raises(Exception):
        spec["class"](**data)


@pytest.mark.parametrize("measurement_key", MEASUREMENT_SPECS.keys())
def test_extra_fields_forbidden(measurement_key):
    spec = MEASUREMENT_SPECS[measurement_key]
    data = spec["factory"]()
    data["not_allowed_field"] = "x"

    with pytest.raises(Exception):
        spec["class"](**data)


@pytest.mark.parametrize(
    "measurement_key,enum_field",
    [
        ("Measurement", "solvent"),
        ("Measurement", "measured_by"),
        ("Measurement", "device"),
        ("CWEPR", "frequency_band"),
        ("TREPR", "frequency_band"),
        ("PulseEPR", "pulse_experiment"),
        ("PulseEPR", "frequency_band"),
        ("TA", "timedomain"),
    ],
)
def test_forbidden_enum_fields(measurement_key, enum_field):
    spec = MEASUREMENT_SPECS[measurement_key]
    data = spec["factory"]()
    data[enum_field] = "not allowed"

    with pytest.raises(Exception):
        spec["class"](**data)


def test_measurement_class_immutable(measurement_instance_pyd):
    with pytest.raises(Exception):
        measurement_instance_pyd.measurement_class = "new"

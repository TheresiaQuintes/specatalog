from utils import model_spec, model_instance

def test_model_class(model_spec, model_instance):
    assert model_instance.model_class is model_spec["model"]

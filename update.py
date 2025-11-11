import helper_functions as hf
import models.measurements as ms
import models.molecules as mol
from sqlalchemy.orm import Session
from pydantic import BaseModel
#from main import session

def update_model(obj,  # SQLAlchemy-Instanz, z.B. TREPR
    update_data: BaseModel,  # Pydantic UpdateModel
s):
    """
    Aktualisiert ein SQLAlchemy-Objekt anhand eines Pydantic UpdateModels.
    """
    # Nur die Werte nehmen, die gesetzt sind
    data = update_data.model_dump(exclude_none=True)

    for field, value in data.items():
        if hasattr(obj, field):
            setattr(obj, field, value)
        else:
            raise ValueError(f"Ungültiges Feld: {field}")

    s.add(obj)
    hf.safe_commit(s)


UpdateModel = hf.make_update_model(mol.TDP)


# Probleme lösen:
    # Session nicht mehrfach verwenden (-> Import ändern)
    # update_model macht update der Subklasse aber nicht vom Namen wenn z.B. linker sich ändert
    # updated_at änder sich nicht

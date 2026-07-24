from specatalog.crud_db import read as r
from specatalog.crud_db import update as up


# Eine CW-EPR-Messung mit der ID 1 laden
results = r.run_query(
    r.CWEPRFilter(id=1),
)

if not results:
    raise ValueError("Keine CW-EPR-Messung mit der ID M1 gefunden.")

measurement = results[0]

# Felder der Messung aktualisieren
updates = up.CWEPRUpdate(
    frequency_band="q",
    temperature=80.0,
    solvent="toluene",
    evaluated=True,
)

up.update_model(
    entry=measurement,
    update_data=updates,
)

print(f"Measurement M{measurement.id} successfully updated.")

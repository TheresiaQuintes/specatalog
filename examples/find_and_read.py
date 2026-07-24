from pathlib import Path

from specatalog.crud_db import read as r
from specatalog.data_management import measurement_management as mm


# Alle EPR-Messungen des Moleküls MOL1 suchen.
# '%' ist ein SQL-Wildcard und steht für beliebig viele Zeichen.
find_measurement = r.MeasurementFilter(
    molecular_id=1,
    method__ilike="%epr",
)

ordering = r.MeasurementOrdering(
    method="desc",
)

results = r.run_query(
    filters=find_measurement,
    ordering=ordering,
)

for measurement in results:
    print(measurement)


# Dateien der Kategorie "raw" für die Messung M1 auflisten
files = mm.list_files(
    ms_id=1,
    category="raw",
)

for file in files:
    print(Path(file).name)
from specatalog.crud_db import read as r
from specatalog.data_management import measurement_management as mm
from specatalog.main import BASE_PATH

find_measurement = r.MeasurementFilter(molecular_id=1, method__ilike="__epr")
order = r.MeasurementOrdering(method="desc")

results = r.run_query(find_measurement, order)

for result in results:
    print(result)


# list files in one categroy of measurement
a = mm.list_files(BASE_PATH, 1, category="raw")
for data in a:
    print(data.name)

from crud_db import read as r

find_measurement = r.MeasurementFilter(molecular_id=1, method__ilike="__epr")
order = r.MeasurementOrdering(method="desc")

results = r.run_query(find_measurement, order)

print(results)

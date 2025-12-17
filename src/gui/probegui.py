from nicegui import ui
from specatalog.crud_db import read as r
from specatalog.data_management import measurement_management as mm
from specatalog.main import BASE_PATH
import pandas as pd

ui.markdown("**Welcome to specatalog!**")

#ms_id = ui.input("ID")
find_measurement = r.MeasurementFilter(molecular_id=1)

ui.button("Query database", color="red", on_click=lambda: query(find_measurement))



def query(FilterModel):
    results = r.run_query(find_measurement)
    df = pd.DataFrame(results)
    rows = [{c.name: getattr(results[0], c.name) for c in results[0].__table__.columns}]
    table = ui.table(rows=rows)
#ui.run()


results = r.run_query(find_measurement)

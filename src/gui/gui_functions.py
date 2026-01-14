from specatalog.crud_db import read as r
from table_models import MeasurementsTableModel
from PyQt6.QtCore import Qt

def print_clicked():
    print("clicked")

def load_all_measurements():
    filter_model = r.MeasurementFilter()
    ordering_model = r.MeasurementOrdering(id="asc")
    results = r.run_query(filter_model, ordering_model)
    model = MeasurementsTableModel(results)
    return model

def on_header_clicked(self):
    filter_model = r.MeasurementFilter()
    ordering_model = r.MeasurementOrdering()

    header_number = self.header.sortIndicatorSection()
    model = r. MeasurementOrdering
    fields = list(model.model_fields)
    field_name = fields[header_number]

    sort_order = self.header.sortIndicatorOrder()
    if sort_order == Qt.SortOrder.DescendingOrder:
        setattr(ordering_model, field_name, "desc")
    if sort_order == Qt.SortOrder.AscendingOrder:
        setattr(ordering_model, field_name, "asc")

    model = load_measurements(filter_model, ordering_model)
    self.MeasurementsView.setModel(model)




def load_measurements(filter_model, ordering_model):
    results = r.run_query(filter_model, ordering_model)
    model = MeasurementsTableModel(results)
    return model

def text_changed(self, text):
    print(text)

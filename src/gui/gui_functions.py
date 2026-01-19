from specatalog.crud_db import read as r
from table_models import MeasurementsTableModel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox,  QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QMessageBox
import datetime
import enum
from typing import get_origin, get_args, Union
import specatalog.models.creation_pydantic_measurements as cpm
from specatalog.helpers.full_measurement import create_full_measurement
from pydantic_core._pydantic_core import ValidationError
from PyQt6 import QtWidgets
from pathlib import Path
from specatalog.main import BASE_PATH

MODEL_FILTER_MAPPER = {"Measurements": r.MeasurementFilter,
                       "trEPR": r.TREPRFilter,
                       "cwEPR": r.CWEPRFilter,
                       "pulseEPR": r.PulseEPRFilter,
                       "UVvis": r.UVVisFilter,
                       "Fluorescence": r.FluorescenceFilter,
                       "TA": r.TAFilter}

MODEL_ORDERING_MAPPER = {"Measurements": r.MeasurementOrdering,
                       "trEPR": r.TREPROrdering,
                       "cwEPR": r.CWEPROrdering,
                       "pulseEPR": r.PulseEPROrdering,
                       "UVvis": r.UVVisOrdering,
                       "Fluorescence": r.FluorescenceOrdering,
                       "TA": r.TAOrdering}

MODEL_NEW_MODEL_MAPPER = {"trEPR": cpm.TREPRModel,
                          "cwEPR": cpm.CWEPRModel,
                          "pulseEPR": cpm.PulseEPRModel,
                          "UVvis": cpm.UVVisModel,
                          "Fluorescence": cpm.FluorescenceModel,
                          "TA": cpm.TAModel}
def run_query(self):
    data = get_values(self, self.filter_fields)
    self.filter_model = self.filter_model.copy(update=data)
    load_measurements(self)

def submit_new_entry(self):
    data = get_values(self, self.new_fields)
    if data["corrected"] == None:
        data["corrected"] = False
    if data["evaluated"] == None:
        data["evaluated"] = False

    try:
        new_entry_model = MODEL_NEW_MODEL_MAPPER[self.ComboModelChoiceNewEntry.currentText()](**data)

    except ValidationError as e:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Validation Error")
        msg.setText("Please fill out all required fields.")
        msg.setDetailedText(str(e))
        msg.exec()
        return

    raw_data = self.LineRawDataInput.text()

    output = create_full_measurement(new_entry_model, BASE_PATH, raw_data,
                                     self.ComboRawFormat.currentText())

    if output.success:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText(f"Measurement M{output.measurement_id} has been created successfully!")
        msg.exec()
        return

    else:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("An error occured.")
        msg.setText("The creation has not been completed.")
        msg.setDetailedText(str(output.error))
        msg.exec()



def open_file_dialog(self):
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose a file")
    if file_path:
        path = Path(file_path)
        self.LineRawDataInput.setText(str(path.with_suffix("")))



def on_tab_changed(self, index):
    self.tab_index = index

def on_header_clicked(self):
    self.ordering_model = MODEL_ORDERING_MAPPER[self.ComboModelChoice.currentText()]()

    header_number = self.header.sortIndicatorSection()
    model = MODEL_ORDERING_MAPPER[self.ComboModelChoice.currentText()]
    fields = list(model.model_fields)
    field_name = fields[header_number]

    sort_order = self.header.sortIndicatorOrder()
    if sort_order == Qt.SortOrder.DescendingOrder:
        setattr(self.ordering_model, field_name, "desc")
    if sort_order == Qt.SortOrder.AscendingOrder:
        setattr(self.ordering_model, field_name, "asc")
    load_measurements(self)


def load_measurements(self):
    results = r.run_query(self.filter_model, self.ordering_model)
    model = MeasurementsTableModel(results, self.ComboModelChoice.currentText())
    self.MeasurementsView.setModel(model)

def filter_model_changed(self, model):
    self.filter_model = MODEL_FILTER_MAPPER[model]()
    self.ordering_model = MODEL_ORDERING_MAPPER[model]()
    self.ordering_model.id="asc"
    load_measurements(self)
    build_form(self, self.FormFilter, self.filter_fields, MODEL_FILTER_MAPPER[model].model_fields)


def new_entry_model_changed(self, model):
    build_form(self, self.FormNewEntry, self.new_fields, MODEL_NEW_MODEL_MAPPER[model].model_fields)



def get_field_type(field_annotation):
    origin = get_origin(field_annotation)
    if origin is Union:
        args = [arg for arg in get_args(field_annotation) if arg is not type(None)]
        if args:
            return args[0]  # z.B. int aus Union[int, NoneType]
        return None
    return field_annotation

def build_form(self, layout, fields, schema: dict):
    # altes Formular löschen
    while layout.rowCount():
        layout.removeRow(0)

    fields.clear()

    for key, field in schema.items():
        if "__" in key:
            continue
        elif (self.tab_index == 0 and (key in["date", "created_at", "updated_at", "method"])):
            continue
        else:
            field_type = get_field_type(field.annotation)
            widget = create_widget_for_type(self, field_type)

            label = key
            if field.is_required():
                label = f"{key} *"

            layout.addRow(label, widget)
            fields[key] = widget


def create_widget_for_type(self, field_type):
    if field_type == str:
        return QLineEdit()
    if field_type == int:
        spin = QSpinBox()
        spin.setRange(-1_000_000_000, 1_000_000_000)
        spin.setValue(0)
        return spin
    if field_type == float:
        dspin = QDoubleSpinBox()
        dspin.setRange(-1e15, 1e15)
        dspin.setDecimals(3)
        dspin.setValue(0.0)
        return dspin
    if field_type == bool:
        combo = QComboBox()
        combo.addItem("", userData=None)
        combo.addItem("Yes", True)
        combo.addItem("No", False)
        combo.setCurrentIndex(0)
        return combo
    if field_type == datetime.date:
        widget = QDateEdit()
        widget.setCalendarPopup(True)
        widget.setDate(datetime.date.today())
        return widget
    if field_type == datetime.datetime:
        widget = QDateTimeEdit()
        widget.setCalendarPopup(True)
        widget.setDate(datetime.date.today())
        return widget
    if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
        combo = QComboBox()
        combo.addItem("", userData=None)
        combo.addItems([e.value for e in field_type])
        return combo
    return QLineEdit()


def get_values(self, fields):
    data = {}
    for key, widget in fields.items():
        if isinstance(widget, QLineEdit):
            data[key] = widget.text()
            if widget.text() == "":
                data[key] = None
        elif isinstance(widget, QSpinBox):
            data[key] = widget.value()
            if widget.value()==0:
                data[key] = None
        elif isinstance(widget, QDoubleSpinBox):
            data[key] = widget.value()
            if widget.value()==0:
                data[key] = None
        elif isinstance(widget, QComboBox):
            data[key] = widget.currentText()
            if widget.currentText() == "":
                data[key] = None
            if widget.currentText() == "Yes":
                data[key] = True
            if widget.currentText() == "No":
                data[key] = False
        elif isinstance(widget, QDateEdit):
            qdate = widget.date()
            py_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
            data[key] = py_date

        elif isinstance(widget, QDateTimeEdit):
            data[key] = widget.datetime().toPython()
    return data

def show_error(self, text: str):
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error")
    msg.setText(text)
    msg.exec()

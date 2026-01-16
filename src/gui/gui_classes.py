from SpecatalogMainWindow import Ui_MainWindow
from PyQt6 import QtWidgets
import gui_signal_slots as gss
import gui_functions as gf
from PyQt6.QtCore import Qt
from specatalog.crud_db import read as r
from specatalog.models import creation_pydantic_measurements as cpm



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # combobox
        self.ComboModelChoice.addItems(["Measurements", "trEPR", "cwEPR",
                                        "pulseEPR", "UVvis", "Fluorescence",
                                        "TA"])
        self.ComboModelChoiceNewEntry.addItems(["trEPR",
                                                "cwEPR", "pulseEPR", "UVvis",
                                                "Fluorescence", "TA"])

        # models
        self.filter_model = r.MeasurementFilter()
        self.ordering_model = r.MeasurementOrdering(id="asc")

        # Measurements table
        gf.load_measurements(self)
        self.header = self.MeasurementsView.horizontalHeader()
        self.header.setSectionsClickable(True)
        self.header.setSortIndicatorShown(True)
        self.header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)

        # Filter area
        self.tab_index = 0
        self.filter_fields = {}
        gf.build_form(self, self.FormFilter, self.filter_fields,
                      r.MeasurementFilter.model_fields)

        # New Entry area
        self.tab_index = 1
        self.new_fields = {}
        gf.build_form(self, self.FormNewEntry, self.new_fields,
                      cpm.TREPRModel.model_fields)
        self.tab_index = 0

        # connections
        gss.connect_signal_slot(self)
        gss.connections_db_tables(self)

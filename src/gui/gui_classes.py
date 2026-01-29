from SpecatalogMainWindow import Ui_MainWindow
from PyQt6 import QtWidgets
import gui_signal_slots as gss
import gui_functions as gf
from PyQt6.QtCore import Qt
from specatalog.crud_db import read as r
from specatalog.models import creation_pydantic_measurements as cpm
from pathlib import Path


class DragDropLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            self.setText(str(path.with_suffix("")))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        gf.change_ms_mol(self)

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

        self.raw_format = "bruker_bes3t"

        # Raw data field
        # Ersetze das normale QLineEdit durch unser DragDropLineEdit
        layout = self.LineRawDataInput.parent().layout()
        # Position des alten Widgets finden
        for row in range(layout.rowCount()):
            for col in range(layout.columnCount()):
                item = layout.itemAtPosition(row, col)
                if item and item.widget() == self.LineRawDataInput:
                    # alte Widget entfernen
                    layout.removeWidget(self.LineRawDataInput)
                    self.LineRawDataInput.deleteLater()
                    # neues DragDropLineEdit an gleicher Position einfügen
                    self.LineRawDataInput = DragDropLineEdit()
                    layout.addWidget(self.LineRawDataInput, row, col)
                    break


        # connections
        gss.connect_signal_slot(self)
        gss.connections_db_tables(self)

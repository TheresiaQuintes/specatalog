from specatalog.gui.SpecatalogMainWindow import Ui_MainWindow
from PyQt6 import QtWidgets, QtCore
import specatalog.gui.gui_signal_slots as gss
import specatalog.gui.gui_functions as gf
from PyQt6.QtCore import Qt
from specatalog.crud_db import read as r
from specatalog.models import creation_pydantic_measurements as cpm
from pathlib import Path


class DragDropLineEdit(QtWidgets.QLineEdit):
    filesDropped = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.files = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.files = list(
                dict.fromkeys(Path(url.toLocalFile()).with_suffix("") for url in urls)
            )
            if len(self.files) == 1:
                self.setText(str(self.files[0]))
            elif len(self.files) == 0:
                self.setText("choose a file")
            else:
                self.setText("multiple files are chosen")

            self.filesDropped.emit(self.files)


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
        gf.build_form(
            self, self.FormFilter, self.filter_fields, r.MeasurementFilter.model_fields
        )

        # New Entry area
        self.tab_index = 1
        self.new_fields = {}
        gf.build_form(
            self, self.FormNewEntry, self.new_fields, cpm.TREPRModel.model_fields
        )
        self.tab_index = 0

        self.raw_format = "bruker_bes3t"

        # Raw data field
        self.raw_data_files = []
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
                    self.LineRawDataInput.filesDropped.connect(
                        lambda files: setattr(self, "raw_data_files", files)
                    )
                    break

        # connections
        gss.connect_signal_slot(self)
        gss.connections_db_tables(self)

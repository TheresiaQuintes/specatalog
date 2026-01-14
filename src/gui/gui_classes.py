from SpecatalogMainWindow import Ui_MainWindow
from PyQt6 import QtWidgets
import gui_signal_slots as gss
import gui_functions as gf
from PyQt6.QtCore import Qt

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # combobox
        self.ComboModelChoice.addItems(["Measurements", "UVvis"])

        # Measurements table
        model = gf.load_all_measurements()
        self.MeasurementsView.setModel(model)

        self.header = self.MeasurementsView.horizontalHeader()
        self.header.setSectionsClickable(True)
        self.header.setSortIndicatorShown(True)
        self.header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)


        # connections
        gss.connect_signal_slot(self)
        gss.connections_db_tables(self)

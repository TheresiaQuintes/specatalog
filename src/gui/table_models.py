from PyQt6.QtCore import QAbstractTableModel, Qt
import specatalog.models.measurements as ms
from sqlalchemy.inspection import inspect
import enum
import datetime

MODEL_MODEL_MAPPER = {"Measurements": ms.Measurement,
                       "trEPR": ms.TREPR,
                       "cwEPR": ms.CWEPR,
                       "pulseEPR": ms.PulseEPR,
                       "UVvis": ms.UVVis,
                       "Fluorescence": ms.Fluorescence,
                       "TA": ms.TA}



class MeasurementsTableModel(QAbstractTableModel):
    def __init__(self, measurements, model):
        super().__init__()
        self._measurements = measurements
        mapper = inspect(MODEL_MODEL_MAPPER[model])
        self._headers = [
            column.key
            for column in mapper.columns
            if not (column.primary_key and column.foreign_keys)]
        self._headers.insert(2, "molecule_name")

    def rowCount(self, parent=None):
        return len(self._measurements)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        measurement = self._measurements[index.row()]
        attr = self._headers[index.column()]

        if attr == "molecule_name":
            value = measurement.molecule.name
        else:
            value = getattr(measurement, attr)

        if value is None:
            return ""

        # Enum → Name oder Value
        if isinstance(value, enum.Enum):
            return value.name       # oder: value.value

        # date / datetime → String
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.strftime("%Y-%m-%d")

        return value

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

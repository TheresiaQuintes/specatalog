from PyQt6.QtCore import QAbstractTableModel, Qt
from specatalog.models.measurements import Measurement
from sqlalchemy.inspection import inspect
import enum
import datetime

mapper = inspect(Measurement)
HEADERS_MEASUREMENT = [column.key for column in mapper.columns]

class MeasurementsTableModel(QAbstractTableModel):
    def __init__(self, measurements):
        super().__init__()
        self._measurements = measurements
        self._headers = HEADERS_MEASUREMENT

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

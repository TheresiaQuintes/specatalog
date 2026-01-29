from PyQt6.QtCore import QAbstractTableModel, Qt, QDate, QDateTime
import specatalog.models.measurements as ms
import specatalog.models.molecules as mol
import specatalog.crud_db.update as up
from sqlalchemy.inspection import inspect
import enum
import datetime
from PyQt6.QtWidgets import QComboBox,  QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QStyledItemDelegate

MODEL_MODEL_MAPPER = {"Measurements": ms.Measurement,
                       "trEPR": ms.TREPR,
                       "cwEPR": ms.CWEPR,
                       "pulseEPR": ms.PulseEPR,
                       "UVvis": ms.UVVis,
                       "Fluorescence": ms.Fluorescence,
                       "TA": ms.TA,
                       "Molecules": mol.Molecule,
                       "SingleMolecule": mol.SingleMolecule,
                       "RP": mol.RP,
                       "TDP": mol.TDP,
                       "TTP": mol.TTP}

MODEL_UPDATE_MAPPER = {"trepr": up.TREPRUpdate,
                       "cwepr": up.CWEPRUpdate,
                       "pulse_epr": up.PulseEPRUpdate,
                       "uvvis": up.UVVisUpdate,
                       "fluorescence": up.FluorescenceUpdate,
                       "ta": up.TAUpdate,
                       "single": up.SingleMoleculeUpdate,
                       "rp": up.RPUpdate,
                       "tdp": up.TDPUpdate,
                       "ttp": up.TTPUpdate
                       }


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

        measurement = self._measurements[index.row()]
        attr = self._headers[index.column()]

        if attr == "molecule_name":
            value = measurement.molecule.name
        else:
            value = getattr(measurement, attr)

        if role == Qt.ItemDataRole.EditRole:
            return value

        if role == Qt.ItemDataRole.DisplayRole:
            if value is None:
                return ""

            if isinstance(value, enum.Enum):
                return value.name

            if isinstance(value, (datetime.date, datetime.datetime)):
                return value.strftime("%Y-%m-%d")

            return value

        return None

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        attr = self._headers[index.column()]

        if attr in ("id", "molecular_id", "method", "path", "created_at",
                    "updated_at", "molecule_name"):
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole:
            return False

        measurement = self._measurements[index.row()]
        attr = self._headers[index.column()]

        # nicht editierbar
        if attr == "molecule_name":
            return False

        try:
            UpdateClass = MODEL_UPDATE_MAPPER[measurement.method]
            update_model = UpdateClass(**{attr: value})
            up.update_model(measurement, update_model)
            setattr(measurement, attr, value)

        except Exception as e:
            print(f"Update failed: {e}")
            return False

        # GUI aktualisieren
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True


class MoleculesTableModel(QAbstractTableModel):
    def __init__(self, molecules, model):
        super().__init__()
        self._molecules = molecules
        mapper = inspect(MODEL_MODEL_MAPPER[model])
        self._headers = [
            column.key
            for column in mapper.columns
            if not (column.primary_key and column.foreign_keys)]

    def rowCount(self, parent=None):
        return len(self._molecules)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        molecule = self._molecules[index.row()]
        attr = self._headers[index.column()]


        value = getattr(molecule, attr)

        if role == Qt.ItemDataRole.EditRole:
            return value

        if role == Qt.ItemDataRole.DisplayRole:
            if value is None:
                return ""

            if isinstance(value, enum.Enum):
                return value.name

            if isinstance(value, (datetime.date, datetime.datetime)):
                return value.strftime("%Y-%m-%d")

            return value

        return None

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        attr = self._headers[index.column()]

        if attr in ("id", "molecular_id", "method", "path", "created_at",
                    "updated_at", "molecule_name"):
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole:
            return False

        molecule = self._molecules[index.row()]
        attr = self._headers[index.column()]

        try:
            UpdateClass = MODEL_UPDATE_MAPPER[molecule.group]
            update_model = UpdateClass(**{attr: value})
            up.update_model(molecule, update_model)
            setattr(molecule, attr, value)

        except Exception as e:
            print(f"Update failed: {e}")
            return False

        # GUI aktualisieren
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True

def create_editor_for_type(field_type, parent):
    if field_type == str:
        return QLineEdit(parent)

    if field_type == int:
        spin = QSpinBox(parent)
        spin.setRange(-1_000_000_000, 1_000_000_000)
        return spin

    if field_type == float:
        dspin = QDoubleSpinBox(parent)
        dspin.setRange(-1e15, 1e15)
        dspin.setDecimals(3)
        return dspin

    if field_type == bool:
        combo = QComboBox(parent)
        combo.addItem("Yes", True)
        combo.addItem("No", False)
        return combo

    if field_type == datetime.date:
        widget = QDateEdit(parent)
        widget.setCalendarPopup(True)
        widget.setDisplayFormat("yyyy-MM-dd")
        return widget

    if field_type == datetime.datetime:
        widget = QDateTimeEdit(parent)
        widget.setCalendarPopup(True)
        widget.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        return widget

    if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
        combo = QComboBox(parent)
        for e in field_type:
            combo.addItem(e.name, e)
        return combo

    return QLineEdit(parent)


def get_editor_value(editor):
    if isinstance(editor, QLineEdit):
        text = editor.text()
        return text if text != "" else None

    if isinstance(editor, QSpinBox):
        return editor.value()

    if isinstance(editor, QDoubleSpinBox):
        return editor.value()

    if isinstance(editor, QComboBox):
        return editor.currentData()

    if isinstance(editor, QDateEdit):
        qdate = editor.date()
        return datetime.date(qdate.year(), qdate.month(), qdate.day())

    if isinstance(editor, QDateTimeEdit):
        return editor.dateTime().toPython()

    return None


class TypedItemDelegate(QStyledItemDelegate):
    def __init__(self, field_type, parent=None):
        super().__init__(parent)
        self.field_type = field_type

    def createEditor(self, parent, option, index):
        return create_editor_for_type(self.field_type, parent)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)

        if value is None:
            return

        if isinstance(editor, QLineEdit):
            editor.setText(str(value))

        elif isinstance(editor, QSpinBox):
            editor.setValue(value)

        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(value)

        elif isinstance(editor, QComboBox):
            idx = editor.findData(value)
            if idx >= 0:
                editor.setCurrentIndex(idx)

        elif isinstance(editor, QDateEdit):
            editor.setDate(QDate(value.year, value.month, value.day))

        elif isinstance(editor, QDateTimeEdit):
            editor.setDateTime(QDateTime(value))

    def setModelData(self, editor, model, index):
        value = get_editor_value(editor)
        model.setData(index, value, Qt.ItemDataRole.EditRole)

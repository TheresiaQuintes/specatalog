import sys
from PyQt6 import QtWidgets
from specatalog.gui.gui_classes import MainWindow
import qdarktheme


# [MAIN LOOP]
def main():
    """Start PySpin."""
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

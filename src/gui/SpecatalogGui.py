import sys
from PyQt6 import QtWidgets
from gui_classes import MainWindow


# [MAIN LOOP]
def main():
    """Start PySpin."""
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""Main module for the cell viewer application."""

import sys
from PySide6.QtWidgets import QApplication
from .controller.MainController import MainController

def main():
    app = QApplication(sys.argv)
    controller = MainController()
    controller.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
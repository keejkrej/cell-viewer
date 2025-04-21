"""Main module for the cell viewer application."""

import sys
from PySide6.QtWidgets import QApplication
from .controller.MainController import MainController
from .model.MainModel import MainModel
from .view.MainView import MainView

def main():
    app = QApplication(sys.argv)
    
    # Create model and view instances
    model = MainModel()
    view = MainView()
    
    # Create controller with dependencies
    controller = MainController(model, view)
    controller.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
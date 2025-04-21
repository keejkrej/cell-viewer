"""Main module for the cell viewer application."""

import sys
from PySide6.QtWidgets import QApplication
from .model.MainModel import MainModel
from .view.MainView import MainView
from .controller.MainController import MainController

def main():
    app = QApplication(sys.argv)
    
    # Create model and view instances
    model = MainModel()
    view = MainView()
    
    # Create controller with dependencies
    MainController(model, view)
    
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
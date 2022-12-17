import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# import ASSController from the controller folder
from controller.ass_controller import ASSController
from model.ass_model import ASSModel
from view.ass_view import ASSView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setWindowIcon(QIcon("imgs/iib-Icon.ico"))
    model = ASSModel()
    view = ASSView()
    controller = ASSController(model, view)
    sys.exit(app.exec())

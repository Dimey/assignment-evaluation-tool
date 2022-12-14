import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ass_controller import ASSController
from ass_model import ASSModel
from ass_view import ASSView


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setWindowIcon(QIcon("imgs/iib-Icon.ico"))
    model = ASSModel()
    view = ASSView()
    controller = ASSController(model, view)
    sys.exit(app.exec())

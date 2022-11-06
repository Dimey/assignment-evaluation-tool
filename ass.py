import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

from ass_controller import ASSController
from ass_model import ASSModel
from ass_view import ASSView


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("macintosh")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    view = ASSView()
    model = ASSModel()
    controller = ASSController(model, view)
    sys.exit(app.exec())

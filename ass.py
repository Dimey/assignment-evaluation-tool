import sys
from PyQt5.QtWidgets import QApplication
from ass_view import ASSView
from ass_controller import ASSController
from ass_model import ASSModel


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("macintosh")
    view = ASSView()
    model = ASSModel()
    controller = ASSController(model, view)
    sys.exit(app.exec())

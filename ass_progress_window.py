from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QVBoxLayout
from PyQt5 import QtCore


class ProgressWindow(QWidget):
    def __init__(self, title):
        super(ProgressWindow, self).__init__()
        self.setWindowTitle(title)
        self.progressBar = QProgressBar(self)
        self.progressBar.setStyleSheet(
            "QProgressBar {border: 1px solid grey; border-radius: 5px; text-align: center;}"
        )
        self.progressBar.setFormat("")
        self.progressBar.setFixedHeight(10)

        self.progressLabel = QLabel(self)
        self.progressBar.setValue(0)
        self.progressLabel.setText("")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.progressBar)
        self.vBox.addWidget(self.progressLabel, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(self.vBox)
        self.show()

    def updateProgressInfo(self, progressValue, progressText=""):
        self.progressBar.setValue(progressValue)
        self.progressLabel.setText(progressText)
        if progressValue == 100:
            self.close()

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ASSView(QMainWindow):
    """docstring for ASSView."""

    def __init__(self):
        super(ASSView, self).__init__()

    def createUI(self, contents, overviewTableModel):
        self.setWindowTitle("Assignment Evaluator")

        self.lineEditList = []

        # Evaluation Detail Panel
        evaluationOverviewLayout = QVBoxLayout()
        twoButtonLayout = QHBoxLayout()
        self.jumpToAssignmentButton = QPushButton("Zur Abgabe")
        self.jumpPDFExportButton = QPushButton("PDF Export")
        twoButtonLayout.addWidget(self.jumpToAssignmentButton)
        twoButtonLayout.addWidget(self.jumpPDFExportButton)

        taskGroupBoxes = self.createAllTaskGroupBoxes(contents["tasks"])
        for taskGroupBox in taskGroupBoxes:
            evaluationOverviewLayout.addWidget(taskGroupBox)
        penaltyGroupBox = self.createPenaltyGroupBox(contents["penalties"])
        evaluationOverviewLayout.addWidget(penaltyGroupBox)

        self.remarkTextEdit = QPlainTextEdit()
        evaluationOverviewLayout.addWidget(self.remarkTextEdit)
        self.pointsLabel = QLabel(f"Gesamtpunktzahl\n{0} / {1+20}")
        self.pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pointsLabel.setStyleSheet("font-weight: bold")
        evaluationOverviewLayout.addWidget(self.pointsLabel)
        evaluationOverviewLayout.addLayout(twoButtonLayout)
        # evaluationOverviewLayout.insertSpacing(1,14)
        self.evaluationOverviewGroupBox = QGroupBox("Bewertungsdetails")
        self.evaluationOverviewGroupBox.setLayout(evaluationOverviewLayout)

        # Evaluation Overview
        self.overviewTable = QTableView()
        self.overviewTable.setModel(overviewTableModel)
        # self.overviewTable.setSortingEnabled(True)
        self.overviewTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overviewTable.setMinimumWidth(len(overviewTableModel._data.columns) * 100)

        # 3 Buttons below table
        threeButtonLayout = QHBoxLayout()
        self.batchPDFExportButton = QPushButton("Batch-PDF-Export")
        self.loadButton = QPushButton("Laden")
        self.saveButton = QPushButton("Speichern")
        threeButtonLayout.addWidget(self.batchPDFExportButton)
        threeButtonLayout.addWidget(self.loadButton)
        threeButtonLayout.addWidget(self.saveButton)
        tableAndButtonsLayout = QVBoxLayout()
        tableAndButtonsLayout.addWidget(self.overviewTable)
        tableAndButtonsLayout.addLayout(threeButtonLayout)

        # Bottom Part of UI
        bottomUILayout = QHBoxLayout()
        bottomUILayout.addLayout(tableAndButtonsLayout, stretch=3)
        bottomUILayout.addWidget(self.evaluationOverviewGroupBox, stretch=1)
        bottomUIWidget = QWidget()
        bottomUIWidget.setLayout(bottomUILayout)
        self.setCentralWidget(bottomUIWidget)

        for lineEdit in self.lineEditList:
            lineEdit.setText("0")

        self.configUI()
        self.show()

    def createSubTaskWidget(self, subTask):
        subTaskLabel = QLabel(subTask["subTaskTitle"])
        subTaskGrad = QLineEdit()
        self.lineEditList.append(subTaskGrad)
        subTaskGrad.setAlignment(Qt.AlignmentFlag.AlignRight)
        subTaskGrad.setFixedWidth(25)
        subTaskMaxPointsLabel = QLabel(f'/ {subTask["subTaskMaxPoints"]}')
        subTaskMaxPointsLabel.setFixedWidth(25)

        subTaskLayout = QHBoxLayout()
        subTaskLayout.addWidget(subTaskLabel)
        subTaskLayout.addWidget(subTaskGrad)
        subTaskLayout.addWidget(subTaskMaxPointsLabel)
        subTaskLayout.insertStretch(1)
        subTaskLayout.setContentsMargins(0, 0, 0, 0)

        subTaskWidget = QWidget()
        subTaskWidget.setLayout(subTaskLayout)

        return subTaskWidget

    def createPenaltyWidget(self, penalty):
        penaltyLabel = QLabel(penalty["penaltyTitle"])
        penaltyLineEdit = QLineEdit()
        self.lineEditList.append(penaltyLineEdit)
        penaltyLineEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        penaltyLineEdit.setFixedWidth(25)

        penaltyLayout = QHBoxLayout()
        penaltyLayout.addWidget(penaltyLabel)
        penaltyLayout.addWidget(penaltyLineEdit)
        penaltyLayout.insertStretch(1)
        penaltyLayout.setContentsMargins(0, 0, 0, 0)

        penaltyWidget = QWidget()
        penaltyWidget.setLayout(penaltyLayout)
        return penaltyWidget

    def createPenaltyGroupBox(self, penalties):
        penaltiesLayout = QVBoxLayout()
        for penalty in penalties:
            penaltiesLayout.addWidget(self.createPenaltyWidget(penalty))
        penaltyGroupBox = QGroupBox("Abzüge")
        penaltyGroupBox.setLayout(penaltiesLayout)
        return penaltyGroupBox

    def createTaskGroupBox(self, task):
        taskLayout = QVBoxLayout()
        for subTask in task["subTasks"]:
            taskLayout.addWidget(self.createSubTaskWidget(subTask))
        taskGroupBox = QGroupBox(task["taskTitle"])
        taskGroupBox.setLayout(taskLayout)
        return taskGroupBox

    def createAllTaskGroupBoxes(self, tasks):
        allTaskGroupBoxes = []
        for task in tasks:
            allTaskGroupBoxes.append(self.createTaskGroupBox(task))
        return allTaskGroupBoxes

    def createImportGroupBox(self):
        pass

    def createStatsGroupBox(self):
        pass

    def configUI(self):
        # Clicking on a single cell will always select the whole row
        self.overviewTable.setSelectionBehavior(QTableView.SelectRows)

        # Useful column resizing for long student names
        header = self.overviewTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

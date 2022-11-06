from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ASSView(QMainWindow):
    """Generate docstring for configUI"""

    def __init__(self):
        super(ASSView, self).__init__()

    def createUI(self, contents, overviewTableModel):
        self.setWindowTitle("Assignment Evaluator")

        self.spinBoxList = []

        # Evaluation Detail Panel
        evaluationOverviewLayout = QVBoxLayout()
        twoButtonLayout = QHBoxLayout()
        self.jumpToAssignmentButton = QPushButton("Zur Abgabe")
        # set icon
        self.jumpToAssignmentButton.setIcon(QIcon("icons/arrowshape.turn.up.forward@4x.png"))
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
        self.pointsLabel = QLabel(f"Gesamtpunktzahl\n{0} / {30}")
        self.pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pointsLabel.setStyleSheet("font-weight: bold")
        evaluationOverviewLayout.addWidget(self.pointsLabel)
        evaluationOverviewLayout.addLayout(twoButtonLayout)
        # evaluationOverviewLayout.insertSpacing(1,14)
        self.evaluationOverviewGroupBox = QGroupBox("Bewertungsdetails")
        self.evaluationOverviewGroupBox.setLayout(evaluationOverviewLayout)

        # Evaluation Overview
        self.overviewTable = QTableView()
        self.overviewTable.setSortingEnabled(True)
        self.overviewTable.setModel(overviewTableModel)
        # self.overviewTable.setSortingEnabled(True)
        self.overviewTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overviewTable.setMinimumWidth(len(overviewTableModel._data.columns) * 100)

        # 3 Buttons below table
        threeButtonLayout = QHBoxLayout()
        self.batchPDFExportButton = QPushButton("Batch-PDF-Export")
        self.batchPDFExportButton.setIcon(QIcon("icons/square.and.arrow.up.on.square@4x.png"))
        self.loadButton = QPushButton("Laden")
        self.saveButton = QPushButton("Speichern")
    
        threeButtonLayout.addWidget(self.batchPDFExportButton)
        threeButtonLayout.addWidget(self.loadButton)
        threeButtonLayout.addWidget(self.saveButton)
        tableAndButtonsLayout = QVBoxLayout()
        # TABLE TITLE
        self.tableTitleLabel = QLabel(f"Bewertungsübersicht")
        font = self.tableTitleLabel.font()
        font.setPointSize(18)  
        self.tableTitleLabel.setFont(font)
        self.tableTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableTitleLabel.setStyleSheet("font-weight: bold")
        self.tableTitleLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        tableAndButtonsLayout.addWidget(self.tableTitleLabel)
        tableAndButtonsLayout.addWidget(self.overviewTable)
        tableAndButtonsLayout.addLayout(threeButtonLayout)
        
        ##### UPPER PART OF UI #####
        # create 

        ##### BOTTOM PART OF UI #####
        bottomUILayout = QHBoxLayout()
        bottomUILayout.addLayout(tableAndButtonsLayout, stretch=3)
        bottomUILayout.addWidget(self.evaluationOverviewGroupBox, stretch=0)
        bottomUIWidget = QWidget()
        bottomUIWidget.setLayout(bottomUILayout)
        self.setCentralWidget(bottomUIWidget)

        self.configUI()
        self.show()

    def createSubTaskWidget(self, subTask):
        subTaskLabel = QLabel(subTask["subTaskTitle"])
        subTaskGrad = QSpinBox()
        subTaskGrad.setAlignment(Qt.AlignmentFlag.AlignRight)
        subTaskGrad.setFixedWidth(40)
        subTaskGrad.setValue(0)
        subTaskGrad.setMaximum(subTask["subTaskMaxPoints"])

        self.spinBoxList.append(subTaskGrad)
        subTaskMaxPointsLabel = QLabel(f'max. {subTask["subTaskMaxPoints"]}')
        # change color of subTaskMaxPointsLabel to grey
        subTaskMaxPointsLabel.setStyleSheet("color: grey;background-color: lightgrey; border-radius: 5px; padding: 2px;")
        font = subTaskMaxPointsLabel.font()
        font.setPointSize(10)
        subTaskMaxPointsLabel.setFont(font)
        subTaskMaxPointsLabel.setFixedWidth(45)

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
        penaltySpinBox = QSpinBox()
        penaltySpinBox.setValue(0)
        # set the prefix to minus
        penaltySpinBox.setPrefix("-")
        penaltySpinBox.setAlignment(Qt.AlignmentFlag.AlignRight)
        penaltySpinBox.setFixedWidth(40)
        self.spinBoxList.append(penaltySpinBox)

        penaltyLayout = QHBoxLayout()
        penaltyLayout.addWidget(penaltyLabel)
        penaltyLayout.addWidget(penaltySpinBox)
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
        return [self.createTaskGroupBox(task) for task in tasks]

    def createImportGroupBox(self):
        # create a hbox containing a label, a line edit and a button
        importLayout = QHBoxLayout()
        importLayout.addWidget(QLabel("Arbeitsverzeichnis"))
        self.workDirPathLineEdit = QLineEdit()
        importLayout.addWidget(self.workDirPathLineEdit)
        self.changeWorkDirButton = QPushButton("Ändern")
        importLayout.addWidget(self.changeWorkDirButton)
        self.importGroupBox = QGroupBox("Import")
        self.importGroupBox.setLayout(importLayout)
        return self.importGroupBox
        

    def createStatsGroupBox(self):
        # create a groupbox containing a vstack which
        # contains in every row two labels
        statsLayout = QVBoxLayout()
        self.statsLabelList = []
        for i in range(3):
            rowLayout = QHBoxLayout()
            rowLayout.addWidget(QLabel("Label"))
            rowLayout.addWidget(QLabel("0"))
            statsLayout.addLayout(rowLayout)
            self.statsLabelList.append(rowLayout.itemAt(1).widget())
        self.statsGroupBox = QGroupBox("Statistik")
        self.statsGroupBox.setLayout(statsLayout)
        return self.statsGroupBox

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
    
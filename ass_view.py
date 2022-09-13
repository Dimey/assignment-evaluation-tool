import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ass_overviewtable_model import *


class ASSView(QMainWindow):
    """docstring for ASSView."""

    def __init__(self):
        super(ASSView, self).__init__()
        self.createUI()
        self.configUI()
        self.show()

    def createUI(self):
        self.setWindowTitle("Assignment Evaluator")
        json_file_path = "json-mock-data/tasks.json"
        with open(json_file_path, 'r') as j:
            contents = json.loads(j.read())

        # Evaluation Detail Panel
        evaluationOverviewLayout = QVBoxLayout()
        twoButtonLayout = QHBoxLayout()
        self.jumpToAssignmentButton = QPushButton('Zur Abgabe')
        self.jumpPDFExportButton = QPushButton('PDF Export')
        twoButtonLayout.addWidget(self.jumpToAssignmentButton)
        twoButtonLayout.addWidget(self.jumpPDFExportButton)
        evaluationOverviewLayout.addLayout(twoButtonLayout)
        taskGroupBoxes = self.createAllTaskGroupBoxes(contents['tasks'])
        for taskGroupBox in taskGroupBoxes:
            evaluationOverviewLayout.addWidget(taskGroupBox)
        penaltyGroupBox = self.createPenaltyGroupBox(contents['penalties'])
        evaluationOverviewLayout.addWidget(penaltyGroupBox)
        evaluationOverviewLayout.insertSpacing(1,14)
        self.remarkTextEdit = QPlainTextEdit()
        evaluationOverviewLayout.addWidget(self.remarkTextEdit)
        self.pointsLabel = QLabel(f'Gesamtpunktzahl\n0 / {1+20}')
        self.pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pointsLabel.setStyleSheet("font-weight: bold")
        evaluationOverviewLayout.addWidget(self.pointsLabel)
        self.evaluationOverviewGroupBox = QGroupBox('Bewertungsdetails')
        self.evaluationOverviewGroupBox.setLayout(evaluationOverviewLayout)

        # Evaluation Overview
        self.overviewTable = QtWidgets.QTableView()
        data = pd.DataFrame([], columns = ['Nachname', 'Vorname', 'Abgabe', 'Punkte', 'Bestanden'])
        data.loc[1771189] = [1, 2, 3, 4, 5]
        data.loc[1771189] = [1, 'Nein', 3, 4, 5]
        data.loc[2334334] = [1, 'Nein', 3, 4, 5]
        self.overviewTableModel = OverviewTableModel(data)
        self.overviewTable.setModel(self.overviewTableModel)
        #self.overviewTable.setSortingEnabled(True)
        self.overviewTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.overviewTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overviewTable.setMinimumWidth(len(data.columns)*100)
        #self.overviewTable.resizeColumnsToContents()

        # Bottom Part of UI
        bottomUILayout = QHBoxLayout()
        bottomUILayout.addWidget(self.overviewTable, stretch=3)
        bottomUILayout.addWidget(self.evaluationOverviewGroupBox, stretch=1)
        bottomUIWidget = QWidget()
        bottomUIWidget.setLayout(bottomUILayout)
        self.setCentralWidget(bottomUIWidget)

    def createSubTaskWidget(self, subTask):
        subTaskLabel = QLabel(subTask['subTaskTitle'])
        subTaskGrad = QLineEdit()
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
        penaltyLabel = QLabel(penalty['penaltyTitle'])
        penaltyLineEdit = QLineEdit()
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
        penaltyGroupBox = QGroupBox('Abzüge')
        penaltyGroupBox.setLayout(penaltiesLayout)
        return penaltyGroupBox

    def createTaskGroupBox(self, task):
        taskLayout = QVBoxLayout()
        for subTask in task['subTasks']:
            taskLayout.addWidget(self.createSubTaskWidget(subTask))
        taskGroupBox = QGroupBox(task['taskTitle'])
        taskGroupBox.setLayout(taskLayout)
        return taskGroupBox

    def createAllTaskGroupBoxes(self, tasks):
        allTaskGroupBoxes = []
        for task in tasks:
            allTaskGroupBoxes.append(self.createTaskGroupBox(task))
        return allTaskGroupBoxes

    def configUI(self):
        pass

    def savePlot(self):
        pass

    
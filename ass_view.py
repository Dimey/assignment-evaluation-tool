from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

import os
import subprocess


class ASSView(QMainWindow):
    """Generate docstring for configUI"""

    def __init__(self):
        super(ASSView, self).__init__()

    def createUI(self, contents, overviewTableModel):
        self.setWindowTitle("Assignment Evaluator")
        self.contents = contents
        self.spinBoxList = []

        # Evaluation Detail Panel
        evaluationOverviewLayout = QVBoxLayout()
        twoButtonLayout = QHBoxLayout()
        self.jumpToAssignmentButton = QPushButton("Zur Abgabe")
        self.jumpToAssignmentButton.setIcon(
            QIcon("icons/arrowshape.turn.up.forward@4x.png")
        )
        self.jumpPDFExportButton = QPushButton("PDF Export")
        twoButtonLayout.addWidget(self.jumpToAssignmentButton)
        twoButtonLayout.addWidget(self.jumpPDFExportButton)

        taskGroupBoxes = self.createAllTaskGroupBoxes(self.contents["tasks"])
        for taskGroupBox in taskGroupBoxes:
            evaluationOverviewLayout.addWidget(taskGroupBox)
        penaltyGroupBox = self.createPenaltyGroupBox(self.contents["penalties"])
        evaluationOverviewLayout.addWidget(penaltyGroupBox)

        self.remarkTextEdit = QPlainTextEdit()
        # set placeholder text in gray
        self.remarkTextEdit.setPlaceholderText("Bemerkungen")
        evaluationOverviewLayout.addWidget(self.remarkTextEdit)
        # self.pointsLabel = QLabel(f"Gesamtpunktzahl\n{0} / {30}")
        # self.pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.pointsLabel.setStyleSheet("font-weight: bold")
        # evaluationOverviewLayout.addWidget(self.pointsLabel)
        evaluationOverviewLayout.addLayout(twoButtonLayout)
        self.evaluationOverviewGroupBox = GroupBox("Bewertung abgeschlossen")
        self.evaluationOverviewGroupBox.setCheckable(True)
        self.evaluationOverviewGroupBox.setLayout(evaluationOverviewLayout)
        self.evaluationOverviewGroupBox.setEnabled(False)

        # Evaluation Overview
        self.overviewTable = QTableView()
        self.overviewTable.setSortingEnabled(True)
        self.overviewTable.setModel(overviewTableModel)
        self.overviewTable.setSortingEnabled(True)
        self.overviewTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overviewTable.setMinimumWidth(len(overviewTableModel._data.columns) * 100)

        # 3 Buttons below table
        threeButtonLayout = QHBoxLayout()
        self.batchPDFExportButton = QPushButton("Batch-PDF-Export")
        # self.batchPDFExportButton.setIcon(QIcon("icons/square.and.arrow.up.on.square@4x.png"))
        self.loadButton = QPushButton("Laden")
        self.saveButton = QPushButton("Speichern")

        threeButtonLayout.addWidget(self.loadButton)
        threeButtonLayout.addWidget(self.saveButton)
        threeButtonLayout.addWidget(self.batchPDFExportButton)
        # deactive buttons
        self.batchPDFExportButton.setEnabled(False)
        self.saveButton.setEnabled(False)
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
        # create hbox containing importgroupbox and statsgroupbox
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(self.createImportGroupBox(), stretch=3)

        # create hbox containing statsgroupbox and a spinbox
        statsLayout = QVBoxLayout()
        statsLayout.addWidget(self.createStatsGroupBox())
        statsLayout.addWidget(self.createPassThresholdSpinBox())
        # no margins for the statsLayout
        statsLayout.setContentsMargins(0, 0, 0, 0)

        upperLayout.addLayout(statsLayout, stretch=1)
        # create widget
        upperWidget = QWidget()
        upperWidget.setLayout(upperLayout)
        # upperLayout.setStretch(0, 1)

        ##### BOTTOM PART OF UI #####
        bottomUILayout = QHBoxLayout()
        bottomUILayout.addLayout(tableAndButtonsLayout, stretch=3)
        bottomUILayout.addWidget(self.evaluationOverviewGroupBox, stretch=1)
        bottomUIWidget = QWidget()
        bottomUIWidget.setLayout(bottomUILayout)

        # combine bottom and upper part in a vbox and set as central widget
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(upperWidget)
        mainLayout.addWidget(bottomUIWidget)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        self.configUI()
        self.show()

    def createPassThresholdSpinBox(self):
        # create widget with label and spinbox
        pointsWidget = QWidget()
        pointsLayout = QHBoxLayout()
        pointsLabel = QLabel("Bestehensgrenze")
        pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pointsLayout.addWidget(pointsLabel)
        self.passThresholdSpinBox = QSpinBox()
        maxPoints = self.contents["maxPoints"]
        self.passThresholdSpinBox.setRange(0, maxPoints)
        self.passThresholdSpinBox.setValue(int(maxPoints / 2))
        self.passThresholdSpinBox.setSingleStep(1)
        self.passThresholdSpinBox.setSuffix(f" / {maxPoints}")
        self.passThresholdSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pointsLayout.addWidget(self.passThresholdSpinBox)
        pointsLayout.insertStretch(1)
        pointsLayout.setContentsMargins(10, 0, 10, 0)
        pointsWidget.setLayout(pointsLayout)
        return pointsWidget

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
        subTaskMaxPointsLabel.setStyleSheet(
            "color: grey;background-color: lightgrey; border-radius: 5px; padding: 2px;"
        )
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
        workDirPathLayout = QHBoxLayout()
        workDirPathLayout.addWidget(QLabel("Arbeitsverzeichnis"))
        self.workDirPathLineEdit = QLineEdit()
        # line edit should not be editable
        self.workDirPathLineEdit.setReadOnly(True)
        self.workDirPathLineEdit.setStyleSheet("color: grey;")
        workDirPathLayout.addWidget(self.workDirPathLineEdit)
        self.changeWorkDirButton = QPushButton("Ändern")
        workDirPathLayout.addWidget(self.changeWorkDirButton)

        # create vbox containing workDirPathLayout and three horizontally aligned buttons
        importLayout = QVBoxLayout()
        importLayout.addLayout(workDirPathLayout)
        # insert an hline between workDirPathLayout and the buttons
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: lightgrey;")
        importLayout.addWidget(line)
        importLayout.addLayout(self.createImportButtons())
        importLayout.addLayout(self.createImportInfoLayout())

        self.importGroupBox = QGroupBox("Import")
        self.importGroupBox.setLayout(importLayout)
        return self.importGroupBox

    def createLabelWithIcon(self, text, iconPath):
        # create hbox with label and icon
        labelWithIconLayout = QHBoxLayout()
        # center the label
        labelWithIconLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        textLabel = QLabel(text)
        # alternative color: #D6D6D6
        textLabel.setStyleSheet(
            "background-color: rgb(235, 77, 62); border-radius: 8px; padding: 4px; color: white;"
        )
        # text should be centered
        textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labelWithIconLayout.addWidget(textLabel)
        label = QLabel(text)
        icon = QIcon(iconPath)
        label.setPixmap(icon.pixmap(20, 20))
        labelWithIconLayout.addWidget(label)

        return labelWithIconLayout, textLabel

    def createImportInfoLayout(self):
        # create a hbox with three labels with icons
        importInfoLayout = QHBoxLayout()
        tucanCountLabelLayout, self.tucanCountLabel = self.createLabelWithIcon(
            "0", "icons/person.fill.checkmark@4x.png"
        )
        importInfoLayout.addLayout(tucanCountLabelLayout)
        moodleCountLabelLayout, self.moodleCountLabel = self.createLabelWithIcon(
            "0", "icons/person.fill.checkmark@4x.png"
        )
        importInfoLayout.addLayout(moodleCountLabelLayout)
        (
            submissionCountLabelLayout,
            self.submissionCountLabel,
        ) = self.createLabelWithIcon("0", "icons/folder.badge.person.crop@4x.png")
        importInfoLayout.addLayout(submissionCountLabelLayout)
        return importInfoLayout

    def createImportButtons(self):
        # create a horizontal layout containing three buttons
        importButtonsLayout = QHBoxLayout()
        self.tucanButton = QPushButton("TUCaN Teilnehmer")
        importButtonsLayout.addWidget(self.tucanButton)
        self.moodleButton = QPushButton("Moodle Teilnehmer")
        importButtonsLayout.addWidget(self.moodleButton)
        self.importSubmissionsButton = QPushButton("Abgaben")
        self.importSubmissionsButton.setEnabled(False)
        importButtonsLayout.addWidget(self.importSubmissionsButton)
        return importButtonsLayout

    def createStatsGroupBox(self):
        # create a groupbox containing a vstack which
        # contains in every row two labels
        statsLayout = QVBoxLayout()
        self.statsLabelList = []
        statsLabel = ["Bewertet", "Bestanden", "Ø Punkte"]
        statsValues = ["0 %", "0 %", "0"]
        for i in range(3):
            rowLayout = QHBoxLayout()
            rowLayout.addWidget(QLabel(statsLabel[i]))
            rowLayout.addWidget(QLabel(statsValues[i]))
            rowLayout.insertStretch(1)
            statsLayout.addLayout(rowLayout)
            self.statsLabelList.append(rowLayout.itemAt(2).widget())
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

    # FUNCTIONAL STUFF
    def setActiveStatusOfWidget(self, widget, isActive):
        widget.setEnabled(isActive)

    def updateWorkDirLineEdit(self, path):
        self.workDirPathLineEdit.setText(path)

    def openFileDialog(self, ext, name):
        return QFileDialog.getOpenFileName(
            self,
            f"Öffne die {ext}-Datei",
            filter=f"{ext}-Dateien k(*{name}*.{ext}) ;; Alle Dateien (*)",
        )

    def openFolderDialog(self, title):
        return QFileDialog.getExistingDirectory(self, caption=title)

    def updateLabel(self, labels, newValues):
        for i in range(len(labels)):
            labels[i].setText(str(newValues[i]))

    def openFileExplorer(self, path):
        if os.name == "nt":
            winPath = path.replace("/", "\\")
            subprocess.call(f"explorer {winPath}")
        else:
            subprocess.call(["open", "-R", path])

    def updateSpinBoxes(self, data):
        self.setActiveStatusOfWidget(self.jumpToAssignmentButton, type(data[-2]) == str)
        for idx, spinBox in enumerate(self.spinBoxList):
            spinBox.setValue(data[idx])
        self.remarkTextEdit.setPlainText(data[-3])
        self.evaluationOverviewGroupBox.setChecked(not data[-1])


class GroupBox(QtWidgets.QGroupBox):
    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionGroupBox()
        self.initStyleOption(option)
        if self.isCheckable():
            option.state &= ~QtWidgets.QStyle.State_Off & ~QtWidgets.QStyle.State_On
            option.state |= (
                QtWidgets.QStyle.State_Off
                if self.isChecked()
                else QtWidgets.QStyle.State_On
            )
        painter.drawComplexControl(QtWidgets.QStyle.CC_GroupBox, option)

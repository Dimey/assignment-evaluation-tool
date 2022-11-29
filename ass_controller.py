from functools import partial
from ass_overviewtable_model import OverviewTableModel


class ASSController:
    """docstring for ASSController."""

    def __init__(self, model, view):
        super(ASSController, self).__init__()
        self.view = view
        self.model = model

        # load assignment defining json file
        self.assignmentDescription = model.loadAssignmentDescription()
        self.overviewTableViewModel = OverviewTableModel(self.assignmentDescription)
        self.view.createUI(self.assignmentDescription, self.overviewTableViewModel)

        self.initializeUI()

        # Connect signals and slots
        self.connectSignals()

    def initializeUI(self):
        self.view.tucanButton.setFocus()  # has no effect yet
        self.view.updateWorkDirLineEdit(path=self.model.workDir)

    def connectSignals(self):
        # signals through user interaction
        for idx, spinBox in enumerate(self.view.spinBoxList):
            spinBox.valueChanged.connect(partial(self.savePoints, spinBox, idx))
        self.view.loadButton.clicked.connect(self.loadSaveFile)
        self.view.saveButton.clicked.connect(self.saveFile)
        self.view.tucanButton.clicked.connect(partial(self.openEntryList, "tucan"))
        self.view.moodleButton.clicked.connect(partial(self.openEntryList, "moodle"))
        self.view.importSubmissionsButton.clicked.connect(self.importSubmissions)
        self.view.overviewTable.selectionModel().selectionChanged.connect(
            self.updateSpinBoxList
        )
        self.view.jumpToAssignmentButton.clicked.connect(self.jumpToAssignment)
        self.view.remarkTextEdit.textChanged.connect(self.saveRemarks)
        self.view.passThresholdSpinBox.valueChanged.connect(self.changePassThreshold)
        self.view.evaluationOverviewGroupBox.clicked.connect(self.saveEvalStatus)

        # signals from model
        self.overviewTableViewModel.labelStat0Signal.connect(
            self.view.statsLabelList[0].setText
        )
        self.overviewTableViewModel.labelStat1Signal.connect(
            self.view.statsLabelList[1].setText
        )
        self.overviewTableViewModel.labelStat2Signal.connect(
            self.view.statsLabelList[2].setText
        )

    def openEntryList(self, typeOfList):
        otherList = "tucan" if typeOfList == "moodle" else "moodle"
        filename = self.view.openFileDialog("xlsx", typeOfList)
        if typeOfList in filename[0].lower():
            if typeOfList == "tucan":
                self.model.loadTucanList(filename[0])
                self.view.updateLabel(
                    [self.view.tucanCountLabel], [self.model.tucanList.shape[0]]
                )
            else:
                self.model.loadMoodleList(filename[0])
                self.view.updateLabel(
                    [self.view.moodleCountLabel], [self.model.moodleList.shape[0]]
                )
            if hasattr(self.model, f"{otherList}List"):
                self.overviewTableViewModel.populateDataModel(
                    self.model.tucanList, self.model.moodleList
                )
                self.view.importSubmissionsButton.setEnabled(True)

    def importSubmissions(self):
        path = self.view.openFolderDialog("Wähle Abgaben-Ordner aus.")
        if path:
            # copy selected folder (param1) to workdir/x (param2)
            pathList = self.model.copySubmissionsToDir(path, "GMV-Testat/Abgaben")
            self.overviewTableViewModel.populateDataModelWithPaths(pathList)
            self.view.updateLabel([self.view.submissionCountLabel], [len(pathList)])
            self.view.overviewTable.selectRow(0)
            self.selectedMatrikel = self.overviewTableViewModel.getIndex(0)
            self.view.evaluationOverviewGroupBox.setEnabled(True)
            self.view.saveButton.setEnabled(True)
            self.view.updateLabel(
                [
                    self.view.statsLabelList[0],
                ],
                [
                    f"{self.overviewTableViewModel.getEvaluatedCount()} von {self.overviewTableViewModel.getSubmissionCount()}"
                ],
            )

    def updateSpinBoxList(self):
        self.selectedMatrikel = self.overviewTableViewModel.getIndex(
            self.view.overviewTable.selectionModel().selectedRows()[0].row()
        )
        data = self.overviewTableViewModel.getEvalData(self.selectedMatrikel)
        self.view.updateSpinBoxes(data)

    def jumpToAssignment(self):
        submPath = self.overviewTableViewModel.getPath(self.selectedMatrikel)
        self.view.openFileExplorer(submPath)

    def savePoints(self, lineEditObj, idx):
        self.overviewTableViewModel.updateValueForCriteria(
            idx, self.selectedMatrikel, self.view.spinBoxList[idx].value()
        )
        self.view.updateLabel(
            [self.view.statsLabelList[1]],
            [
                f"{100*self.overviewTableViewModel.getPassedCount() / self.overviewTableViewModel.getSubmissionCount():.1f} %"
            ],
        )

    def saveRemarks(self):
        self.overviewTableViewModel.updateRemarkText(
            self.selectedMatrikel, self.view.remarkTextEdit.toPlainText()
        )

    def loadSaveFile(self):
        data = self.model.loadSaveFileFromJSON()
        if data is not None:
            self.overviewTableViewModel.setData(data)
            self.view.evaluationOverviewGroupBox.setEnabled(True)
            self.view.saveButton.setEnabled(True)
            participantCount = f"{len(self.overviewTableViewModel.getData())}+"
            submCount = self.overviewTableViewModel.getSubmissionCount()
            self.view.updateLabel(
                [
                    self.view.tucanCountLabel,
                    self.view.moodleCountLabel,
                    self.view.submissionCountLabel,
                    self.view.statsLabelList[0],
                    self.view.statsLabelList[1],
                    self.view.statsLabelList[2],
                ],
                [
                    participantCount,
                    participantCount,
                    str(submCount),
                    f"{self.overviewTableViewModel.getEvaluatedCount()} von {submCount}",
                    f"{100*self.overviewTableViewModel.getPassedCount() / submCount:.1f} %",
                    f"{self.overviewTableViewModel.getAvgPoints():.1f}",
                ],
            )
            self.view.overviewTable.selectRow(0)
            self.selectedMatrikel = self.overviewTableViewModel.getIndex(0)

    def saveFile(self):
        self.model.saveDataToJSON(self.overviewTableViewModel.getData())

    def changePassThreshold(self):
        self.overviewTableViewModel.setPassThreshold(
            self.view.passThresholdSpinBox.value()
        )

    def saveEvalStatus(self):
        evaluatedCount = self.overviewTableViewModel.updateEvalStatus(
            self.selectedMatrikel, not self.view.evaluationOverviewGroupBox.isChecked()
        )

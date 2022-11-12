from functools import partial
import random
import pandas as pd


class ASSController:
    """docstring for ASSController."""

    def __init__(self, model, view):
        super(ASSController, self).__init__()
        self.view = view
        self.model = model

        # load assignment defining json file
        self.assignmentDescription = model.loadAssignmentDescription()
        self.overviewTableViewModel = model.createOverviewTableModel()
        self.view.createUI(self.assignmentDescription, self.overviewTableViewModel)
        self.overviewTableViewModel.extendDataModellBySubTasks(
            self.assignmentDescription
        )

        self.initializeUI()

        # Connect signals and slots
        self.connectSignals()

    def initializeUI(self):
        self.view.tucanButton.setFocus()  # has no effect yet
        self.view.updateWorkDirLineEdit(path=self.model.workDir)

    def connectSignals(self):
        # connect textfields to savePoints method
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

    def openEntryList(self, typeOfList):
        otherList = "tucan" if typeOfList == "moodle" else "moodle"
        filename = self.view.openFileDialog("xlsx", typeOfList)
        if typeOfList in filename[0].lower():
            if typeOfList == "tucan":
                self.model.loadTucanList(filename[0])
                self.view.updateLabel(
                    self.view.tucanCountLabel, self.model.tucanList.shape[0]
                )
            else:
                self.model.loadMoodleList(filename[0])
                self.view.updateLabel(
                    self.view.moodleCountLabel, self.model.moodleList.shape[0]
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
            # populate data model with paths and set subm. status
            self.overviewTableViewModel.populateDataModelWithPaths(pathList)
            self.view.updateLabel(self.view.submissionCountLabel, len(pathList))
            self.view.overviewTable.selectRow(0)
            self.selectedMatrikel = self.overviewTableViewModel.getIndex(0)
            self.view.evaluationOverviewGroupBox.setEnabled(True)

    def updateSpinBoxList(self):
        self.selectedMatrikel = self.overviewTableViewModel.getIndex(
            self.view.overviewTable.selectionModel().selectedRows()[0].row()
        )
        # get data for matrikel number from data model and update spinboxes
        # data = self.overviewTableViewModel.getDataForMatrikel(self.selectedMatrikel)
        print(self.selectedMatrikel)

    def jumpToAssignment(self):
        submPath = self.overviewTableViewModel.getPath(self.selectedMatrikel)
        self.view.openFileExplorer(submPath)

    def loadSaveFile(self):
        pass

    def saveFile(self):
        pass

    def savePoints(self, lineEditObj, idx):
        print(f"Save points in QLineEdit Nr.{idx+1}")

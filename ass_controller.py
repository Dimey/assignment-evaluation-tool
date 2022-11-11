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

        self.selectedRow = 0

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
            self.view.updateLabel(self.view.submissionCountLabel, len(pathList))
            # populate data model with paths and set subm. status
            self.overviewTableViewModel.populateDataModelWithPaths(pathList)

    def loadSaveFile(self):
        pass

    def saveFile(self):
        pass

    def savePoints(self, lineEditObj, idx):
        print(f"Save points in QLineEdit Nr.{idx+1}")

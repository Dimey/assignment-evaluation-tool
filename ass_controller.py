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

    def openEntryList(self, typeOfList):
        otherList = "tucan" if typeOfList == "moodle" else "moodle"
        try:
            filename = self.view.openFileDialog("xlsx")
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
                    # self.view.fuelleBewertungsUebersicht(
                    #     self.model.bewertungsuebersicht
                    # )
            else:
                self.view.falscheListeFenster(typeOfList)
        except:
            print(f"Die {typeOfList}-Liste konnte nicht geladen werden.")

    def loadSaveFile(self):
        self.overviewTableViewModel.makeRandomEntry()

    def saveFile(self):
        pass

    def savePoints(self, lineEditObj, idx):
        print(f"Save points in QLineEdit Nr.{idx+1}")

from functools import partial
import random


class ASSController:
    """docstring for ASSController."""

    def __init__(self, model, view):
        super(ASSController, self).__init__()
        self.view = view
        self.model = model

        # load assignment defining json file
        self.assignmentDescription = model.loadAssignmentDescription()

        self.overviewTableViewModel = model.createOverviewTableModel(
            self.assignmentDescription
        )

        self.view.createUI(self.assignmentDescription, self.overviewTableViewModel)

        # Connect signals and slots
        self.connectSignals()

    def connectSignals(self):
        # connect textfields to savePoints method
        for idx, spinBox in enumerate(self.view.spinBoxList):
            spinBox.editingFinished.connect(partial(self.savePoints, spinBox, idx))

        # connect load button to add-entry-function
        self.view.loadButton.clicked.connect(self.addEntry)

    def addEntry(self):
        # create random integer with 7 digits
        randomInt = random.randint(1000000, 9999999)

        self.overviewTableViewModel._data.at[1234567, "Criteria 1"] = randomInt
        self.overviewTableViewModel._data.at[1234567, "Criteria 2"] = randomInt
        self.overviewTableViewModel.layoutChanged.emit()
        print(self.overviewTableViewModel._data.loc[1234567])

    def savePoints(self, lineEditObj, idx):
        print(f"Save points in QLineEdit Nr.{idx+1}")

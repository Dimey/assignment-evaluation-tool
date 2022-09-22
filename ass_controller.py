import json
import pandas as pd

from functools import partial

from ass_overviewtable_model import *


class ASSController:
    """docstring for ASSController."""

    def __init__(self, model, view):
        super(ASSController, self).__init__()
        self.view = view
        self.model = model

        self.createOverviewTableModel()
        self.initializeModel()
        self.view.createUI(self.contents, self.overviewTableViewModel)

        # Connect signals and slots
        self.connectSignals()

    def createOverviewTableModel(self):
        json_file_path = "json-mock-data/tasks.json"
        with open(json_file_path, "r") as j:
            self.contents = json.loads(j.read())
        self.data = pd.DataFrame(
            [], columns=["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        )
        subTaskCount = 0
        for task in self.contents["tasks"]:
            subTaskCount += len(task["subTasks"])
        columnNames = [f"criteria{idx+1}" for idx in range(subTaskCount)]
        dataCriteria = pd.DataFrame([], columns=columnNames)
        self.data.loc[1771189] = ["Haas", "Dimitri", "Ja", 14, "Ja"]
        self.data.loc[2334334] = ["Wagenbach", "Lars", "Fehler", 0, "Nein"]
        self.overviewTableViewModel = OverviewTableModel(self.data)

    def initializeModel(self):
        pass

    def connectSignals(self):
        for idx, lineEdit in enumerate(self.view.lineEditList):
            lineEdit.editingFinished.connect(partial(self.savePoints, lineEdit, idx))

    def savePoints(self, lineEditObj, idx):
        print(f"Save points in QLineEdit Nr.{idx+1}")

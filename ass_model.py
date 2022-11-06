import json

import pandas as pd

from ass_overviewtable_model import *


class ASSModel:
    """docstring for ASSModell."""

    def __init__(self):
        super(ASSModel, self).__init__()

    def loadAssignmentDescription(self):
        json_file_path = "json-mock-data/tasks.json"
        with open(json_file_path, "r") as j:
            return json.loads(j.read())

    def createOverviewTableModel(self, assignmentDescription):
        self.data = pd.DataFrame(
            [], columns=["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        )
        subTaskCount = 0
        for task in assignmentDescription["tasks"]:
            subTaskCount += len(task["subTasks"])
        columnNames = [f"Criteria {idx+1}" for idx in range(subTaskCount)]
        dataCriteria = pd.DataFrame([], columns=columnNames)
        # self.data = pd.concat([self.data, dataCriteria], axis=1)
        self.data.loc[1234567, ["Nachname", "Vorname"]] = ["Haas", "Dimitri"]
        self.data.loc[1234568, ["Nachname", "Vorname"]] = ["Wagenbach", "Lars"]
        print(self.data)
        return OverviewTableModel(self.data)

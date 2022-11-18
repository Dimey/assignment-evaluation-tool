import json
import os
from shutil import copytree

import pandas as pd

from ass_overviewtable_model import *


class ASSModel:
    """docstring for ASSModell."""

    def __init__(self):
        super(ASSModel, self).__init__()
        self.workDir = os.path.abspath(os.getcwd())

    def loadAssignmentDescription(self):
        json_file_path = "json-mock-data/tasks.json"
        with open(json_file_path, "r") as j:
            return json.loads(j.read())

    def createOverviewTableModel(self):
        self.data = pd.DataFrame(
            [], columns=["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        )
        return OverviewTableModel(self.data)

    def changeWorkDir(self, path):
        os.chdir(path)
        self.workDir = path

    def loadMoodleList(self, path):
        moodleList = pd.read_excel(path)
        moodleList = moodleList.drop("E-Mail-Adresse", axis=1)
        self.moodleList = moodleList

    def loadTucanList(self, path):
        tucanList = pd.read_excel(path)
        tucanList.columns = ["Index", "Matrikelnummer", "Nachname", "Vorname"]
        tucanList = tucanList.drop("Index", axis=1)
        self.tucanList = tucanList

    def createDirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
            return True
        return False

    def copySubmissionsToDir(self, path, newDir):
        if not os.path.isdir(newDir):
            copytree(f"{path}", newDir)
        return [
            os.path.join(root, file)
            for root, dirs, files in os.walk(newDir)
            for file in files
            if file.endswith(".html")
        ]

    def saveDataToJSON(self, data):
        data.to_json("data.json")

    def loadSaveFileFromJSON(self):
        if os.path.isfile("data.json"):
            return pd.read_json("data.json")

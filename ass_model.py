import json
import os
import sys
from shutil import copytree

import pandas as pd
from ass_pdf import PDFModel


class ASSModel:
    """docstring for ASSModell."""

    @classmethod
    def resourcePath(cls, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def __init__(self):
        super(ASSModel, self).__init__()
        self.workDir = os.path.abspath(os.getcwd())

    def loadAssignmentDescription(self):
        json_file_path = "json-mock-data/tasks.json"
        with open(json_file_path, "r") as j:
            return json.loads(j.read())

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

    def exportToPDF(self, data, descr, th):
        img_dir = ASSModel.resourcePath("imgs")
        pdf = PDFModel(data, descr, th, img_dir)
        path = data["Pfad zur Abgabe"]
        path = os.path.split(path)[0]
        pdf.output(f"{path}/{data.name}.pdf", "F")

        # pdf.output(
        #     f"{path}{'/' if path != '' else 'GMV Testat Tool/Studenten ohne Abgabe/'}{data.index[0]}.pdf"
        # )

    def getHTMLFromMatrikel(self, path):
        # read html file and return it as string
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

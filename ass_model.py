import json
import os
import sys
from shutil import copytree, copy

import pandas as pd
from ass_pdf import PDFModel

from PyQt5.QtWidgets import QFileDialog, QMessageBox


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
        self.checkContentDir()

    def checkContentDir(self):
        content_dir = ASSModel.resourcePath("content")
        if not os.path.isdir(content_dir):
            os.makedirs(content_dir)
        while not os.path.isfile(f"{content_dir}/testat.json"):
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Neuen Speicherstand anlegen?")
            msgBox.setIcon(1)
            msgBox.setText(f"Willkommen zum Testat-Tool des IIB.")
            msgBox.setInformativeText(
                "Keine Testatdatei gefunden.\nSoll eine Testatdatei ausgewählt werden?"
            )
            msgBox.setDetailedText("The details are as follows:")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.button(QMessageBox.Yes).setText("Ja")
            msgBox.button(QMessageBox.No).setText("Nein")
            msgBox.setDetailedText(f"Name der Testatdatei: 'testat.json'")

            msgBox.exec()
            if msgBox.result() == QMessageBox.Yes:
                jsonFile = QFileDialog.getOpenFileName(
                    msgBox,
                    f"Öffne die JSON-Datei",
                    filter=f"JSON-Dateien k(*.json) ;; Alle Dateien (*)",
                )
                if jsonFile[0] != "":
                    copy(jsonFile[0], content_dir)

            else:
                sys.exit()

    def loadAssignmentDescription(self):
        content_dir = ASSModel.resourcePath("content")
        json_file_path = f"{content_dir}/testat.json"
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
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import random
import os


class OverviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, descr):
        super(OverviewTableModel, self).__init__()
        self._data = pd.DataFrame(
            [], columns=["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        )
        self.descr = descr
        self.maxPoints = self.descr["maxPoints"]
        self.passThreshold = int(self.maxPoints / 2)
        criteriaCount = sum(
            map(lambda task: len(task["subTasks"]), self.descr["tasks"])
        ) + len(self.descr["penalties"])
        self.criteriaColumnNames = [f"Criteria {idx}" for idx in range(criteriaCount)]
        self.criteriaColumnNames.append("Kommentar")
        self.criteriaColumnNames.append("Pfad zur Abgabe")
        self.weights = self.descr["weights"]
        if len(self.weights) != criteriaCount:
            raise ValueError("Number of weights does not match number of criteria.")

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data
        self.layoutChanged.emit()

    def getIndex(self, row):
        return self._data.index[row]

    def getPath(self, matrikel):
        return self._data.at[matrikel, "Pfad zur Abgabe"]

    def getEvalData(self, matrikel):
        return self._data.loc[matrikel, self.criteriaColumnNames + ["Bewertet"]]

    def getSubmissionCount(self):
        return self._data["Abgabe"].value_counts()["Ja"]

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return 5  # only display the first 5 columns in the ui

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def populateDataModel(self, tucanList, moodleList):
        entryList = pd.merge(tucanList, moodleList, on=["Nachname", "Vorname"])
        columns = ["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        for idx, entry in entryList.iterrows():
            newValues = [entry["Nachname"], entry["Vorname"], "Nein", 0, "Nein"]
            self._data.loc[entry["Matrikelnummer"], columns] = newValues
        self._data[self.criteriaColumnNames[:-2]] = 0
        self._data[self.criteriaColumnNames[-2]] = "Keine Bemerkungen."
        self._data["Bewertet"] = False
        self._data.sort_values(by=["Nachname", "Vorname"], inplace=True)
        self.layoutChanged.emit()

    def populateDataModelWithPaths(self, pathList):
        for path in pathList:
            matrikel = int(os.path.splitext(os.path.basename(path))[0])
            self._data.loc[matrikel, ["Abgabe", "Pfad zur Abgabe"]] = ["Ja", path]
        self.layoutChanged.emit()

    def updateValueForCriteria(self, nr, matrikel, value):
        self._data.at[matrikel, f"Criteria {nr}"] = value
        # weight the points with the weights, sum them up and cap at 0
        self._data.at[matrikel, "Punkte"] = max(
            0,
            sum(
                map(
                    lambda x: x[0] * x[1],
                    zip(
                        self._data.loc[matrikel, self.criteriaColumnNames[:-2]],
                        self.weights,
                    ),
                )
            ),
        )
        self.updatePassStatus()
        self.dataChanged.emit(self.index(matrikel, 3), self.index(matrikel, 3))

    def updateRemarkText(self, matrikel, text):
        self._data.at[matrikel, "Kommentar"] = text

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(
            self._data.columns[column], ascending=order == Qt.AscendingOrder
        )
        self.layoutChanged.emit()

    def setPassThreshold(self, newValue):
        self.passThreshold = newValue
        self.updatePassStatus()
        self.layoutChanged.emit()

    def updatePassStatus(self):
        self._data["Bestanden"] = self._data["Punkte"].apply(
            lambda x: "Ja" if x >= self.passThreshold else "Nein"
        )

    def setEvalStatus(self, matrikel, newStatus):
        self._data.at[matrikel, "Bewertet"] = newStatus

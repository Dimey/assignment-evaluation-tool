import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import random
import os


class OverviewTableModel(QtCore.QAbstractTableModel):
    labelStat0Signal = QtCore.pyqtSignal(str)  # subm
    labelStat1Signal = QtCore.pyqtSignal(str)  # passed
    labelStat2Signal = QtCore.pyqtSignal(str)  # avg

    def __init__(self, descr):
        super(OverviewTableModel, self).__init__()
        self._data = pd.DataFrame(
            [], columns=["Nachname", "Vorname", "Punkte", "Bestanden", "Abgabe"]
        )
        self.maxPoints = descr["maxPoints"]
        self.passThreshold = int(self.maxPoints / 2)
        self.criteriaCount = sum(
            map(lambda task: len(task["subTasks"]), descr["tasks"])
        ) + len(descr["penalties"])
        self.criteriaColumnNames = [
            f"Criteria {idx}" for idx in range(self.criteriaCount)
        ]
        self.criteriaColumnNames.append("Kommentar")
        self.criteriaColumnNames.append("Pfad zur Abgabe")
        self.weights = descr["weights"]
        if len(self.weights) != self.criteriaCount:
            raise ValueError("Number of weights does not match number of criteria.")

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if isinstance(value, float):
                return f"{value:g}"
            if index.column() == 3:
                if self._data.iloc[index.row(), -2] == True:
                    return "\u2713"
                else:
                    return None
            return str(value)

        # if student has no submission make the text light gray
        if role == Qt.ForegroundRole:
            if self._data.iloc[index.row(), 4] == "Nein":
                return QtGui.QColor(200, 200, 200)
            if index.column() == 2:
                if self._data.iloc[index.row(), 2] < self.passThreshold:
                    return QtGui.QColor(191, 70, 39)
                return QtGui.QColor(0, 128, 0)

        # make the points and bestanden align them to the center
        if role == Qt.TextAlignmentRole:
            if index.column() == 2:
                return Qt.AlignRight | Qt.AlignVCenter
            if index.column() == 3:
                return Qt.AlignCenter | Qt.AlignVCenter

        # make the points bold
        if role == Qt.FontRole and index.column() in [2, 3]:
            font = QtGui.QFont()
            font.setBold(True)
            return font

    def getData(self):
        return self._data

    def getStudentData(self, matrikel):
        return self._data.loc[matrikel]

    def setData(self, data):
        self._data = data
        self.layoutChanged.emit()

    def getIndex(self, row):
        return self._data.index[row]

    def getPath(self, matrikel):
        return self._data.at[matrikel, "Pfad zur Abgabe"]

    def getPathsOfSubmittingStudents(self):
        return self._data[self._data["Abgabe"] == "Ja"]["Pfad zur Abgabe"].tolist()

    def getEvalData(self, matrikel):
        return self._data.loc[matrikel, self.criteriaColumnNames + ["Bewertet"]]

    def getIndexOfEvaluatedStudents(self):
        return self._data[
            (self._data["Bewertet"] == True) & (self._data["Abgabe"] == "Ja")
        ].index

    def getSubmissionCount(self):
        return self._data["Abgabe"].value_counts()["Ja"]

    def getIndexOfSubmittingStudents(self):
        return self._data[self._data["Abgabe"] == "Ja"].index

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return 4  # only display the first 3 columns in the ui

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 3:
                    return "Bewertet"
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def populateDataModel(self, tucanList, moodleList):
        entryList = pd.merge(tucanList, moodleList, on=["Nachname", "Vorname"])
        columns = ["Nachname", "Vorname", "Punkte", "Bestanden", "Abgabe"]
        for idx, entry in entryList.iterrows():
            newValues = [entry["Nachname"], entry["Vorname"], 0, "Nein", "Nein"]
            self._data.loc[entry["Matrikelnummer"], columns] = newValues
        self._data[self.criteriaColumnNames[:-2]] = 0
        self._data[self.criteriaColumnNames[-2]] = ""
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
        self.dataChanged.emit(self.index(matrikel, 2), self.index(matrikel, 2))

    def updateRemarkText(self, matrikel, text):
        self._data.at[matrikel, "Kommentar"] = text

    def addTextToRemark(self, matrikel, text):
        self._data.at[matrikel, "Kommentar"] += text

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
        statTxt = f"{100*self.getPassedCount() / self.getSubmissionCount():.1f} %"
        self.labelStat1Signal.emit(statTxt)

    def getPassedCount(self):
        return self._data[self._data["Bestanden"] == "Ja"].shape[0]

    def updateEvalStatus(self, matrikel, newStatus):
        self._data.at[matrikel, "Bewertet"] = newStatus
        statTxt = f"{self.getEvaluatedCount()} von {self.getSubmissionCount()}"
        self.labelStat0Signal.emit(statTxt)
        self.labelStat2Signal.emit(f"{self.getAvgPoints():.1f}")
        # emit signal to trigger decoration update
        self.dataChanged.emit(self.index(matrikel, 0), self.index(matrikel, 0))
        return self.getEvaluatedCount()

    def getEvaluatedCount(self):
        return self._data[
            (self._data["Bewertet"] == True) & (self._data["Abgabe"] == "Ja")
        ].shape[0]

    def getAvgPoints(self):
        points = self._data[
            (self._data["Bewertet"] == True) & (self._data["Abgabe"] == "Ja")
        ]["Punkte"].mean()
        return 0 if points != points else points

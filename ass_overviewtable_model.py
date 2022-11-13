import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import random
import os


class OverviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(OverviewTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def getIndex(self, row):
        return self._data.index[row]

    def getPath(self, matrikel):
        return self._data.at[matrikel, "Pfad zur Abgabe"]

    def getEvalData(self, matrikel):
        return self._data.loc[matrikel, self.criteriaColumns]

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        # return self._data.shape[1]
        return 5  # we will only display the first 5 columns in the ui

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def extendDataModellBySubTasks(self, descr):
        criteriaCount = sum(map(lambda task: len(task["subTasks"]), descr["tasks"]))
        criteriaCount += len(descr["penalties"])
        self.criteriaColumns = [f"Criteria {idx}" for idx in range(criteriaCount)]
        self.criteriaColumns.append("Kommentar")
        self.criteriaColumns.append("Pfad zur Abgabe")
        dataCriteria = pd.DataFrame([], columns=self.criteriaColumns)
        self._data = pd.concat([self._data, dataCriteria], axis=1)

    def populateDataModel(self, tucanList, moodleList):
        entryList = pd.merge(tucanList, moodleList, on=["Nachname", "Vorname"])
        columns = ["Nachname", "Vorname", "Abgabe", "Punkte", "Bestanden"]
        for idx, entry in entryList.iterrows():
            newValues = [entry["Nachname"], entry["Vorname"], "Nein", 0, "Nein"]
            self._data.loc[entry["Matrikelnummer"], columns] = newValues
        self._data[self.criteriaColumns[:-2]] = 0
        self._data[self.criteriaColumns[-2]] = "Keine Bemerkungen."
        self._data.sort_values(by=["Nachname", "Vorname"], inplace=True)
        self.layoutChanged.emit()

    def populateDataModelWithPaths(self, pathList):
        for path in pathList:
            matrikel = int(os.path.splitext(os.path.basename(path))[0])
            self._data.loc[matrikel, ["Abgabe", "Pfad zur Abgabe"]] = ["Ja", path]
        self.layoutChanged.emit()

    def updateValueForCriteria(self, nr, matrikel, value):
        self._data.at[matrikel, f"Criteria {nr}"] = value
        self._data.at[matrikel, "Punkte"] = self._data.loc[
            matrikel, self.criteriaColumns[:-2]
        ].sum()
        self.dataChanged.emit(self.index(matrikel, 3), self.index(matrikel, 3))

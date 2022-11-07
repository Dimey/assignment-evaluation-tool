import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import random


class OverviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(OverviewTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

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
        subTaskCount = 0
        for task in descr["tasks"]:
            subTaskCount += len(task["subTasks"])
        columnNames = [f"Criteria {idx+1}" for idx in range(subTaskCount)]
        dataCriteria = pd.DataFrame([], columns=columnNames)
        self._data = pd.concat([self._data, dataCriteria], axis=1)

    def makeRandomEntry(self):
        # create a random integer with 7 digits
        randomInt = random.randint(1000000, 9999999)
        # create random nachname and vorname
        self._data.loc[randomInt, "Nachname"] = "Muster"
        self._data.loc[randomInt, "Vorname"] = "Max"
        self._data.loc[randomInt, "Abgabe"] = random.choice(["Ja", "Nein"])
        self._data.loc[randomInt, "Punkte"] = random.randint(0, 30)
        self._data.loc[randomInt, "Bestanden"] = random.choice(["Ja", "Nein"])
        self.layoutChanged.emit()

    def populateDataModel(self, tucanList, moodleList):
        entryList = pd.merge(tucanList, moodleList, on=["Nachname", "Vorname"])
        # populate the data model with the entries from the merged list
        for idx, entry in entryList.iterrows():
            self._data.loc[entry["Matrikelnummer"], "Nachname"] = entry["Nachname"]
            self._data.loc[entry["Matrikelnummer"], "Vorname"] = entry["Vorname"]
            self._data.loc[entry["Matrikelnummer"], "Abgabe"] = "Nein"
            self._data.loc[entry["Matrikelnummer"], "Punkte"] = 0
            self._data.loc[entry["Matrikelnummer"], "Bestanden"] = "Nein"
        self._data.sort_values(by=["Nachname", "Vorname"], inplace=True)
        self.layoutChanged.emit()

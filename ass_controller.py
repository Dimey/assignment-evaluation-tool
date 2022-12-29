import math

from functools import partial
from ass_overviewtable_model import OverviewTableModel

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QAbstractItemView

from ass_worker import Worker


class ASSController:
    """docstring for ASSController."""

    def __init__(self, model, view):
        super(ASSController, self).__init__()
        self.view = view
        self.model = model
        self.threadpool = QThreadPool()

        # load assignment defining json file
        self.assignmentDescription = model.loadAssignmentDescription()
        self.overviewTableViewModel = OverviewTableModel(self.assignmentDescription)
        self.view.createUI(self.assignmentDescription, self.overviewTableViewModel)

        self.initializeUI()

        # Connect signals and slots
        self.connectSignals()

    def initializeUI(self):
        self.view.updateWorkDirLineEdit(path=self.model.workDir)

    def connectSignals(self):
        # signals through user interaction
        for idx, spinBox in enumerate(self.view.spinBoxList):
            spinBox.valueChanged.connect(partial(self.savePoints, spinBox, idx))
        self.view.loadButton.clicked.connect(self.loadSaveFile)
        self.view.saveButton.clicked.connect(self.saveFile)
        self.view.tucanButton.clicked.connect(partial(self.openEntryList, "tucan"))
        self.view.moodleButton.clicked.connect(partial(self.openEntryList, "moodle"))
        self.view.importSubmissionsButton.clicked.connect(self.importSubmissions)
        self.view.overviewTable.selectionModel().selectionChanged.connect(
            self.updateSpinBoxList
        )
        self.view.jumpToAssignmentButton.clicked.connect(self.jumpToAssignment)
        self.view.remarkTextEdit.textChanged.connect(self.saveRemarks)
        self.view.passThresholdSpinBox.valueChanged.connect(self.changePassThreshold)
        self.view.evaluationOverviewGroupBox.clicked.connect(self.saveEvalStatus)
        self.view.pdfExportButton.clicked.connect(self.exportToPDF)
        self.view.batchPDFExportButton.clicked.connect(self.batchExportToPDFThread)
        self.view.preCheckButton.clicked.connect(self.preCheck)
        self.view.changeWorkDirButton.clicked.connect(self.changeWorkDir)
        self.view.newTestatButton.clicked.connect(self.loadTestatFile)

        # signals from model
        self.overviewTableViewModel.labelStat0Signal.connect(
            self.view.statsLabelList[0].setText
        )
        self.overviewTableViewModel.labelStat1Signal.connect(
            self.view.statsLabelList[1].setText
        )
        self.overviewTableViewModel.labelStat2Signal.connect(
            self.view.statsLabelList[2].setText
        )

    def openEntryList(self, typeOfList):
        otherList = "tucan" if typeOfList == "moodle" else "moodle"
        filename = self.view.openFileDialog("xlsx", typeOfList)
        if typeOfList in filename[0].lower():
            if typeOfList == "tucan":
                self.model.loadTucanList(filename[0])
                self.view.updateLabel(
                    [self.view.tucanCountLabel], [self.model.tucanList.shape[0]]
                )
            else:
                self.model.loadMoodleList(filename[0])
                self.view.updateLabel(
                    [self.view.moodleCountLabel], [self.model.moodleList.shape[0]]
                )
            self.view.showTextInStatusBar(
                txt=f"{typeOfList.capitalize()}-Liste geladen."
            )
            if hasattr(self.model, f"{otherList}List"):
                # self.view.showTextInStatusBar(txt="Fuzzy Matching...")
                self.overviewTableViewModel.populateDataModel(
                    self.model.tucanList, self.model.moodleList
                )
                self.view.showTextInStatusBar(txt="Fuzzy Matching abgeschlossen.")
                self.view.importSubmissionsButton.setEnabled(True)

    def importSubmissions(self):
        path = self.view.openFolderDialog("Wähle Abgaben-Ordner aus.")
        if path:
            # copy selected folder (param1) to workdir/x (param2)
            pathList = self.model.copySubmissionsToDir(path, "gmv1_testat/Abgaben")
            self.view.showTextInStatusBar(
                txt=f"Abgaben nach .../gmv1_testat/Abgaben kopiert."
            )
            pathErrors = self.overviewTableViewModel.populateDataModelWithPaths(
                pathList
            )
            if pathErrors:
                self.view.createMessageBox(
                    "Fehler in den Abgaben gefunden",
                    "Bitte überprüfe in den unten aufgelisteten Pfaden die Abgaben auf Format-Fehler.",
                    pathErrors,
                )
            self.view.updateLabel([self.view.submissionCountLabel], [len(pathList)])
            self.selectedMatrikel = self.overviewTableViewModel.getIndex(0)
            self.view.evaluationOverviewGroupBox.setEnabled(True)
            self.view.saveButton.setEnabled(True)
            self.view.batchPDFExportButton.setEnabled(True)
            self.view.preCheckButton.setEnabled(True)
            self.view.updateLabel(
                [
                    self.view.statsLabelList[0],
                ],
                [
                    f"{self.overviewTableViewModel.getEvaluatedCount()} von {self.overviewTableViewModel.getSubmissionCount()}"
                ],
            )
            self.view.overviewTable.setSelectionMode(QAbstractItemView.SingleSelection)
            self.view.overviewTable.selectRow(0)

    def updateSpinBoxList(self):
        self.selectedMatrikel = self.overviewTableViewModel.getIndex(
            self.view.overviewTable.selectionModel().selectedRows()[0].row()
        )

        data = self.overviewTableViewModel.getEvalData(self.selectedMatrikel)
        self.view.updateSpinBoxes(data)

    def jumpToAssignment(self):
        submPath = self.overviewTableViewModel.getPath(self.selectedMatrikel)
        self.view.openFileExplorer(submPath)

    def savePoints(self, lineEditObj, idx):
        self.overviewTableViewModel.updateValueForCriteria(
            idx, self.selectedMatrikel, self.view.spinBoxList[idx].value()
        )
        self.view.updateLabel(
            [self.view.statsLabelList[1]],
            [
                f"{100*self.overviewTableViewModel.getPassedCount() / self.overviewTableViewModel.getSubmissionCount():.1f} %"
            ],
        )

    def saveRemarks(self):
        self.overviewTableViewModel.updateRemarkText(
            self.selectedMatrikel, self.view.remarkTextEdit.toPlainText()
        )

    def loadSaveFile(self):
        data = self.model.loadSaveFileFromJSON()
        if data is not None:
            self.overviewTableViewModel.setData(data)
            self.view.evaluationOverviewGroupBox.setEnabled(True)
            self.view.saveButton.setEnabled(True)
            self.view.batchPDFExportButton.setEnabled(True)
            self.view.preCheckButton.setEnabled(True)
            participantCount = f"{len(self.overviewTableViewModel.getData())}+"
            submCount = self.overviewTableViewModel.getSubmissionCount()
            self.view.updateLabel(
                [
                    self.view.tucanCountLabel,
                    self.view.moodleCountLabel,
                    self.view.submissionCountLabel,
                    self.view.statsLabelList[0],
                    self.view.statsLabelList[1],
                    self.view.statsLabelList[2],
                ],
                [
                    participantCount,
                    participantCount,
                    str(submCount),
                    f"{self.overviewTableViewModel.getEvaluatedCount()} von {submCount}",
                    f"{100*self.overviewTableViewModel.getPassedCount() / submCount:.1f} %",
                    f"{self.overviewTableViewModel.getAvgPoints():.1f}",
                ],
            )
            self.view.showTextInStatusBar(txt="Speicherdatei erfolgreich geladen.")
            self.view.overviewTable.setSelectionMode(QAbstractItemView.SingleSelection)
            self.view.overviewTable.selectRow(0)
            self.selectedMatrikel = self.overviewTableViewModel.getIndex(0)

    def saveFile(self):
        self.model.saveDataToJSON(self.overviewTableViewModel.getData())
        self.view.showTextInStatusBar(txt="Dateien erfolgreich gespeichert.")

    def changePassThreshold(self):
        self.overviewTableViewModel.setPassThreshold(
            self.view.passThresholdSpinBox.value()
        )

    def saveEvalStatus(self):
        evaluatedCount = self.overviewTableViewModel.updateEvalStatus(
            self.selectedMatrikel,
            not self.view.evaluationOverviewGroupBox.isChecked(),
        )

    def exportToPDF(self, matrikel=None):
        studentData = self.overviewTableViewModel.getStudentData(
            matrikel or self.selectedMatrikel
        )
        self.model.exportToPDF(
            studentData,
            self.assignmentDescription,
            self.overviewTableViewModel.passThreshold,
        )
        if matrikel is False:
            self.view.showTextInStatusBar(
                txt=f"Einzelne PDF für {studentData['Nachname']}, {studentData['Vorname'][0]}. erzeugt."
            )

    def batchExportToPDF(self, progress_callback):
        matrikelNumbers = self.overviewTableViewModel.getIndexOfEvaluatedStudents()
        pdfCount = len(matrikelNumbers)
        for idx, matrikel in enumerate(matrikelNumbers):
            self.exportToPDF(matrikel)
            progress = math.ceil((idx + 1) * 100 / pdfCount)
            progress_callback.emit(progress, f"{idx+1} von {pdfCount} PDFs erzeugt.")

    def thread_complete(self):
        self.view.showTextInStatusBar(
            txt=f"PDFs wurden für alle bewerteten Studenten erzeugt."
        )

    def batchExportToPDFThread(self):
        self.view.showProgressWindow("PDF Batch Export")
        worker = Worker(self.batchExportToPDF)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.view.progressWindow.updateProgressInfo)

        self.threadpool.start(worker)

    def preCheck(self):
        matrikelNumbers = self.overviewTableViewModel.getIndexOfSubmittingStudents()
        paths = self.overviewTableViewModel.getPathsOfSubmittingStudents()

        valueVariations = self.assignmentDescription["valueVariations"]
        searchStrings = self.assignmentDescription["searchStrings"]

        for matrikel, path in zip(matrikelNumbers, paths):
            cp_html = self.model.getHTMLFromMatrikel(path)

            failCount = 0
            for idx, (key, value) in enumerate(searchStrings.items()):
                pos = int(str(matrikel)[int(key)])
                searchString = value.replace("$", f"{valueVariations[idx][pos]:g}")
                if cp_html.find(searchString) == -1:
                    failCount += 1
            self.overviewTableViewModel.updateValueForCriteria(
                self.overviewTableViewModel.criteriaCount - 1, matrikel, failCount
            )
            if failCount > 0:
                self.overviewTableViewModel.addTextToRemark(
                    matrikel,
                    f"Matrikelnummer an {failCount} Stelle{'n' if failCount > 1 else ''} nicht korrekt angepasst.\n",
                )
        self.updateSpinBoxList()
        self.view.showTextInStatusBar(
            txt="Vorprüfung durchgeführt. Ergebnisse aktualisiert."
        )
        self.view.preCheckButton.setEnabled(False)

    def changeWorkDir(self, arg):
        path = self.view.openFolderDialog("Wähle einen Ort für das Arbeitsverzeichnis")
        if path:
            self.model.changeWorkDir(path)
            self.view.showWorkDir(path)

    def loadTestatFile(self):
        self.model.loadTestatFile(appStart=False)

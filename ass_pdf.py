import datetime

import pandas as pd
from fpdf import FPDF


class PDFModel(FPDF):
    @classmethod
    def idCheck(cls, kp, werte):
        pass

    def __init__(self, data, descr, th, img_dir):
        super().__init__("P", "mm")
        self.data = data
        self.descr = descr
        self.threshold = th
        self.img_dir = img_dir

        # Meta data
        self.set_title(f"Bewertung für {self.data['Vorname']} {self.data['Nachname']}")
        self.set_author(f"{self.descr['courseTitle']}")

        # Set document parameters
        self.textHeight = 11
        self.titleHeight = 13
        self.cellHeight = 8
        self.cellMaxWidth = 170
        self.cellWidthLeft = 135.9
        self.cellWidthLeftPart = 42.5
        self.cellWidthRight = 26.1
        self.font = "Courier"

        self.set_auto_page_break(auto=False)
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.set_top_margin(20)
        self.constructPDF()

    def header(self):
        # IIB Logo
        self.image(name=self.img_dir + "/iib_logo.png", x=160, y=22, w=25)
        # Font
        self.set_font(family="Arial", style="B", size=16)
        # Title
        self.cell(
            w=0,
            h=8,
            txt=f"{self.descr['courseTitle']}",
            border=False,
            ln=1,
            align="L",
        )
        self.set_font("Arial", "", 14)
        self.cell(w=130, h=8, txt=f"{self.descr['term']}", align="L")
        # Line break
        self.ln(16)

    def footer(self):
        # Set position
        self.set_y(-20)
        # Set font and color
        self.set_font(family="Arial", style="I", size=10)
        self.set_text_color(0, 0, 0)
        # Set text
        self.cell(
            w=0,
            h=8,
            txt=f"Dokument erzeugt am {str(datetime.datetime.now())[0:19]}",
            align="C",
        )

    def emptyLine(self):
        self.cell(w=0, h=self.cellHeight, border=True, ln=1)

    def twoPartCell_subTask(self, txt1, pt1, pt2):
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(
            w=self.cellWidthLeft, h=self.cellHeight, txt=txt1, align="L", border=True
        )
        self.set_font(family=self.font, style="B", size=self.textHeight)
        self.cell(w=15.5, h=self.cellHeight, txt=f"{pt1:g}", align="R", border="TB")
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(w=3.1, h=self.cellHeight, txt="/", align="C", border="TB")
        self.cell(
            w=15.5, h=self.cellHeight, txt=f"{pt2:g}", align="L", border="TBR", ln=1
        )

    def twoPartCell_penalty(self, txt1, pen):
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(
            w=self.cellWidthLeft, h=self.cellHeight, txt=txt1, align="L", border=True
        )
        self.set_font(family=self.font, style="B", size=self.textHeight)
        self.cell(
            w=34.1, h=self.cellHeight, txt=f"{pen:g}", align="C", border="TBR", ln=1
        )

    def twoPartCell_param(self, txt1, txt2):
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(
            w=self.cellWidthLeftPart,
            h=self.cellHeight,
            txt=txt1,
            align="L",
            border=True,
        )
        self.set_font(family=self.font, style="B", size=self.textHeight)
        self.cell(
            w=self.cellMaxWidth - self.cellWidthLeftPart,
            h=self.cellHeight,
            txt=f"{txt2}",
            align="L",
            border=True,
            ln=1,
        )

    def twoPartCell_notes(self, txt1):
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.multi_cell(
            w=self.cellWidthLeftPart,
            h=self.cellHeight,
            txt="Bemerkungen\n \n \n ",
            align="L",
            border=True,
        )
        self.set_font(family=self.font, style="B", size=self.textHeight - 2)
        x = 20 + self.cellWidthLeftPart
        y = self.get_y() - 4 * self.cellHeight
        self.set_xy(x, y)
        # TODO: ".replace('\n', '')" entfernen
        self.multi_cell(
            w=self.cellMaxWidth - self.cellWidthLeftPart,
            h=self.cellHeight,
            txt=str(txt1).replace("\u000A", "\n").replace(r"\n", ""),
            align="L",
            border=False,
        )
        self.set_xy(x, y)
        self.cell(
            w=self.cellMaxWidth - self.cellWidthLeftPart,
            h=self.cellHeight * 4,
            border=True,
            ln=1,
        )

    def taskTitle(self, title):
        self.set_font(family=self.font, style="U", size=self.textHeight)
        self.cell(w=0, h=self.cellHeight, txt=f"{title}", align="C", border=True, ln=1)

    def textLine(self, txt1, family, style, align):
        self.set_font(family=family, style=style, size=self.textHeight)
        self.cell(
            w=0, h=self.cellHeight, txt=f"{txt1}", align=align, border=False, ln=1
        )

    def grading(self, points, passThreshold):
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(
            w=self.cellWidthLeft,
            h=self.cellHeight,
            txt="Ergebnis",
            align="L",
            border="LT",
        )
        self.set_font(family=self.font, style="B", size=self.textHeight)
        self.set_line_width(width=0.2)
        self.cell(w=15.5, h=self.cellHeight, txt=f"{points:g}", align="R", border="LT")
        self.set_font(family=self.font, style="", size=self.textHeight)
        self.cell(w=3.1, h=self.cellHeight, txt="/", align="C", border="T")
        self.cell(w=15.5, h=self.cellHeight, txt="30", align="L", border="TR", ln=1)

        self.set_line_width(width=0.2)
        self.cell(
            w=self.cellWidthLeft,
            h=self.cellHeight,
            txt=f"(Bestehensgrenze: {passThreshold} Punkte)",
            align="L",
            border="LB",
        )
        self.set_font(family=self.font, style="B", size=self.textHeight - 1)
        self.set_line_width(width=0.2)
        if points >= passThreshold:
            self.set_text_color(102, 164, 99)
            self.cell(
                w=34.1,
                h=self.cellHeight,
                txt=f"BESTANDEN",
                align="C",
                border="LBR",
                ln=1,
            )
        else:
            self.set_text_color(191, 70, 39)
            self.cell(
                w=34.1,
                h=self.cellHeight,
                txt=f"NICHT BESTANDEN",
                align="C",
                border="LBR",
                ln=1,
            )
        self.set_text_color(0, 0, 0)
        self.set_line_width(width=0.2)

    def constructPDF(self):
        # Add a page
        self.add_page()

        # Title
        self.taskTitle(f"{self.descr['assignmentTitle']}")

        # Id + name
        self.twoPartCell_param("Matrikelnummer", f"{self.data.name}")
        self.twoPartCell_param(
            "Name", f"{self.data['Nachname']}, {self.data['Vorname']}"
        )
        self.emptyLine()

        criteriaCounter = 0
        criteriaWeights = self.descr["weights"]
        for task in self.descr["tasks"]:
            self.taskTitle(f"{task['taskTitle']}")
            for subtask in task["subTasks"]:
                self.twoPartCell_subTask(
                    subtask["subTaskTitle"],
                    self.data[f"Criteria {criteriaCounter}"]
                    * criteriaWeights[criteriaCounter],
                    subtask["subTaskMaxPoints"] * criteriaWeights[criteriaCounter],
                )
                criteriaCounter += 1

        self.emptyLine()
        self.taskTitle("Abzüge")
        for penalty in self.descr["penalties"]:
            self.twoPartCell_penalty(
                penalty["penaltyTitle"],
                self.data[f"Criteria {criteriaCounter}"]
                * criteriaWeights[criteriaCounter],
            )
            criteriaCounter += 1

        self.emptyLine()
        self.twoPartCell_notes(self.data["Kommentar"])

        self.emptyLine()
        self.grading(self.data["Punkte"], self.threshold)

        # # Notes
        # self.twoPartCell_notes(self.data["Kommentar"])

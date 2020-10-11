#!/usr/bin/python3
import sys
import sqlite3
import codecs
import random
from PySide2 import QtWidgets, QtCore

DBFILENAME = "verben.db"
OUTFILENAME = "verbmanager.out.txt"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.tenselist = [u'presente', u'indefinido', u'imperfecto', u'participio', u'gerundio', u'condicional',
                          u'futuro', u'subjuntivopresente', u'subjuntivoimperfecto', u'imperativoafirmativo', u'imperativonegativo']
        self.action_save = QtWidgets.QAction("&Export and save...", self, shortcut="Ctrl+S", triggered=self.save, enabled=True)
        self.action_export = QtWidgets.QAction("&Export only...", self, shortcut="Ctrl+Alt+S", triggered=self.export, enabled=True)
        self.action_exit = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.action_save)
        self.fileMenu.addAction(self.action_export)
        self.fileMenu.addAction(self.action_exit)
        self.menuBar().addMenu(self.fileMenu)
        #
        self.table_widget = QtWidgets.QTableWidget()
        self.populate()
        #
        self.setCentralWidget(self.table_widget)
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def save(self):
        self.save_(dosave=True)

    def export(self):
        self.save_(dosave=False)

    def save_(self, dosave):
        linebreak = u"<br/>"
        replacementdict = {
            u'anterior': u'Pretérito anterior',
            u'subjuntivoimperfecto': u'Subjuntivo Imperfecto',
            u'imperativoafirmativo': u'Imperativo afirmativo',
            u'imperativonegativo': u'Imperativo negativo',
            u'A_infinitivo': u'Infinitivo',
            u'gerundio': u'Gerundio',
            u'indefinido': u'Pretérito indefinido',
            u'subjuntivofuturo': u'Subjuntivo Futuro',
            u'subjuntivoperfecto': u'Subjuntivo Perfecto',
            u'participio': u'Participio',
            u'subjuntivopluscuamperfecto': u'Subjuntivo Pluscuamperfecto',
            u'futuroperfecto': u'Futuro perfecto',
            u'condicionalperfecto': u'Condicional perfecto',
            u'imperativoafirmativoreflexiv': u'Imperativo afirmativo reflexivo',
            u'imperfecto': u'Pretérito imperfecto',
            u'condicional': u'Condicional',
            u'pluscuamperfecto': u'Pretérito pluscuamperfecto',
            u'gerundioreflexiv': u'Gerundio reflexivo',
            u'perfecto': u'Pretérito perfecto compuesto',
            u'subjuntivopresente': u'Subjuntivo Presente',
            u'presente': u'Presente',
            u'A_english': u'Ingles',
            u'subjuntivofuturoperfecto': u'Subjuntivo Futuro Perfecto',
            u'A_german': u'Aleman',
            u'futuro': u'Futuro',
        }
        pronomenlist = [
            u"yo", u"tú", u"él/ella/usted", u"nosotros/-as", u"vosotros/-as", u"ellos/ellas/ustedes"
        ]
        rlist = []
        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        for row in range(self.table_widget.rowCount()):
            infinitivo = self.table_widget.item(row, 0).text()
            german = self.table_widget.item(row, 1).text()
            for col in range(2, self.table_widget.colorCount()):
                widget = self.table_widget.item(row, col)
                if not widget or int(widget.flags()) & QtCore.Qt.ItemIsEnabled == 0 or widget.checkState() == 0:
                    continue
                tense = self.tenselist[col - 2]
                verben_id = self.table_widget.item(row, 0)._id

                if tense in ["participio", "gerundio", "gerundioreflexiv"]:
                    question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                        german=german,
                        linebreak=linebreak,
                        tense=replacementdict[tense])
                    result = cur.execute("SELECT {} FROM verben WHERE id == ?".format(tense), (verben_id, )).fetchone()
                    rlist.append([question, "{}{}{}".format(infinitivo, linebreak, result[0])])
                else:
                    result = cur.execute("""SELECT s1, s2, s3, p1, p2, p3 FROM {} WHERE id == ?""".format(tense), (verben_id, )).fetchone()
                    question = u'<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="{color}">{tense}</font></u></b>?'.format(
                        german=german,
                        linebreak=linebreak,
                        tense=replacementdict[tense],
                        color="#ef2929" if tense == "subjuntivoimperfecto" else "#000000")
                    tlist = [infinitivo, ""]
                    for pronomen, item in zip(pronomenlist, result):
                        if item is None:
                            continue
                        tlist.append("{} {}".format(pronomen, item))
                    if tense == "subjuntivoimperfecto":
                        tlist.append("")
                        for pronomen, result, repl in zip(pronomenlist, result, ["se", "ses", "se", "semos", "seis", "sen"]):
                            tlist.append("{} {}{}".format(pronomen, result[:-len(repl)], repl))
                    rlist.append([question, linebreak.join(tlist)])
                if dosave:
                    if cur.execute("SELECT id FROM export WHERE id == ?", (verben_id, )).fetchone() is None:
                        cur.execute("""INSERT INTO export ({}) VALUES ({})""".format("id", verben_id))
                    cur.execute("""UPDATE export SET {!r} = "2" WHERE id == ?""".format(tense), (verben_id, ))

        random.shuffle(rlist)
        ostr = "\n".join(u"{}|{}|{}".format(ritem[0], ritem[1], "Verb") for ritem in rlist)
        with codecs.open(OUTFILENAME, "w", encoding="utf-8") as fh:
            fh.write(ostr)
        self.statusBar().showMessage("Exported to {}".format(OUTFILENAME), 3000)
        if dosave:
            con.commit()
            con.close()
            self.table_widget.clear()
            self.populate()

    def populate(self):
        labellist = ['Infinitivo', 'Aleman', u'Presente', u'Indefinido', u'Imperfecto', u'Participio', u'Gerundio', u'Condicional',
                     u'Futuro', u'Subjuntivo presente', u'Subjuntivo imperfecto', u'Imperativo afirmativo', u'Imperativo negativo']
        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        cur.execute("""SELECT infinitivo, german, id FROM verben""")
        verbitemlist = cur.fetchall()
        self.table_widget.setRowCount(len(verbitemlist))
        self.table_widget.setColumnCount(2 + len(self.tenselist))
        for row, verbitem in enumerate(verbitemlist):
            for col in [0, 1]:
                widget = QtWidgets.QTableWidgetItem(str(verbitem[col]))
                widget._id = verbitem[-1]
                widget.setToolTip(str(verbitem[col]))
                widget.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table_widget.setItem(row, col, widget)
            for ccol, tense in enumerate(self.tenselist):
                flag = cur.execute("SELECT {} FROM export WHERE id == ?".format(tense), (verbitem[-1], )).fetchone()
                widget = QtWidgets.QTableWidgetItem("")
                if flag is None or flag[0] is None:
                    widget.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                    widget.setCheckState(QtCore.Qt.Unchecked)
                else:
                    widget.setFlags(QtCore.Qt.ItemIsUserCheckable)
                    widget.setCheckState(QtCore.Qt.Checked)
                self.table_widget.setItem(row, 2 + ccol, widget)
        self.table_widget.setHorizontalHeaderLabels(labellist)
        for col in range(self.table_widget.columnCount()):
            self.table_widget.horizontalHeaderItem(col).setToolTip(labellist[col])


if __name__ == '__main__':
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())

import sys
import sqlite3
from datetime import datetime
from functools import partial
import locale
from PySide2 import QtWidgets, QtCore


DBFILENAME = "wordslibros.db"
EXPORTFILENAME = "wordslibros4anki.txt"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.action_save = QtWidgets.QAction("&Export and save", self, shortcut="Ctrl+S", triggered=self.save, enabled=True)
        self.action_export = QtWidgets.QAction("Export &only", self, shortcut="Ctrl+Alt+S", triggered=self.export, enabled=True)
        self.action_exall = QtWidgets.QAction("Export &all", self, shortcut="Ctrl+A", triggered=self.export_all, enabled=True)
        self.action_exit = QtWidgets.QAction("E&xit", self, shortcut="Alt+X", triggered=self.close)
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.action_save)
        self.fileMenu.addAction(self.action_export)
        self.fileMenu.addAction(self.action_exall)
        self.fileMenu.addAction(self.action_exit)
        self.menuBar().addMenu(self.fileMenu)
        #
        self.table_widget = QtWidgets.QTableWidget()
        self.populate()
        self.table_widget.setColumnWidth(1, 2 * self.table_widget.columnWidth(1))
        self.table_widget.setColumnWidth(2, 4 * self.table_widget.columnWidth(2))
        #
        self.setCentralWidget(self.table_widget)
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def populate(self):
        self.table_widget.setSortingEnabled(False)
        self.table_widget.clear()
        columnlist = "exported spain german source type created updated id".split()
        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        cur.execute("""SELECT {} FROM WORDS""".format(",".join(columnlist)))
        worditemlist = cur.fetchall()
        self.table_widget.setRowCount(len(worditemlist))
        self.table_widget.setColumnCount(7)
        for row, worditem in enumerate(worditemlist):
            for column in range(len(columnlist) - 1):
                if column in [5, 6]:
                    text = datetime.fromtimestamp(int(worditem[column])).isoformat()
                else:
                    text = str(worditem[column])
                widget = QtWidgets.QTableWidgetItem(text)
                widget.setToolTip(text)
                if column == 0:
                    widget._id = worditem[-1]
                    if worditem[0] == 0:
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                        widget.setCheckState(QtCore.Qt.Unchecked)
                    elif worditem[0] < 0:
                        pass
                    else:
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable)
                        widget.setCheckState(QtCore.Qt.Checked)
                self.table_widget.setItem(row, column, widget)
        self.table_widget.setHorizontalHeaderLabels([item.capitalize() for item in columnlist[:-1]])
        [self.table_widget.horizontalHeaderItem(column).setTextAlignment(QtCore.Qt.AlignLeft) for column in range(self.table_widget.columnCount())]
        self.table_widget.setSortingEnabled(True)

    def save(self):
        self.save_(dosave=True)

    def export(self):
        self.save_(dosave=False)

    def save_(self, dosave):
        slist = []
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            checked = item.checkState() == QtCore.Qt.Checked and item.flags() & QtCore.Qt.ItemIsEnabled != 0
            if not checked:
                continue
            slist.append(str(item._id))

        if len(slist) == 0:
            return

        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        cur.execute("SELECT spain, german, type, source FROM words WHERE id in ({})".format(",".join(slist)))
        filename = EXPORTFILENAME
        with open(filename, "w") as fh:
            for item in cur.fetchall():
                print("{0}|{1}|{2}|{3}".format(*item), file=fh)
        if dosave:
            now = datetime.now().timestamp()
            cur.execute("UPDATE words SET exported = 1, updated = ? WHERE id in ({})".format(",".join(slist)), (now, ))
        con.commit()
        con.close()

        self.populate()

    def export_all(self):
        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM words")
        wordlist = cur.fetchall()
        print(wordlist)
        sortfn = partial(self.keyfn, 1)
        wordlist = sorted(wordlist, key=sortfn)
        with open("wordslibros.txt", "w") as fh:
            for word in wordlist:
                print(word[:-2], file=fh)
        con.close()

    def keyfn(self, index, a):
        a_ = a[index]
        if a_.startswith("el ") or a_.startswith("la ") or a_.startswith("las ") or a_.startswith("los ") or a_.startswith("a ") or a_.startswith("en ") or a_.startswith("el/la "):
            a_ = a_.split()[1]
            #print(a_)
        return locale.strxfrm(a_)
        return a_


if __name__ == '__main__':
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())

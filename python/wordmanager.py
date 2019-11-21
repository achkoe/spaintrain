import sys
import sqlite3
from PySide2 import QtWidgets, QtCore


DBFILENAME = "wordslibros.db"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.table_widget.setSortingEnabled(True)
        self.populate()
        self.table_widget.setColumnWidth(1, 2 * self.table_widget.columnWidth(1))
        self.table_widget.setColumnWidth(2, 4 * self.table_widget.columnWidth(2))
        #
        self.setCentralWidget(self.table_widget)
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def populate(self):
        con = sqlite3.connect(DBFILENAME)
        cur = con.cursor()
        columnlist = "exported spain german source type created updated".split()
        cur.execute("""SELECT {} FROM WORDS""".format(",".join(columnlist)))
        worditemlist = cur.fetchall()
        self.table_widget.setRowCount(len(worditemlist))
        self.table_widget.setColumnCount(7)
        for row, worditem in enumerate(worditemlist):
            for column in range(len(columnlist)):
                widget = QtWidgets.QTableWidgetItem(str(worditem[column]))
                widget.setToolTip(str(worditem[column]))
                #widget.setFlags(QtCore.Qt.ItemIsEnabled)
                if column == 0:
                    if worditem[0] == 0:
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                        widget.setCheckState(QtCore.Qt.Unchecked)
                    elif worditem[0] < 0:
                        pass
                    else:
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable)
                        widget.setCheckState(QtCore.Qt.Checked)
                self.table_widget.setItem(row, column, widget)

    def save(self):
        self.save_(dosave=True)

    def export(self):
        self.save_(dosave=False)

    def save_(self, dosave):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())

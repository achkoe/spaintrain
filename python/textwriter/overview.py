#!/usr/bin/env python
import os
import glob
import argparse
import json
from collections import Counter
import sys
import subprocess
from PyQt4 import QtCore, QtGui


class QCustomTableWidgetItem(QtGui.QTableWidgetItem):
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(QtCore.QString('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            selfDataValue  = str(self.data(QtCore.Qt.EditRole).toString()).split('-')[1][1:]
            otherDataValue = str(other.data(QtCore.Qt.EditRole).toString()).split('-')[1][1:]
            return int(selfDataValue) < int(otherDataValue)
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


class MainWin(QtGui.QMainWindow):
    def __init__(self, args):
        super(MainWin, self).__init__()
        self.setWindowTitle("{} - overview".format(os.path.abspath(args.path)))
        self.mainView = QtGui.QTableWidget()
        self.mainView.setColumnCount(4)
        self.mainView.setHorizontalHeaderLabels(["Solution", "Executed", "Results", "Name"])
        self.mainView.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignLeft)
        header = self.mainView.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(3, QtGui.QHeaderView.Stretch)
        self.mainView.cellDoubleClicked.connect(self.cellClicked)
        self.mainView.setSortingEnabled(True)
        self.setCentralWidget(self.mainView)
        self.args = args
        self.populateTable()
        action = QtGui.QAction(self, shortcut=QtGui.QKeySequence("Ctrl+R"), triggered=self.refresh)
        self.addAction(action)
        self.resize(1200, 800)

    def refresh(self):
        self.populateTable()

    def populateTable(self):
        filelist = getinput(self.args)
        self.mainView.setRowCount(len(filelist))
        for row, item in enumerate(filelist):
            tableWidgetItem = QCustomTableWidgetItem(os.path.splitext(os.path.basename(item))[0])
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.mainView.setItem(row, 3, tableWidgetItem)
            # adding data
            rdict, hassolution = analyze(item)
            rstrlist = []
            for cnt, name in rdict['r']:
                rstrlist.append("{name}: ok:{ok}, nok:{nok}".format(name=name, ok=cnt.get(1, 0), nok=cnt.get(2, 0)))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            cb = QtGui.QComboBox()
            cb.addItems(rstrlist)
            self.mainView.setCellWidget(row, 2, cb)
            # adding number
            tableWidgetItem = QtGui.QTableWidgetItem(str(len(rstrlist)))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.mainView.setItem(row, 1, tableWidgetItem)
            # adding hassolution
            tableWidgetItem = QtGui.QTableWidgetItem(str(hassolution))
            tableWidgetItem._data = item
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.mainView.setItem(row, 0, tableWidgetItem)

    def cellClicked(self, row, col):
        if col == 0 and self.mainView.item(row, 0).text() == "False":
            print "Not implemented"
        else:
            subprocess.Popen([sys.executable, "textwriter.py", self.mainView.item(row, 0)._data])


def analyze(filename):
    rdict = {"filename": filename, "r": []}
    lesson = json.load(open(filename))
    for index, item in enumerate(lesson["config"]):
        if item["name"].startswith("Default"):
            searchindex = index
            break
    for session in lesson["sessionlist"]:
        cnt = Counter()
        for item in [i for i in session["textlist"] if i["fontindex"] == searchindex]:
            cnt[item["state"]] += 1
        rdict["r"].append((cnt, session['name']))
    hassolution = "solution" in lesson
    return rdict, hassolution


def formatout(rlist):
    rval = []
    for rdict in rlist:
        rstrlist = []
        for cnt, name in rdict["r"]:
            rstrlist.append("u:{}, c:{}, f:{}".format(cnt.get(0, 0), cnt.get(1, 0), cnt.get(2, 0)))
        rval.append("{}\t{}".format(rdict["filename"], "|".join(rstrlist)))
    return rval


def getinput(args):
    return sorted(glob.glob(os.path.join(args.path, "*.json")), key=lambda item: int(item.split('-')[1][1:]))


def main(args):
    filelist = getinput(args)
    rlist = []
    for filename in filelist:
        rlist.append(analyze(filename)[0])
    print "\n".join(formatout(rlist))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs='?', default=".", help="path to show overview")
    parser.add_argument("--nogui", action="store_true", help="start in terminal")
    args = parser.parse_args()
    if not args.nogui:
        app = QtGui.QApplication(sys.argv)
        mainwin = MainWin(args)
        mainwin.show()
        sys.exit(app.exec_())
    else:
        main(args)

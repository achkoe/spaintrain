#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tempus Trainer."""

import voctiempo
import json
from PyQt4 import QtCore, QtGui


class TempusTrainer(QtGui.QMainWindow):
    def __init__(self, fileName=None):
        super(TempusTrainer, self).__init__()
        self.fileName = fileName
        self.lbl = QtGui.QLabel()
        self.setCentralWidget(self.lbl)
        self.maxRecentFiles = 4
        self.configname = "tempustrain.config.json"
        self.counter = 0
        self.rlist = voctiempo.read_vocdata(voctiempo.filename)
        config = [item for item in self.rlist[0].keys() if item not in [u"Infinitivo"]]
        config = dict(zip(config, [True] * len(config)))
        self.sdict = voctiempo.read_statistic(voctiempo.resultname, self.rlist)
        self.totallen = voctiempo.update_database(self.rlist)
        config.update(json.load(open(self.configname)))

        self.createActions(config)
        self.createMenus(config)
        self.resize(800, 400)

        self.mainWidget = QtGui.QWidget(self)
        self.lblQuestion = self._getStyleLabel()
        self.lblAnswer = self._getStyleLabel()
        self.lblStatistics = QtGui.QLabel()
        self.lblStatistics.setAlignment(QtCore.Qt.AlignRight)
        self.lblCounter = QtGui.QLabel()
        self.lblCounter.setAlignment(QtCore.Qt.AlignLeft)
        self.btnShowAnswer = QtGui.QPushButton("Show Answer")
        self.btnShowAnswer.setShortcut(QtCore.Qt.Key_Space)
        self.btnShowAnswer.clicked.connect(self.showAnswer)
        self.btnOkay = QtGui.QPushButton("&Yes")
        self.btnOkay.setShortcut(QtCore.Qt.Key_Y)
        self.btnOkay.clicked.connect(self.answerOkay)
        self.btnNotOkay = QtGui.QPushButton("&No")
        self.btnNotOkay.setShortcut(QtCore.Qt.Key_N)
        self.btnNotOkay.clicked.connect(self.answerNotOkay)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.lblQuestion, stretch=1)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.lblCounter, stretch=0)
        hbox.addWidget(self.lblStatistics, stretch=0)
        layout.addLayout(hbox)
        layout.addWidget(self.lblAnswer, stretch=1)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btnShowAnswer)
        hbox.addWidget(self.btnOkay)
        hbox.addWidget(self.btnNotOkay)
        layout.addLayout(hbox)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

        self.nextQuestion()

    def _getStyleLabel(self):
        lbl = QtGui.QLabel("")
        lbl.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        lbl.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        font = QtGui.QFont("Arial", 20)
        lbl.setFont(font)
        return lbl

    def nextQuestion(self):
        self.lblCounter.setText(str(self.counter))
        self.counter += 1
        excludelist = [unicode(item.text()) for item in self.langActions if not item.isChecked()]
        print excludelist
        self.qdict = voctiempo.get_next_question(self.rlist, self.totallen, excludelist)
        self.qa = voctiempo.get_question(self.rlist, self.qdict)
        self.lblQuestion.setText(self.qa[0])
        self.lblAnswer.setText("")
        self.statistic = self.sdict[self.rlist[self.qdict["listindex"]][u"Infinitivo"][0]][self.qdict["tempus"]]
        self.lblStatistics.setText("{} executed, {} correct".format(
            self.statistic["total"][self.qdict["person"]],
            self.statistic["correct"][self.qdict["person"]]))
        self.btnOkay.setEnabled(False)
        self.btnNotOkay.setEnabled(False)
        self.btnShowAnswer.setEnabled(True)

    def showAnswer(self):
        self.lblAnswer.setText(self.qa[1])#.replace("\xc3\xad", '\xed'))
        self.btnOkay.setEnabled(True)
        self.btnNotOkay.setEnabled(True)
        self.btnShowAnswer.setEnabled(False)

    def answerOkay(self):
        self.statistic["total"][self.qdict["person"]] += 1
        self.statistic["correct"][self.qdict["person"]] += 1
        self.nextQuestion()

    def answerNotOkay(self):
        self.statistic["total"][self.qdict["person"]] += 1
        self.nextQuestion()

    def closeEvent(self, event):
        print "saving"
        voctiempo.save_statistics(voctiempo.resultname, self.sdict)
        config = {}
        for action in self.langActions:
            config[unicode(action.text())] = action.isChecked()
        json.dump(config, open(self.configname, 'w'))
        super(TempusTrainer, self).closeEvent(event)

    def createMenus(self, config):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.exitAct)
        self.viewMenu = QtGui.QMenu("&View", self)
        for action in self.langActions:
            self.viewMenu.addAction(action)
        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutQtAct)
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def createActions(self, config):
        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.aboutQtAct = QtGui.QAction("About &Qt", self, triggered=QtGui.qApp.aboutQt)
        self.langActions = []
        for key, value in config.iteritems():
            self.langActions.append(QtGui.QAction(key, self, triggered=self.langAction, checkable=True, checked=value))

    def langAction(self):
        if all(not item.isChecked() for item in self.langActions):
            index = self.langActions.index(self.sender())
            self.langActions[index].setChecked(True)

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    tempustrainer = TempusTrainer("test")
    tempustrainer.show()
    sys.exit(app.exec_())

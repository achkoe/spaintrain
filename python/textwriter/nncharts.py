import sys
import json
import pprint
import re
from collections import OrderedDict, Counter
from PyQt5 import QtCore, QtWidgets, QtGui

try:
    from PyQt5 import QtChart
    have_modules = True
except ImportError:
    have_modules = False


def init(mainwindow):
    if not have_modules:
        return
    mainwindow.mainView.addTab(ChartWidget(mainwindow), "Chart")


class ChartWidget(QtChart.QChartView):
    PASS = 1
    FAIL = 2

    def __init__(self, mainwindow, *args):
        super(ChartWidget, self).__init__(*args)
        self.myposition = mainwindow.mainView.count()
        self.mainwindow = mainwindow
        mainwindow.mainView.currentChanged.connect(self.showChart)
        self._init = False

    def showEvent(self, *args):
        super(ChartWidget, self).showEvent(*args)
        self.adjustSeriesLabels()

    def resizeEvent(self, *args):
       # print("resizeEvent")
        super(ChartWidget, self).resizeEvent(*args)
        self.adjustSeriesLabels()


    def showChart(self, index):
        if index != self.myposition:
            return
        if self.mainwindow.overviewWidget.currentRow() < 0:
            hint = self.scene().addSimpleText("No lesson selected")
            font = hint.font()
            font.setPointSize(30)
            hint.setFont(font)
            hint.setBrush(QtCore.Qt.red)
            bbox = hint.boundingRect()
            hint.setPos(self.scene().width() / 2 - bbox.center().x(), self.scene().height() / 2 - bbox.center().y())
        else:
            lessonname = self.mainwindow.overviewWidget.item(self.mainwindow.overviewWidget.currentRow(), 0)._data
            data = self.getStatistic(lessonname)
            chart = self.getChart(lessonname, data)
            self.setChart(chart)
            # ---
            # search xlabels
            self._xlabellist = [d["name"] for d in data]
            self.xlabelitems = [item for item in self.scene().items() if isinstance(item, QtWidgets.QGraphicsTextItem) and item.toPlainText() in self._xlabellist]

            # get y labels for min and max positions
            regexp = re.compile("[01]+\.0+")
            self.ylabellist = [item for item in self.scene().items() if isinstance(item, QtWidgets.QGraphicsTextItem) and regexp.match(item.toPlainText())]

            # set custom label of every bar
            for d in data:
                d["lbl1"] = self.scene().addSimpleText(str(d[11]))
                d["lbl1"].setPen(QtCore.Qt.white)
                d["lbl2"] = self.scene().addSimpleText(str(d[12]))
                d["lbl2"].setPen(QtCore.Qt.white)

            self.customlabeloffset = data[0]["lbl1"].boundingRect().height()
            self.data = data
            self._init = True
            self.adjustSeriesLabels()

    def adjustSeriesLabels(self):
        if not self._init:
            return

        ymin, ymax = [item.y() for item in sorted(self.ylabellist, key=lambda a: a.y(), reverse=True)]
        dy = ymax - ymin

        for d in self.data:
            index = [item.toPlainText() for item in self.xlabelitems].index(d["name"])
            xpos = self.xlabelitems[index].x() + self.xlabelitems[index].boundingRect().width() / 2
            ypos = d[1] / 200.0 * dy + ymin + self.customlabeloffset
            d["lbl1"].setPos(xpos - d["lbl1"].boundingRect().width() / 2, ypos)
            ypos = (ymax + d[1] / 100 * dy + ymin) / 2 + self.customlabeloffset
            d["lbl2"].setPos(xpos - d["lbl2"].boundingRect().width() / 2, ypos)

    def getStatistic(self, lessonname):
        sessionlist = self.mainwindow.db.database[lessonname]["sessionlist"]
        sessionresultlist = []
        for session in sessionlist:
            sessionresultdict = {"name": session["name"]}
            count = Counter()
            for textitem in session["textlist"]:
                count[textitem["state"]] += 1
            total = sum(count[k] for k in [self.PASS, self.FAIL])
            sessionresultdict[10 + self.PASS] = count[self.PASS]
            sessionresultdict[10 + self.FAIL] = count[self.FAIL]
            sessionresultdict[self.PASS] = 0 if total == 0 else 100.0 * float(count[self.PASS]) / float(total)
            sessionresultdict[self.FAIL] = 0 if total == 0 else 100.0 * float(count[self.FAIL]) / float(total)
            sessionresultlist.append(sessionresultdict)
        return sessionresultlist

    def getChart(self, lessonname, data):
        series = QtChart.QStackedBarSeries()
        for key, name, color, brush in zip([self.PASS, self.FAIL], ["pass", "fail"], ["green", "red"], [QtCore.Qt.Dense1Pattern, QtCore.Qt.Dense2Pattern]):
            barset = QtChart.QBarSet(name)
            barset.append([d[key] for d in data])
            barset.setBrush(QtGui.QBrush(QtGui.QColor(color), brush))
            barset.setLabel(name)
            series.append(barset)

        series.setLabelsFormat("@value%")
        series.setLabelsVisible(True)

        chart = QtChart.QChart()
        chart.addSeries(series)
        chart.setTitle(lessonname)
        chart.setAnimationOptions(QtChart.QChart.SeriesAnimations)

        categories = [d["name"] for d in data]

        axis = QtChart.QBarCategoryAxis()
        axis.append(categories)

        chart.setAxisX(axis, series)

        axis = QtChart.QValueAxis()
        axis.setMax(100)
        axis.setMin(0)
        chart.setAxisY(axis)

        chart.legend().setVisible(True)
        return chart

if __name__ == '__main__':
    data = [{"name": "AAA", 1: 80, 2: 20}, {"name": "BB", 1: 70, 2: 30}, {"name": "CCCC", 1: 60, 2: 40}]
    def count(*args):
        return 1

    class o(object):
        _data = "Sample"
        database = {
            "Sample":
            {
                "sessionlist": [
                    {   "name": "AAA",
                        "textlist": [{"state": 0}, {"state": 1}, {"state": 2}] * 100
                    },
                    {   "name": "BBBB",
                        "textlist": [{"state": 0}, {"state": 1},{"state": 1}, {"state": 2}]
                    },
                    {   "name": "CCCCC",
                        "textlist": [{"state": 0}, {"state": 1}, {"state": 2}, {"state": 2}]
                    },
                ]
            }
        }


    def item(a, b):
        return o()

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    window.overviewWidget = QtWidgets.QTabWidget()
    window.overviewWidget.currentRow = count
    window.overviewWidget.item = item
    window.db = o()

    window.mainView = QtWidgets.QTabWidget()
    window.mainView.addTab(window.overviewWidget, "Overview")
    window.setCentralWidget(window.mainView)

    chart = ChartWidget(window)
    chart.myposition = 1
    chart.showChart(1)
    window.setCentralWidget(chart)

    window.resize(800, 800)
    window.show()
    sys.exit(app.exec_())
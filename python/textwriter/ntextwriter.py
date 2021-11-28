#!/usr/bin/env python
"""File scanned documents on screen ond organize them.

Textwriter is a PyQt GUI to
- write notes on images,
- mark notes
- move notes
- delete notes
- save notes in JSON files
and some other things.
"""

import json
import datetime
import os.path
import sys
import argparse
from collections import Counter
import pprint
from PyQt4 import QtCore, QtGui

wintitle = "Text Writer"

defaultconfig = [
    {
        "color": 4294923520,
        "font": "Noto Sans [unknown],14,-1,5,50,0,0,0,0,0",
        "name": "Default Pen"
    },
    {
        "color": 4294907027,
        "font": "Noto Sans [unknown],14,-1,5,50,0,0,0,0,0",
        "name": "Correction Pen"
    },
    {
        "color": 4278233600,
        "font": "Helvetica,14,-1,5,50,0,0,0,0,0",
        "name": "Remark Pen"
    }
]


class DataHolder(object):
    """Holds the big data.

    Implements the singular pattern.
    """
    __instance = None

    def __new__(cls):
        if DataHolder.__instance is None:
            DataHolder.__instance = object.__new__(cls)
        return DataHolder.__instance


class ExtendedQScrollArea(QtGui.QScrollArea):
    """Derived class to handle key events Control + [Up, Down, Left, Right]."""
    shiftevent = QtCore.pyqtSignal(QtGui.QKeyEvent)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Left, QtCore.Qt.Key_Right]:
            self.shiftevent.emit(event)
            event.accept()
        else:
            super(ExtendedQScrollArea, self).keyPressEvent(event)


class TextPos(object):
    """Hold data from a text item."""
    UNKNOWN, CORRECT, INCORRECT = 0, 1, 2

    def __init__(self, xpos, ypos, text, fontindex, state=UNKNOWN):
        self.x = xpos
        self.y = ypos
        self.text = text
        self.fontindex = fontindex
        self.deleted = False
        self.state = state

    def box(self, font):
        self.bbox = QtGui.QFontMetrics(font).boundingRect(self.text)
        return self


class TextEdit(QtGui.QPlainTextEdit):
    """Derived class to handle preesing Enter key in TextEdit."""
    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if 0 == int(event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier)):
                # enter key pressed without Shift or Ctrl key pressed
                event.ignore()
                return
        elif event.key() in [QtCore.Qt.Key_Tab]:
            tc = self.textCursor()
            text = unicode(self.toPlainText()).replace("~n", unichr(241)).replace("??", unichr(191)).replace("!!", unichr(161))
            self.setPlainText(text)
            self.setTextCursor(tc)
            event.accept()
            return
        super(TextEdit, self).keyPressEvent(event)

    def showEvent(self, event):
        super(TextEdit, self).showEvent(event)
        self.selectAll()


class ToolBar(QtGui.QWidget):
    """Class implemeting tool bar widget."""
    def __init__(self, parent, config):
        super(ToolBar, self).__init__()
        self.parent = parent
        self.config = config
        self.setLayout(QtGui.QVBoxLayout())
        self.btnFontList = []
        self.btnColorList = []
        self.lblList = []
        self.buttonGroup = QtGui.QButtonGroup()
        layout = self.layout()
        for index, item in enumerate(config):
            rb = QtGui.QRadioButton(item["name"])
            rb.setShortcut("Ctrl+{}".format(index + 1))
            layout.addWidget(rb)
            self.buttonGroup.addButton(rb, index)
            btn = QtGui.QPushButton("Change Font ...")
            btn.clicked.connect(self.changeFont)
            self.btnFontList.append(btn)
            layout.addWidget(btn)
            btn = QtGui.QPushButton("Change Color ...")
            btn.clicked.connect(self.changeColor)
            self.btnColorList.append(btn)
            layout.addWidget(btn)
            lbl = QtGui.QLabel("Query")
            lbl.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
            self.lblList.append(lbl)
            self.updateLabel(index)
            layout.addWidget(lbl)
            layout.addSpacing(10)
            self.buttonGroup.buttons()[0].setChecked(True)
        self.buttonGroup.buttonClicked.connect(self.fontChanged)
        layout.addStretch(1)
        sublayout = QtGui.QGridLayout()
        row = 0
        col = 0
        self.modeButtonList = []
        for lbl, shortcut in zip(["Edit", "Correct", "Wrong", "Reset", "Move", "Delete"], ["Ctrl+E", "Ctrl+C", "Ctrl+W", "Ctrl+R", "Ctrl+M", "Ctrl+D"]):
            btn = QtGui.QPushButton(lbl)
            btn.setCheckable(True)
            btn.setShortcut(shortcut)
            btn.clicked.connect(self.modeButtonClicked)
            self.modeButtonList.append(btn)
            sublayout.addWidget(btn, row >> 1, col & 1)
            row += 1
            col += 1
        layout.addLayout(sublayout)
        self.modeButtonList[0].setChecked(True)
        self.mode = str(self.modeButtonList[0].text()).lower()

    def initialize(self, config):
        self.config = config
        for index, item in enumerate(config):
            self.updateLabel(index)
            self.buttonGroup.buttons()[index].setText(item["name"])

    def modeButtonClicked(self):
        [btn.setChecked(btn == self.sender()) for btn in self.modeButtonList]
        self.mode = str(self.sender().text()).lower()

    def updateLabel(self, index):
        lbl = self.lblList[index]
        lbl.setFont(self.config[index]["font"])
        palette = lbl.palette()
        palette.setColor(lbl.foregroundRole(), self.config[index]["color"])
        lbl.setPalette(palette)

    def changeFont(self):
        index = self.btnFontList.index(self.sender())
        font, okay = QtGui.QFontDialog.getFont(self.config[index]["font"], self)
        if okay:
            self.config[index]["font"] = font
            self.updateLabel(index)

    def changeColor(self):
        index = self.btnColorList.index(self.sender())
        color = QtGui.QColorDialog.getColor(self.config[index]["color"], self)
        if color.isValid():
            self.config[index]["color"] = color
            self.updateLabel(index)

    def fontChanged(self):
        self.parent.currentFontIndex = self.buttonGroup.checkedId()


class InputDialog(QtGui.QDialog):
    """Class implementing input dialog."""
    def __init__(self):
        super(InputDialog, self).__init__()
        self.setWindowTitle("Input Text")
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.setOrientation(QtCore.Qt.Vertical)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        blayout = QtGui.QVBoxLayout()
        blayout.addStretch(1)
        blayout.addWidget(buttonBox)
        blayout.addStretch(1)
        #
        self.textedit = TextEdit()
        self.textedit.setMaximumHeight(60)
        tlayout = QtGui.QVBoxLayout()
        tlayout.addWidget(self.textedit, 1)
        #
        gridlayout = QtGui.QGridLayout()
        gridlayout.setVerticalSpacing(0)
        width = QtGui.QPushButton().fontMetrics().boundingRect("?").width() + 7
        for char, col, row in zip([unichr(191), unichr(161), unichr(241)], [0, 1, 0], [0, 0, 1]):
            btn = QtGui.QPushButton(char)
            btn.setMaximumWidth(width)
            btn.clicked.connect(self.insertChar)
            gridlayout.addWidget(btn, row, col)
            gridlayout.setColumnMinimumWidth(col, 0)
            gridlayout.setRowMinimumHeight(row, 0)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addLayout(gridlayout)
        hlayout.addLayout(tlayout)
        hlayout.addLayout(blayout)
        self.setLayout(hlayout)

    def insertChar(self):
        self.textedit.insertPlainText(self.sender().text())
        self.textedit.setFocus()

    def getData(self):
        return self.textedit.toPlainText()

    def setData(self, text):
        self.text = text
        self.textedit.setPlainText(text)

    def showEvent(self, event):
        geom = self.frameGeometry()
        pos = QtGui.QCursor.pos()
        pos.setY(pos.y() + 26)
        geom.moveTopLeft(pos)
        self.setGeometry(geom)
        self.textedit.setFocus()
        super(InputDialog, self).showEvent(event)


class ExtendedQLabel(QtGui.QLabel):
    """Derived class for drawing text on an image."""
    mouseclicked = QtCore.pyqtSignal(QtGui.QMouseEvent)

    def __init__(self, parent):
        super(ExtendedQLabel, self).__init__()
        self.db = DataHolder()
        self.parent = parent
        self.contextMenu = QtGui.QMenu(self)
        self.markCorrectAction = self.contextMenu.addAction("Correct")
        self.markIncorrectAction = self.contextMenu.addAction("Incorrect")
        self.markResetAction = self.contextMenu.addAction("Reset")
        self.deleteAction = self.contextMenu.addAction("Delete")
        self.moveAction = self.contextMenu.addAction("Move")
        self.moveIndex = None
        self.pen_lbl = QtGui.QPen(QtGui.QBrush(QtCore.Qt.SolidPattern), 1, QtCore.Qt.DotLine)
        self.pen_sts = QtGui.QPen(QtGui.QBrush(QtCore.Qt.SolidPattern), 3, QtCore.Qt.SolidLine)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseMove:
            self.update()
        return super(ExtendedQLabel, self).eventFilter(obj, event)

    def export(self, fileName):
        pixmap = self.pixmap()
        painter = QtGui.QPainter(pixmap)
        self.drawText(None, painter)
        pixmap.save(fileName)

    def print_(self, printer):
        painter = QtGui.QPainter(printer)
        rect = painter.viewport()
        size = self.pixmap().size()
        size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(self.pixmap().rect())
        painter.drawPixmap(0, 0, self.pixmap())
        self.drawText(None, painter)
        painter.end()

    def paintEvent(self, event):
        super(ExtendedQLabel, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawText(event, painter)
        painter.end()

    def drawText(self, event, qp):
        for index, textitem in enumerate(self.db.textlist):
            if textitem.deleted:
                continue
            bbox = textitem.bbox
            if self.moveIndex == index:
                pos = self.mapFromGlobal(QtGui.QCursor.pos())
                bbox.moveBottomLeft(pos)
            else:
                bbox.moveBottomLeft(QtCore.QPoint(textitem.x, textitem.y))
            if textitem.state > textitem.UNKNOWN:
                self.pen_sts.setColor([QtCore.Qt.green, QtCore.Qt.red][textitem.state - 1])
                qp.setPen(self.pen_sts)
                xp1, yp1, xp2, yp2 = bbox.getCoords()
                qp.drawLine(xp1, yp2 + 3, xp2, yp2 + 3)
            self.pen_lbl.setColor(self.db.database[self.db.lessonName]["config"][textitem.fontindex]["color"])
            qp.setPen(self.pen_lbl)
            qp.setFont(self.db.database[self.db.lessonName]["config"][textitem.fontindex]["font"])
            textitem.bbox = qp.drawText(bbox, QtCore.Qt.AlignLeft | QtCore.Qt.TextDontClip, textitem.text)
            qp.drawRect(textitem.bbox)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.moveIndex is not None:
                item = self.db.textlist[self.moveIndex]
                item.x = event.x()
                item.y = event.y()
                item.box(QtGui.QFontMetrics(self.db.database[self.db.lessonName]["config"][item.fontindex]["font"]))
                self.setCursor(QtCore.Qt.ArrowCursor)
                self.moveIndex = None
                self.db.modified = True
                self.removeEventFilter(self)
            else:
                self.mouseclicked.emit(event)
            self.update()

    def contextMenuEvent(self, event):
        xpos = event.x()
        ypos = event.y()
        index = self.parent.searchText(xpos, ypos)
        if index is None:
            return
        action = self.contextMenu.exec_(self.mapToGlobal(event.pos()))
        self.execAction(action, index)

    def execAction(self, action, index):
        if action == self.moveAction:
            self.moveIndex = index
            self.setCursor(QtCore.Qt.CrossCursor)
            self.installEventFilter(self)
        elif action == self.deleteAction:
            self.db.textlist[index].deleted = True
            self.db.modified = True
            self.update()
        elif action in [self.markCorrectAction, self.markIncorrectAction, self.markResetAction]:
            state_list = [self.db.textlist[index].CORRECT, self.db.textlist[
                index].INCORRECT, self.db.textlist[index].UNKNOWN]
            self.db.textlist[index].state = state_list[
                [self.markCorrectAction, self.markIncorrectAction, self.markResetAction].index(action)]
            self.db.modified = True
            self.update()


class ImageWriter(QtGui.QSplitter):
    """Class for displaying two images and writing on the one."""

    sig_modified = QtCore.pyqtSignal()

    def __init__(self, args, config):
        super(ImageWriter, self).__init__()
        self.textlist = []
        self.db = DataHolder()
        self.toolWidget = ToolBar(self, config)
        self.toolWidget.initialize([])
        self.addWidget(self.toolWidget)

        self.imageLabel = ExtendedQLabel(self)
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = ExtendedQScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        self.solutionLabel = QtGui.QLabel(self)
        self.solutionLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.solutionLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.solutionLabel.setScaledContents(True)
        self.scrollSolutionArea = QtGui.QScrollArea()
        self.scrollSolutionArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollSolutionArea.setWidget(self.solutionLabel)

        if (1):
            splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)
            splitter.addWidget(self.scrollArea)
            splitter.addWidget(self.scrollSolutionArea)
            splitter.setStretchFactor(0, 1)
            self.addWidget(splitter)
            sizelist = splitter.sizes()
            splitter.setSizes(sizelist)
        else:
            w = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            layout.addWidget(self.scrollArea)
            layout.addWidget(self.scrollSolutionArea)
            w.setLayout(layout)
            self.addWidget(w)

        self.setStretchFactor(1, 1)
        self.inputdialog = InputDialog()
        self.currentFontIndex = 0
        self.scrollArea.shiftevent.connect(self.shiftItem)
        self.imageLabel.mouseclicked.connect(self.mouseclicked)
        self.connected = False

    def initialize(self):
        # fix data["config"]
        self.db.textlist = []
        # new session need not to be copied
        if self.db.sessionindex > 0:
            for item in self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"]:
                self.db.textlist.append(
                    TextPos(item['x'], item['y'], item['text'], fontindex=item["fontindex"], state=int(item["state"]))
                    .box(self.db.database[self.db.lessonName]["config"][item["fontindex"]]["font"]))
        self.toolWidget.initialize(self.db.database[self.db.lessonName]["config"])
        imageName = os.path.join(os.path.dirname(str(self.db.fileName)), self.db.database[self.db.lessonName]["image"])
        image = QtGui.QImage(imageName)
        if image.isNull():
            QtGui.QMessageBox.information(self, "TextWriter", "Cannot load %s." % self.db.database[self.db.lessonName]["image"])
            return
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        self.scaleFactor = 1.0
        self.imageLabel.adjustSize()
        self.connected = True
        if "solution" in self.db.database[self.db.lessonName]:
            imageName = os.path.join(os.path.dirname(str(self.db.fileName)), self.db.database[self.db.lessonName]["solution"]["image"])
            image = QtGui.QImage(imageName)
            if image.isNull():
                return
            self.solutionLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.solutionLabel.adjustSize()

    def reset(self):
        self.db.textlist = []
        self.imageLabel.setText("None")
        self.imageLabel.adjustSize()
        if self.connected:
            self.connected = False

    def shiftItem(self, event):
        if not self.connected:
            return
        screenpos = QtGui.QCursor.pos()
        pos = self.imageLabel.mapFromGlobal(screenpos)
        index = self.searchText(pos.x(), pos.y())
        if index is None:
            return
        if event.key() == QtCore.Qt.Key_Up:
            self.db.textlist[index].y -= 1
            screenpos.setY(screenpos.y() - 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.db.textlist[index].y += 1
            screenpos.setY(screenpos.y() + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.db.textlist[index].x -= 1
            screenpos.setX(screenpos.x() - 1)
        elif event.key() == QtCore.Qt.Key_Right:
            self.db.textlist[index].x += 1
            screenpos.setX(screenpos.x() + 1)
        QtGui.QCursor.setPos(screenpos)
        self.imageLabel.update()
        self.db.modified = True
        self.sig_modified.emit()

    def mouseclicked(self, event):
        if not self.connected:
            return
        screenpos = QtGui.QCursor.pos()
        xpos = event.x()
        ypos = event.y()
        mode = self.toolWidget.mode
        index = self.searchText(xpos, ypos)
        if index is None and mode == "edit":
            # place new text
            if self.inputdialog.exec_() == QtGui.QDialog.Accepted:
                text = self.inputdialog.getData()
                if len(text) <= 0:
                    return
                self.db.textlist.append(TextPos(xpos, ypos, text, self.currentFontIndex).box(self.db.database[self.db.lessonName]["config"][self.currentFontIndex]["font"]))
                self.imageLabel.update()
                self.db.modified = True
        elif index is not None:
            if mode == "edit":
                # we like to edit existing text
                self.inputdialog.setData(self.db.textlist[index].text)
                if self.inputdialog.exec_() == QtGui.QDialog.Accepted:
                    text = self.inputdialog.getData()
                    item = self.db.textlist[index]
                    item.text = text
                    item.fontindex = self.currentFontIndex
                    item.box(self.db.database[self.db.lessonName]["config"][self.currentFontIndex]["font"])
                    self.db.modified = True
            else:
                action = [self.imageLabel.markCorrectAction, self.imageLabel.markIncorrectAction,
                          self.imageLabel.markResetAction, self.imageLabel.deleteAction,
                          self.imageLabel.moveAction][["correct", "wrong", "reset", "delete", "move"].index(mode)]
                self.imageLabel.execAction(action, index)
                self.db.modified = True
        QtGui.QCursor.setPos(screenpos)
        self.sig_modified.emit()

    def searchText(self, xpos, ypos):
        for index, textitem in enumerate(self.db.textlist):
            if textitem.bbox.contains(xpos, ypos):
                return index
        return None


class QCustomTableWidgetItem(QtGui.QTableWidgetItem):
    """Derived class to enable proper sorting of table widget items."""
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(QtCore.QString('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            selfDataValue  = str(self.data(QtCore.Qt.EditRole).toString()).split('-')[1][1:]
            otherDataValue = str(other.data(QtCore.Qt.EditRole).toString()).split('-')[1][1:]
            return int(selfDataValue) < int(otherDataValue)
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


class OverView(QtGui.QTableWidget):
    """Class implementing overview table."""
    def __init__(self):
        super(OverView, self).__init__()
        self.db = DataHolder()
        self.setColumnCount(4)
        self.setHeader()
        self.setSortingEnabled(True)

    def setHeader(self):
        self.setHorizontalHeaderLabels(["Solution", "Executed", "Results", "Name"])
        self.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignLeft)
        header = self.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(3, QtGui.QHeaderView.Stretch)

    def populateTable(self, sort=False):
        self.clear()
        self.setHeader()
        self.setRowCount(len(self.db.database.keys()))
        for row, item in enumerate(sorted(self.db.database.keys())):
            tableWidgetItem = QCustomTableWidgetItem(item)
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(row, 3, tableWidgetItem)
            # adding data
            rlist, hassolution = self.analyze(self.db.database[item])
            rstrlist = []
            plist = []
            for cnt, name in sorted(rlist, key=lambda r: r[1], reverse=True):
                p = 0 if cnt.get(2, 0) + cnt.get(1, 0) == 0 else 100.0 * cnt.get(1, 0) / (cnt.get(2, 0) + cnt.get(1, 0))
                plist.append(p)
                rstrlist.append("{name}: ok:{ok}, nok:{nok} ({p:5.1f}%)"
                                .format(name=name, ok=cnt.get(1, 0), nok=cnt.get(2, 0), p=p))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            cb = QtGui.QComboBox()
            cb.addItems(rstrlist)
            self.setCellWidget(row, 2, cb)
            # adding number
            tableWidgetItem = QtGui.QTableWidgetItem(str(len(rstrlist)))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)

            gradient = QtGui.QLinearGradient(0, 0, 100, 0)
            if len(plist) == 1:
                    # only one session executed
                    gradient.setColorAt(0, QtGui.QColor.fromRgbF(0, 0, 0.8, .5))
                    gradient.setColorAt(0.5, QtGui.QColor.fromRgbF(1, 1, 1, .5))
                    gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 0, 0.8, .5))
            elif len(plist) >= 2:
                # two or more sessions executed
                if plist[0] > plist[1]:
                    # last session better than previous section
                    gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 1, 0, 1))
                    gradient.setColorAt(0, QtGui.QColor.fromRgbF(0, 0, 0, 0))
                    # last session worser than previous section
                elif plist[0] < plist[1]:
                    gradient.setColorAt(0, QtGui.QColor.fromRgbF(1, 0, 0, 1))
                    gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 0, 0, 0))
                else:
                    # last session equal than previous section
                    gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 1, 0, 0.5))
                    gradient.setColorAt(0, QtGui.QColor.fromRgbF(0, 1, 0, 0.5))
            else:
                # no session executed
                gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 0, 0, .5))
                gradient.setColorAt(0.5, QtGui.QColor.fromRgbF(1, 1, 1, .5))
                gradient.setColorAt(0, QtGui.QColor.fromRgbF(0, 0, 0, .5))
            tableWidgetItem.setBackground(QtGui.QBrush(gradient))

            self.setItem(row, 1, tableWidgetItem)
            # adding hassolution
            tableWidgetItem = QtGui.QTableWidgetItem(str(hassolution))
            tableWidgetItem._data = item
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(row, 0, tableWidgetItem)
        #if sort:
        #    self.sortByColumn(3, QtCore.Qt.AscendingOrder)

    def analyze(self, lesson):
        result = []
        for index, item in enumerate(lesson["config"]):
            if item["name"].startswith("Default"):
                searchindex = index
                break
        for session in lesson["sessionlist"]:
            if session["name"] == "new":
                print "section 'new' skipped"
                continue
            cnt = Counter()
            for item in [i for i in session["textlist"] if i["fontindex"] == searchindex]:
                cnt[item["state"]] += 1
            result.append((cnt, session['name']))
        hassolution = "solution" in lesson
        return result, hassolution


class TextWriter(QtGui.QMainWindow):
    """Main class puting all together."""
    def __init__(self, args):
        super(TextWriter, self).__init__()
        icon = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAA3NCSVQICAjb4U/"\
               "gAAAACXBIWXMAAABvAAAAbwHxotxDAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2"\
               "NhcGUub3Jnm+48GgAAAD9QTFRF/////wAAzAAz1gAp2AAn97I/2QAm2AAn2AAn2"\
               "AAn/9pF2AAn9aU9/9pE2AAn9qk+2AAn2AAn2AAn9qo+/9pEMA0V1gAAABJ0Uk5T"\
               "AAMFHyGBjJCRrLrF5ujs+Pn6ryxQhQAAAFRJREFUGFdlj0cOgDAMBDe9d/7/VgJ"\
               "IUYLn5pFs7wITYUPOwQp8MNP6SzPsmbnrC8en0H1DA7LuokqoWMaiRAV/HXikUy"\
               "QqyAo5St6SYDQ6KferfwNgeQ3hV9pJPwAAAABJRU5ErkJggg=="
        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(QtCore.QByteArray.fromBase64(icon), "PNG"):
            self.setWindowIcon(QtGui.QIcon(pixmap))
        self.db = DataHolder()
        self.db.textlist = []
        self.writerWidget = ImageWriter(args, self.config2Qt(defaultconfig))
        self.writerWidget.sig_modified.connect(self.checkModifications)
        self.overviewWidget = OverView()
        self.overviewWidget.cellDoubleClicked.connect(self.lessonSelected)
        self.mainView = QtGui.QTabWidget()
        self.mainView.addTab(self.overviewWidget, "Overview")
        self.mainView.addTab(self.writerWidget, "Writer")
        self.setCentralWidget(self.mainView)
        self.resize(1250, 800)

        self.createActions()
        self.createMenus()

        self.db.modified = False
        #self.setWindowTitle("{}".format(wintitle))
        self.setTitle()
        if args.filename:
            self.lastfolder = os.path.dirname(args.filename)
            self.open(None, args.filename)
        else:
            self.lastfolder = str(QtCore.QDir.currentPath())

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.saveAct = QtGui.QAction("&Save...", self, shortcut="Ctrl+S", triggered=self.save, enabled=False)
        self.exportAct = QtGui.QAction("&Export...", self, shortcut="Alt+E", triggered=self.export, enabled=False)
        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P", triggered=self.print_, enabled=False)
        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.exportAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.menuBar().addMenu(self.fileMenu)
        self.sessionMenu = QtGui.QMenu("Session")
        self.sessionMenu.setEnabled(False)
        self.menuBar().addMenu(self.sessionMenu)

    def updateSessions(self, select=None):
        print "updateSessions"
        self.sessionMenu.clear()
        sessiongroup = QtGui.QActionGroup(self)
        sessionnamelist = ["new"] + [item["name"] for item in self.db.database[self.db.lessonName]["sessionlist"]]
        for index, name in enumerate(sessionnamelist):
            action = QtGui.QAction(name, self, checkable=True, triggered=self.selectSession)
            if index == select:
                action.setChecked(True)
                self.db.sessionindex = index
                self.db.sessionname = name
            action.setData((index, name))
            sessiongroup.addAction(action)
            self.sessionMenu.addAction(action)
        self.sessionMenu.setEnabled(True)

    def lessonSelected(self, row, col):
        if hasattr(self.db, "lessonName"):
            self.config2String(self.db.database[self.db.lessonName]["config"])
        if self.db.modified:
            self.askToSave()
        self.db.lessonName = self.overviewWidget.item(row, 0)._data
        self.updateSessions(0)
        self.setTitle()
        self.sessionMenu.actions()[self.db.sessionindex].setChecked(True)
        #
        self.db.modified = False
        #
        self.config2Qt(self.db.database[self.db.lessonName]["config"])
        self.writerWidget.initialize()
        self.mainView.setCurrentIndex(1)
        #
        self.exportAct.setEnabled(True)
        self.printAct.setEnabled(True)

    def config2Qt(self, config):
        for item in config:
            if isinstance(item["color"], QtGui.QColor):
                continue
            if isinstance(item["color"], unicode):
                item["color"] = int(item["color"], 0)
            color = QtGui.QColor()
            color.setRgb(item["color"])
            item["color"] = color
            font = QtGui.QFont()
            font.fromString(item['font'])
            item["font"] = font
        return config

    def config2String(self, config):
        for item in config:
            item["font"] = str(item["font"].toString())
            item["color"] = item["color"].rgb()
        return config

    def selectSession(self):
        index, name = self.sender().data().toPyObject()
        print "selectSession", index, name
        if index == self.db.sessionindex:
            return
        if self.db.modified:
            self.askToSave()
        self.db.sessionindex = index
        self.db.sessionname = name
        self.writerWidget.initialize()
        self.setTitle()

    def open(self, _, fileName=None):
        if self.db.modified:
            self.askToSave()
        if fileName is None:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", self.lastfolder, "*.jsondata")
        if fileName:
            self.db.fileName = str(fileName)
            self.lastfolder = os.path.dirname(self.db.fileName)
            self.db.database = json.load(open(fileName))
            self.overviewWidget.populateTable(sort=True)
            self.writerWidget.reset()
            self.mainView.setCurrentIndex(0)
            self.sessionMenu.setEnabled(False)
            if hasattr(self.db, "lessonName"):
                del self.db.lessonName
            if hasattr(self.db, "sessionindex"):
                del self.db.sessionindex
            self.setTitle()

    def save(self):
        print "save:", self.db.lessonName, self.db.sessionindex, self.db.sessionname, self.db.modified
        if self.db.sessionindex == 0:
            # new session
            self.db.sessionname = self._getnewname()
            self.db.database[self.db.lessonName]["sessionlist"].append({"name": self.db.sessionname, "textlist": []})
            self.db.sessionindex = len(self.db.database[self.db.lessonName]["sessionlist"])
            self.updateSessions(self.db.sessionindex)
        self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"] = []
        for item in self.db.textlist:
            if item.deleted:
                continue
            self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"].append({
                "x": item.x,
                "y": item.y,
                "text": unicode(item.text),
                "fontindex": item.fontindex,
                "state": item.state
            })
        self.db.database[self.db.lessonName]["config"] = self.config2String(self.db.database[self.db.lessonName]["config"])
        try:
            data = json.dumps(self.db.database, indent=4)
            with open(self.db.fileName, "w") as fh:
                fh.write(data)
        finally:
            self.db.database[self.db.lessonName]["config"] = self.config2Qt(self.db.database[self.db.lessonName]["config"])
        self.overviewWidget.populateTable()
        self.db.modified = False
        self.checkModifications()
        self.setTitle()

    def _getnewname(self):
        sessionlist = [item["name"] for item in self.db.database[self.db.lessonName]["sessionlist"]]
        for index in xrange(1, sys.maxint):
            sessionname = "{}-{}".format(datetime.datetime.now().strftime("%Y-%m-%d"), index)
            if sessionname not in sessionlist:
                break
        return sessionname

    def askToSave(self):
        if QtGui.QMessageBox.question(self, "Save Changes?", "File is modified. Save changes?",
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.save()

    def checkModifications(self):
        self.saveAct.setEnabled(self.db.modified)
        if self.db.modified and not str(self.windowTitle()).startswith('*'):
            self.setWindowTitle('*' + self.windowTitle())
        if not self.db.modified and str(self.windowTitle()).startswith('*'):
            self.setWindowTitle(str(self.windowTitle())[1:])

    def closeEvent(self, event):
        if self.db.modified:
            self.askToSave()
        super(TextWriter, self).closeEvent(event)

    def setTitle(self):
        title = ''
        title += os.path.basename(self.db.fileName) if hasattr(self.db, "fileName") else ""
        title += "({}".format(self.db.lessonName) if hasattr(self.db, "lessonName") else ""
        title += ":{}".format(self.db.sessionname) if hasattr(self.db, "sessionname") else ""
        title += ")"if hasattr(self.db, "lessonName") else ""
        fmt = "{0} - {1}" if hasattr(self.db, "fileName") else "{1}"
        self.setWindowTitle(fmt.format(title, wintitle))

    def debug(self):
        pprint.pprint(self.db.database[self.db.lessonName]["sessionlist"])

    def export(self):
        print("export")
        fileName = "{0}_{1}_{2}.png".format(os.path.splitext(os.path.basename(self.db.fileName))[0], self.db.lessonName, self.db.sessionname)
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Export File", fileName, "*.png")
        if not fileName:
            return
        self.writerWidget.imageLabel.export(unicode(fileName))

    def print_(self):
        printer = QtGui.QPrinter()
        fileName = "{0}_{1}_{2}.pdf".format(os.path.splitext(os.path.basename(self.db.fileName))[0], self.db.lessonName, self.db.sessionname)
        fileName = os.path.join(os.getcwd(), fileName)
        printer.setOutputFileName(fileName)
        dlg = QtGui.QPrintDialog(printer)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.writerWidget.imageLabel.print_(dlg.printer())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", default=None, nargs='?')
    args = parser.parse_args()
    textwriter = TextWriter(args)
    textwriter.show()
    sys.exit(app.exec_())

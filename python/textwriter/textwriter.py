#!/usr/bin/env python

import json
import datetime
import os.path
from PyQt4 import QtCore, QtGui

wintitle = "Text Writer"


class ExtendedQScrollArea(QtGui.QScrollArea):
    shiftevent = QtCore.pyqtSignal(QtGui.QKeyEvent)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Left, QtCore.Qt.Key_Right]:
            self.shiftevent.emit(event)
            event.accept()
        else:
            super(ExtendedQScrollArea, self).keyPressEvent(event)


class TextPos(object):
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
    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if 0 == int(event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier)):
                # enter key pressed without Shift or Ctrl key pressed
                event.ignore()
                return
        super(TextEdit, self).keyPressEvent(event)

    def showEvent(self, event):
        super(TextEdit, self).showEvent(event)
        self.selectAll()


class ToolBar(QtGui.QWidget):
    def __init__(self, parent):
        super(ToolBar, self).__init__()
        self.parent = parent
        self.config = []
        self.setLayout(QtGui.QVBoxLayout())

    def initialize(self, config):
        self.config = config
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
        for lbl in ["Edit", "Correct", "Wrong", "Reset", "Move", "Delete"]:
            btn = QtGui.QPushButton(lbl)
            btn.setCheckable(True)
            btn.clicked.connect(self.modeButtonClicked)
            self.modeButtonList.append(btn)
            sublayout.addWidget(btn, row >> 1, col & 1)
            row += 1
            col += 1
        layout.addLayout(sublayout)
        self.modeButtonList[0].setChecked(True)
        self.mode = str(self.modeButtonList[0].text()).lower()

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

    def x__init__(self):
        super(InputDialog, self).__init__()
        self.setWindowTitle("Input Text")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch(1)
        self.textedit = TextEdit()
        self.textedit.setMaximumHeight(60)
        width = QtGui.QPushButton().fontMetrics().boundingRect("?").width() + 7
        for c in [unichr(191), unichr(161), unichr(241)]:
            btn = QtGui.QPushButton(c)
            btn.setMaximumWidth(width)
            btn.clicked.connect(self.insertChar)
            hlayout.addWidget(btn)
        vlayout = QtGui.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.textedit)
        vlayout.addWidget(buttonBox)
        self.setLayout(vlayout)

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
    mouseclicked = QtCore.pyqtSignal(QtGui.QMouseEvent)

    def __init__(self, parent):
        super(ExtendedQLabel, self).__init__(parent)
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

    def paintEvent(self, event):
        super(ExtendedQLabel, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawText(event, painter)
        painter.end()

    def drawText(self, event, qp):
        for textitem in self.parent.textlist:
            if textitem.deleted:
                continue
            bbox = textitem.bbox
            bbox.moveBottomLeft(QtCore.QPoint(textitem.x, textitem.y))
            if textitem.state > textitem.UNKNOWN:
                self.pen_sts.setColor([QtCore.Qt.green, QtCore.Qt.red][textitem.state - 1])
                qp.setPen(self.pen_sts)
                xp1, yp1, xp2, yp2 = bbox.getCoords()
                qp.drawLine(xp1, yp2 + 3, xp2, yp2 + 3)
            self.pen_lbl.setColor(self.parent.data["config"][textitem.fontindex]["color"])
            qp.setPen(self.pen_lbl)
            qp.setFont(self.parent.data["config"][textitem.fontindex]["font"])
            textitem.bbox = qp.drawText(bbox, QtCore.Qt.AlignLeft | QtCore.Qt.TextDontClip, textitem.text)
            qp.drawRect(textitem.bbox)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.moveIndex is not None:
                item = self.parent.textlist[self.moveIndex]
                item.x = event.x()
                item.y = event.y()
                item.box(QtGui.QFontMetrics(self.parent.data["config"][item.fontindex]["font"]))
                self.setCursor(QtCore.Qt.ArrowCursor)
                self.moveIndex = None
                self.parent.modified = True
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
        elif action == self.deleteAction:
            self.parent.textlist[index].deleted = True
            self.parent.modified = True
            self.update()
        elif action in [self.markCorrectAction, self.markIncorrectAction, self.markResetAction]:
            state_list = [self.parent.textlist[index].CORRECT, self.parent.textlist[
                index].INCORRECT, self.parent.textlist[index].UNKNOWN]
            self.parent.textlist[index].state = state_list[
                [self.markCorrectAction, self.markIncorrectAction, self.markResetAction].index(action)]
            self.parent.modified = True
            self.update()


class TextWriter(QtGui.QMainWindow):
    def __init__(self, fileName=None, session=None):
        super(TextWriter, self).__init__()

        icon = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAABvAAAAbwHxotxDAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAD9QTFRF/////wAAzAAz1gAp2AAn97I/2QAm2AAn2AAn2AAn/9pF2AAn9aU9/9pE2AAn9qk+2AAn2AAn2AAn9qo+/9pEMA0V1gAAABJ0Uk5TAAMFHyGBjJCRrLrF5ujs+Pn6ryxQhQAAAFRJREFUGFdlj0cOgDAMBDe9d/7/VgJIUYLn5pFs7wITYUPOwQp8MNP6SzPsmbnrC8en0H1DA7LuokqoWMaiRAV/HXikUyQqyAo5St6SYDQ6KferfwNgeQ3hV9pJPwAAAABJRU5ErkJggg=="
        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(QtCore.QByteArray.fromBase64(icon), "PNG"):
            self.setWindowIcon(QtGui.QIcon(pixmap))

        self.textlist = []
        self.modified = False
        self.fileName = fileName
        self.currentFontIndex = 0
        self.maxRecentFiles = 4
        self.printer = QtGui.QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = ExtendedQLabel(self)
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.mouseclicked.connect(self.mouseclicked)

        self.scrollArea = ExtendedQScrollArea()
        self.scrollArea.shiftevent.connect(self.shiftItem)
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()

        self.inputdialog = InputDialog()
        self.toolWidget = ToolBar(self)
        self.toolDock = QtGui.QDockWidget()
        self.toolDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.toolDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetMovable)
        self.toolDock.setWidget(self.toolWidget)
        self.toolDock.visibilityChanged.connect(self.fontEditorVisibilityChanged)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.toolDock)

        self.solutionLabel = QtGui.QLabel(self)
        self.solutionLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.solutionLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.solutionLabel.setScaledContents(True)
        self.scrollSolutionArea = QtGui.QScrollArea()
        self.scrollSolutionArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollSolutionArea.setWidget(self.solutionLabel)
        self.solutionDock = QtGui.QDockWidget()
        self.solutionDock.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.solutionDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.solutionDock.setWidget(self.scrollSolutionArea)

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.solutionDock)
        self.solutionDock.hide()

        self.createMenus()

        self.setWindowTitle(wintitle)
        self.resize(1200, 800)
        self.open(False, fileName=self.fileName, session=session)

    def shiftItem(self, event):
        screenpos = QtGui.QCursor.pos()
        pos = self.imageLabel.mapFromGlobal(screenpos)
        index = self.searchText(pos.x(), pos.y())
        if index is None:
            return
        if event.key() == QtCore.Qt.Key_Up:
            self.textlist[index].y -= 1
            screenpos.setY(screenpos.y() - 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.textlist[index].y += 1
            screenpos.setY(screenpos.y() + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.textlist[index].x -= 1
            screenpos.setX(screenpos.x() - 1)
        elif event.key() == QtCore.Qt.Key_Right:
            self.textlist[index].x += 1
            screenpos.setX(screenpos.x() + 1)
        QtGui.QCursor.setPos(screenpos)
        self.imageLabel.update()
        self.modified = True

    def mouseclicked(self, event):
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
                self.textlist.append(TextPos(xpos, ypos, text, self.currentFontIndex).box(self.data["config"][self.currentFontIndex]["font"]))
                self.imageLabel.update()
                self.modified = True
        elif index  is not None:
            if mode == "edit":
                # we like to edit existing text
                self.inputdialog.setData(self.textlist[index].text)
                if self.inputdialog.exec_() == QtGui.QDialog.Accepted:
                    text = self.inputdialog.getData()
                    item = self.textlist[index]
                    item.text = text
                    item.fontindex = self.currentFontIndex
                    item.box(self.data["config"][self.currentFontIndex]["font"])
                    self.modified = True
            else:
                action = [self.imageLabel.markCorrectAction, self.imageLabel.markIncorrectAction,
                          self.imageLabel.markResetAction, self.imageLabel.deleteAction,
                          self.imageLabel.moveAction][["correct", "wrong", "reset", "delete", "move"].index(mode)]
                self.imageLabel.execAction(action, index)
        QtGui.QCursor.setPos(screenpos)

    def searchText(self, xpos, ypos):
        for index, textitem in enumerate(self.textlist):
            if textitem.bbox.contains(xpos, ypos):
                return index
        return None

    def save(self):
        sessionlist = [item["name"] for item in self.data["sessionlist"]]
        index = 0
        while True:
            index += 1
            session = "{} ({})".format(datetime.datetime.now().strftime("%Y-%m-%d"), index)
            if session not in sessionlist:
                break
        self.data["sessionlist"][self.sessionindex]["name"] = session

        self.data["sessionlist"][self.sessionindex]["textlist"] = []
        for item in self.textlist:
            if item.deleted:
                continue
            self.data["sessionlist"][self.sessionindex]["textlist"].append({
                "x": item.x,
                "y": item.y,
                "text": unicode(item.text),
                "fontindex": item.fontindex,
                "state": item.state
            })

        self.data["config"] = self.config2String(self.data["config"])
        json.dump(self.data, open(self.fileName, "w"), indent=4)
        self.data["config"] = self.config2Qt(self.data["config"])
        self.modified = False
        self.open(None, self.fileName, self.sessionindex)

    def closeEvent(self, event):
        if self.modified:
            self.askSaveModifications()
        super(TextWriter, self).closeEvent(event)

    def open(self, state, fileName=None, session=None):
        if self.modified:
            self.askSaveModifications()
        if fileName is None:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath(), "*.json")
        if fileName:
            self.data = json.load(open(fileName))
            self.imageName = os.path.join(os.path.dirname(str(fileName)), self.data["image"])
            image = QtGui.QImage(self.imageName)
            if image.isNull():
                QtGui.QMessageBox.information(self, "TextWriter", "Cannot load %s." % self.data["image"])
                return
            # update session menu
            self.sessionMenu.clear()
            sessiongroup = QtGui.QActionGroup(self)
            for index, name in enumerate(["new"] + [item["name"] for item in self.data["sessionlist"]]):
                action = QtGui.QAction(name, self, checkable=True, triggered=self.selectSession)
                action.setData(index)
                sessiongroup.addAction(action)
                self.sessionMenu.addAction(action)
            #
            if session is None:
                session = "new"
                self.data["sessionlist"].insert(0, {"name": session, "textlist": []})
                self.sessionindex = 0
            else:
                self.sessionindex = session

            self.modified = False

            self.sessionMenu.actions()[self.sessionindex].setChecked(True)
            # fix data["config"]
            self.config2Qt(self.data["config"])
            self.textlist = []
            for item in self.data["sessionlist"][self.sessionindex]["textlist"]:
                self.textlist.append(
                    TextPos(item['x'], item['y'], item['text'], fontindex=item["fontindex"], state=int(item["state"]))
                    .box(self.data["config"][item["fontindex"]]["font"]))

            # delete all widgets in fonteditor and set fonteditor
            while self.toolWidget.layout().count():
                item = self.toolWidget.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.toolWidget.initialize(self.data["config"])
            self.viewSolutionAct.setEnabled("solution" in self.data)

            self.fileName = fileName

            self.setWindowTitle("{} - {} - {}".format(wintitle, os.path.splitext(os.path.basename(str(fileName)))[0],
                self.data["sessionlist"][self.sessionindex]["name"]))
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()
            self.adjustForCurrentFile(fileName)

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def selectSession(self):
        session, _ = self.sender().data().toInt()
        if session == 0:
            # new session
            session = None
        else:
            session -= 1
        self.open(None, self.fileName, session)

    def config2Qt(self, config):
        for item in config:
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

    def askSaveModifications(self):
        if QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(self, "Warning: file modified", "Save changes to modified file?",
                                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                               QtGui.QMessageBox.Yes):
            self.save()

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QtGui.QMessageBox.about(self, "About Text Writer",
                                "<p>The <b>Text Writer</b> program allows for drawing text "
                                "on top of an image with different fonts and colors.</p>"
                                "<p>The result can be saved in json files. Main purpose is "
                                "filling scanned pages e.g. for learning a language when "
                                "you don't want to write in a book.</p>")

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                                     triggered=self.open)

        self.saveAct = QtGui.QAction("&Save...", self, shortcut="Ctrl+S",
                                     triggered=self.save)

        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
                                      enabled=False, triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                                     triggered=self.close)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                                       shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                                        shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                                           shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                                            enabled=False, checkable=True, shortcut="Ctrl+F",
                                            triggered=self.fitToWindow)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self, triggered=QtGui.qApp.aboutQt)

        self.toggleToolBarAct = QtGui.QAction("Font Editor", self, shortcut="Ctrl+E", checkable=True, triggered=self.toggleToolBar, checked=True)

        self.viewSolutionAct = QtGui.QAction("Show solution", self, triggered=self.showSolution, enabled=False)
        #self.viewSolutionAct = self.solutionDock.toggleViewAction()
        #self.viewSolutionAct.triggered =self.showSolution
        #self.viewSolutionAct.enabled = False

        self.recentFileActionList = []
        for index in range(1, self.maxRecentFiles + 1):
            recentFileAct = QtGui.QAction(self, triggered=self.openRecent)
            recentFileAct.setVisible(False)
            self.recentFileActionList.append(recentFileAct)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        recentFilesMenu = self.fileMenu.addMenu("Open Recent")
        for index in range(self.maxRecentFiles):
            recentFilesMenu.addAction(self.recentFileActionList[index])
        self.updateRecentActionList()

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.toggleToolBarAct)
        self.viewMenu.addAction(self.viewSolutionAct)

        self.sessionMenu = QtGui.QMenu("Session")

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.sessionMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2)))

    def toggleToolBar(self):
        self.toolDock.toggleViewAction().activate(QtGui.QAction.Trigger)

    def fontEditorVisibilityChanged(self, state):
        self.toggleToolBarAct.setChecked(state)

    def showSolution(self):
        imageName = os.path.join(os.path.dirname(str(self.fileName)), self.data["solution"]["image"])
        image = QtGui.QImage(imageName)
        self.solutionLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        self.solutionLabel.adjustSize()
        self.solutionDock.toggleViewAction().activate(QtGui.QAction.Trigger)

    def openRecent(self):
        action = self.sender()
        if action:
            self.open(None, str(action.data))

    def updateRecentActionList(self):
        recentFileList = QtCore.QStringList(self.readConfig()["recentfiles"])
        index = 0
        for index in range(min(len(recentFileList), self.maxRecentFiles)):
            self.recentFileActionList[index].setText(QtCore.QFileInfo(recentFileList[index]).fileName())
            self.recentFileActionList[index].data = recentFileList[index]
            self.recentFileActionList[index].setVisible(True)
        while index < self.maxRecentFiles:
            self.recentFileActionList[index].setVisible(False)
            index += 1

    def adjustForCurrentFile(self, fileName):
        cfg = self.readConfig()
        recentFileList = QtCore.QStringList(cfg["recentfiles"])
        recentFileList.removeAll(fileName)
        recentFileList.prepend(fileName)
        while len(recentFileList) > self.maxRecentFiles:
            recentFileList.removeAt(len(recentFileList) - 1)
        cfg["recentfiles"] = [str(item) for item in recentFileList]
        self.saveConfig(cfg)
        self.updateRecentActionList()

    def readConfig(self):
        try:
            config = json.load(open("textwriter.config"))
        except:
            config = {"recentfiles": []}
        return config

    def saveConfig(self, config):
        json.dump(config, open("textwriter.config", 'w'))


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", default=None, nargs='?')
    parser.add_argument("session", default=None, nargs='?', type=int)
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    if 0:
        d = InputDialog()
        d.exec_()
    else:
        textwriter = TextWriter(args.filename, args.session)
        textwriter.show()
        sys.exit(app.exec_())

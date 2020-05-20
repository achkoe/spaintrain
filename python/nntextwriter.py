#!/usr/bin/env python3
"""File scanned documents on screen ond organize them.

Textwriter is a PyQt GUI to
- write notes on images,
- mark notes
- move notes
- delete notes
- save notes in JSON files
And some other things.

It used PyQt5 and Python, tested with PyQt5.8 and Python 3.6.
"""

import json
import datetime
import os.path
import sys
import argparse
from collections import Counter
import pprint
import logging
import traceback
import random
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
#import nncharts

wintitle = "Text Writer"
"""str: Windows Title shown in the title bar."""

MAXRECENTFILES = 4
"""int: maximum number of recent files"""

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
"""Default configuration of fonts and pens."""


class DataHolder(object):
    """Holds the big data.

    Implements the singular pattern.
    """
    __instance = None

    def __new__(cls):
        if DataHolder.__instance is None:
            DataHolder.__instance = object.__new__(cls)
        return DataHolder.__instance


class TextEdit(QtWidgets.QPlainTextEdit):
    """Derived class to handle pressing Enter key and for special replacements with Tab key in TextEdit."""

    def keyPressEvent(self, event):
        """Handle keypress event.

        Ignores Enter key without Shift or Ctrl.
        Replaces the key sequences ~n, ??, !! followed by Tab with unicode charceters.
        """
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if 0 == int(event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier)):
                # 'enter' key pressed without Shift or Ctrl key pressed
                event.ignore()
                return
        elif event.key() in [QtCore.Qt.Key_Tab]:
            # 'tab' key pressed, replace ~n, ??, !!
            tc = self.textCursor()
            text = self.toPlainText().replace("~n", chr(241)).replace("??", chr(191)).replace("!!", chr(161))
            self.setPlainText(text)
            self.setTextCursor(tc)
            event.accept()
            return
        super(TextEdit, self).keyPressEvent(event)

    def showEvent(self, event):
        """Call selectAll() on show."""
        super(TextEdit, self).showEvent(event)
        self.selectAll()


class ToolBar(QtWidgets.QWidget):
    """Class implemeting tool bar widget."""

    sig_modechange = QtCore.pyqtSignal(str)
    """Signal is emitted when anything in toolbar changes."""

    def __init__(self, parent, config):
        """Setup toolbar.

        Args:
            parent (QtWidgets.QWidget): arent of the widget
            config (list): configuration
        """
        super(ToolBar, self).__init__()
        # Initialize variables
        self.parent = parent
        self.config = config
        self.setLayout(QtWidgets.QVBoxLayout())
        self.btnFontList = []
        self.btnColorList = []
        self.lblList = []
        self.buttonGroup = QtWidgets.QButtonGroup()
        layout = self.layout()
        # create elements for each entry in config
        for index, item in enumerate(config):
            # radiobutton in group to select the pen
            rb = QtWidgets.QRadioButton(item["name"])
            rb.setShortcut("Ctrl+{}".format(index + 1))
            layout.addWidget(rb)
            self.buttonGroup.addButton(rb, index)
            # buttons to change font and color
            btn = QtWidgets.QPushButton("Change Font ...")
            btn.clicked.connect(self.changeFont)
            self.btnFontList.append(btn)
            layout.addWidget(btn)
            btn = QtWidgets.QPushButton("Change Color ...")
            btn.clicked.connect(self.changeColor)
            self.btnColorList.append(btn)
            layout.addWidget(btn)
            # label to show sample of current font and color
            lbl = QtWidgets.QLabel("Query")
            lbl.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
            self.lblList.append(lbl)
            self.updateLabel(index)
            layout.addWidget(lbl)
            layout.addSpacing(10)
            self.buttonGroup.buttons()[0].setChecked(True)
        self.buttonGroup.buttonClicked.connect(self.fontChanged)
        layout.addStretch(1)
        # buttons for different  modes
        sublayout = QtWidgets.QGridLayout()
        row = 0
        col = 0
        self.modeButtonList = []
        zipped = zip(
            ["&Edit", "&Correct", "&Wrong", "&Reset", "&Move", "&Delete"],
            ["Ctrl+E", "Ctrl+C", "Ctrl+W", "Ctrl+R", "Ctrl+M", "Ctrl+D"],
            ["edit", "correct", "wrong", "reset", "move", "delete"])
        for lbl, shortcut, prop in zipped:
            btn = QtWidgets.QPushButton(lbl)
            btn.setCheckable(True)
            btn.setShortcut(shortcut)
            btn.setProperty("mode", prop)
            btn.clicked.connect(self.modeButtonClicked)
            self.modeButtonList.append(btn)
            sublayout.addWidget(btn, row >> 1, col & 1)
            row += 1
            col += 1
        layout.addLayout(sublayout)
        self.modeButtonList[0].setChecked(True)
        self.mode = self.modeButtonList[0].property("mode")

    def initialize(self, config):
        """Initialize widgets with config.

        Args:
            config (list): configuration
        """
        self.config = config
        for index, item in enumerate(config):
            self.updateLabel(index)
            self.buttonGroup.buttons()[index].setText(item["name"])

    def modeButtonClicked(self):
        """Set self.mode and emit sig_modechange on mode button click."""
        [btn.setChecked(btn == self.sender()) for btn in self.modeButtonList]
        self.mode = self.sender().property("mode")
        self.sig_modechange.emit(self.mode)

    def updateLabel(self, index):
        """Update label to show the font and color.

        Args:
            index (int): index in self.config
        """
        lbl = self.lblList[index]
        lbl.setFont(self.config[index]["font"])
        palette = lbl.palette()
        palette.setColor(lbl.foregroundRole(), self.config[index]["color"])
        lbl.setPalette(palette)

    def changeFont(self):
        """Call font selection dialog and update config and labels."""
        index = self.btnFontList.index(self.sender())
        font, okay = QtWidgets.QFontDialog.getFont(self.config[index]["font"], self)
        if okay:
            self.config[index]["font"] = font
            self.updateLabel(index)

    def changeColor(self):
        """Call color selection dialog and update config and labels."""
        index = self.btnColorList.index(self.sender())
        color = QtWidgets.QColorDialog.getColor(self.config[index]["color"], self)
        if color.isValid():
            self.config[index]["color"] = color
            self.updateLabel(index)

    def fontChanged(self):
        """Updae current font in parent."""
        self.parent.currentFontIndex = self.buttonGroup.checkedId()


class InputDialog(QtWidgets.QDialog):
    """Class implementing input dialog."""

    def __init__(self):
        """Setup dialog.

        A dialog with textedit, some replacement buttons and standard buttons is constructed.
        """
        super(InputDialog, self).__init__()
        self.setWindowTitle("Input Text")
        # standard buttons
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.setOrientation(QtCore.Qt.Vertical)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        # add textedit
        self.textedit = TextEdit()
        #self.textedit.setMaximumHeight(80)
        #
        layout = QtWidgets.QGridLayout()
        # add buttons in gridlayout for special characters
        width = QtWidgets.QPushButton().fontMetrics().boundingRect("?").width() + 7
        for char, col, row in zip([chr(191), chr(161), chr(241)], [0, 1, 0], [0, 0, 1]):
            btn = QtWidgets.QPushButton(char)
            btn.setMaximumWidth(width)
            btn.clicked.connect(self.insertChar)
            layout.addWidget(btn, row, col)
        layout.addWidget(self.textedit, 0, 2, -1, 1)
        layout.addWidget(buttonBox, 0, 3, -1, 1)
        self.setLayout(layout)


    def insertChar(self):
        """Slot called when special character butto pressed."""
        self.textedit.insertPlainText(self.sender().text())
        self.textedit.setFocus()

    def getData(self):
        """Get dialog data."""
        return self.textedit.toPlainText()

    def setData(self, text):
        """Set dialog data."""
        self.textedit.setPlainText(text)

    def showEvent(self, event):
        """Set dialog pos ner to position of mouse click on showing dialog."""
        geom = self.frameGeometry()
        pos = QtGui.QCursor.pos()
        pos.setY(pos.y() + 26)
        geom.moveTopLeft(pos)
        self.setGeometry(geom)
        self.textedit.setFocus()
        super(InputDialog, self).showEvent(event)
        self.adjustSize()


class TWGraphicsView(QtWidgets.QGraphicsView):
    """Derived class for drawing text on an image."""
    sig_mouseclicked = QtCore.pyqtSignal(QtGui.QMouseEvent)
    """Emitted signal for mouse click."""
    sig_modified = QtCore.pyqtSignal()
    """Emitted signal whe change occured."""

    def __init__(self, parent):
        """Setup class.

        Initialize variables, initialize context menu.

        Args:
            parent (QtWidgets.QWidget): parent view
        """
        super(TWGraphicsView, self).__init__()
        self.setScene(QtWidgets.QGraphicsScene())
        parent.toolWidget.sig_modechange.connect(self.modeChange)
        self.colors = [QtGui.QColor(0, 0, 0, 0), QtGui.QColor(22, 236, 8), QtGui.QColor(236, 22, 8)]
        self.widths = [0, 3, 3]
        self.db = DataHolder()
        self.parent = parent
        self.compatibleMode = False
        self.contextMenu = QtWidgets.QMenu(self)
        self.markCorrectAction = self.contextMenu.addAction("Correct")
        self.markIncorrectAction = self.contextMenu.addAction("Incorrect")
        self.markResetAction = self.contextMenu.addAction("Reset")
        self.deleteAction = self.contextMenu.addAction("Delete")
        self.pen_lbl = QtGui.QPen(QtGui.QBrush(QtCore.Qt.SolidPattern), 1, QtCore.Qt.DotLine)
        self.pen_sts = QtGui.QPen(QtGui.QBrush(QtCore.Qt.SolidPattern), 3, QtCore.Qt.SolidLine)
        self.setMouseTracking(True)

    def keyPressEvent(self, e):
        key = e.key()
        keylist = [QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]
        if e.modifiers() != QtCore.Qt.ControlModifier or key not in keylist:
            return
        pos = self.cursor().pos()
        scenePoint = self.mapToScene(self.mapFromGlobal(pos))
        itemlist = [item for item in self.scene().items(scenePoint) if isinstance(item, QtWidgets.QGraphicsItemGroup)]
        if len(itemlist) == 0:
            return
        delta = [(-1, 0), (+1, 0), (0, -1), (0, +1)][keylist.index(key)]
        ipos = itemlist[0].pos()
        ipos.setX(ipos.x() + delta[0])
        ipos.setY(ipos.y() + delta[1])
        itemlist[0].setPos(ipos)
        self.cursor().setPos(pos.x() + delta[0], pos.y() + delta[1])
        self.sig_modified.emit()

    def initialize(self, filename):
        """Clear scene and set background image.

        Args:
            filename (str): file name of background image
        """
        self.scene().clear()
        self.scene().addPixmap(QtGui.QPixmap(filename))

    def export(self, filename):
        """Write current scene to a image file.

        Args:
            filename (str): name of export file
        """
        image = QtGui.QImage(self.scene().sceneRect().size().toSize(), QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.scene().render(painter)
        image.save(filename)

    def print_(self, printer):
        """Print current scene.

        Args:
            printer (QtCore.QPrinter): printer to print on
        """
        painter = QtGui.QPainter(printer)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.scene().clearSelection()
        self.scene().render(painter)

    def mousePressEvent(self, event):
        """Slot for mouse pressed event.

        If current mode is not 'move' the sig_mouseclicked event is emitted.
        """
        logging.debug("TWGraphicsView.mousePressEvent")
        if event.button() == QtCore.Qt.LeftButton:
            logging.debug(self.parent.toolWidget.mode)
            if self.parent.toolWidget.mode in ["edit", "delete", "correct", "wrong", "reset"]:
                self.sig_mouseclicked.emit(event)
            elif self.parent.toolWidget.mode in ["move"]:
                self.sig_modified.emit()
        super(TWGraphicsView, self).mousePressEvent(event)

    def contextMenuEvent(self, event):
        """Slot for context menu event.

        Args:
            event (QtCore.QMouseEvent): the event
        """
        logging.debug("TWGraphicsView.contextMenuEvent")
        index = self.searchText(event)
        if index is None:
            return
        action = self.contextMenu.exec_(self.mapToGlobal(event.pos()))
        self.execAction(action, index)

    def execAction(self, action, item):
        """Execute an action.

        Args:
            action (QtWidgets.QAction): one of the class actions definde in __init__
            item (QtWidgets.QGraphicsItemGroup): the item for this action
        """
        logging.debug("TWGraphicsView.execAction")
        actionlist = [self.markResetAction, self.markCorrectAction, self.markIncorrectAction]
        if action == self.deleteAction:
            self.scene().removeItem(item)
        elif action in actionlist:
            textitem, decoitem = self.extractItems(item)
            state = actionlist.index(action)
            textitem.setData(0, state)
            pen = QtGui.QPen(QtGui.QColor(self.colors[state]))
            pen.setWidth(self.widths[state])
            decoitem.setPen(pen)
        self.sig_modified.emit()

    def addText(self, event, text, configindex, state=0, map=True):
        """Add new text to scene.

        Args:
            event (QtCore.QMouseEvent): the event with position information
            text (str): text to be added
            configindex (int): inden to configuration
            state (int): indicatiin of state, 0: notselected, 1: correct, 2: wrong
            map (bool): flag if calling mapToScene() is required

        A new QGraphicsItemGroup is created, data 0 of QGraphicsItemGroup holds the state, data 1 the configindex.
        The QGraphicsItemGroup is populated with QGraphicsLineItem and QGraphicsSimpleTextItem and the group
        is rendered at the required position.
        """
        mpos = self.mapToScene(event.pos()) if map else event.pos()
        item = QtWidgets.QGraphicsItemGroup()
        textitem = QtWidgets.QGraphicsSimpleTextItem(text)
        config = self.db.database[self.db.lessonName]["config"][configindex]
        textitem.setFont(config["font"])
        textitem.setBrush(QtGui.QBrush(config["color"]))
        textitem.setData(0, state)
        textitem.setData(1, configindex)
        bbox = textitem.boundingRect()
        decoitem = QtWidgets.QGraphicsLineItem(bbox.left(), bbox.bottom(), bbox.right(), bbox.bottom())
        pen = QtGui.QPen(QtGui.QColor(self.colors[state]))
        pen.setWidth(self.widths[state])
        decoitem.setPen(pen)
        item.addToGroup(decoitem)
        item.addToGroup(textitem)
        self.scene().addItem(item)
        # set item bottom left corner to mouse pos
        mpos.setY(mpos.y() - (bbox.bottom() - bbox.top()))
        # fix y to ensure compatibility with previous versions
        if self.compatibleMode:
            mpos.setY(mpos.y() + bbox.bottom())
        item.setPos(mpos)
        self.sig_modified.emit()

    def extractItems(self, itemgroup):
        """Extract items from an itemgroup.

        Args:
            itemgroup (QtWidgets.QGraphicsItemGroup): item group to extract

        Returns:
            Tuple (textitem, decoitem)
        """
        itemlist = itemgroup.childItems()
        typelist = [type(_item) for _item in itemlist]
        textitem = itemlist[typelist.index(QtWidgets.QGraphicsSimpleTextItem)]
        decoitem = itemlist[typelist.index(QtWidgets.QGraphicsLineItem)]
        return textitem, decoitem

    def updateItem(self, itemgroup, text, configindex):
        """Update an existing item group.

        Args:
            itemgroup (QtWidgets.QGraphicsItemGroup): tem group to be updated
            text (str): new text
            configindex (int): new configindex

        The signal sig_modified is emitted.
        """
        config = self.parent.toolWidget.config[configindex]
        textitem, decoitem = self.extractItems(itemgroup)
        itemgroup.removeFromGroup(textitem)
        itemgroup.removeFromGroup(decoitem)
        textitem.setText(text)
        textitem.setData(1, configindex)
        textitem.setFont(config["font"])
        textitem.setBrush(QtGui.QBrush(config["color"]))
        bbox = textitem.boundingRect()
        decoitem.setLine(bbox.left(), bbox.bottom(), bbox.right(), bbox.bottom())
        itemgroup.addToGroup(textitem)
        itemgroup.addToGroup(decoitem)
        self.sig_modified.emit()

    def searchText(self, event):
        """Search for an item and position of event.

        Args:
            event (QtCore.QMouseEvent): event

        Returns:
            None if no item is at position of event, else the itemgroup at given position.
        """
        mpos = self.mapToScene(event.pos())
        itemlist = self.scene().items(mpos)
        # remove background
        del itemlist[[type(item) for item in itemlist].index(QtWidgets.QGraphicsPixmapItem)]
        return None if len(itemlist) == 0 else itemlist[0].parentItem()

    def modeChange(self, mode):
        """Handle change of mode.

        Args:
            mode (str): one of 'move', 'delete', ...
        """
        logging.debug("TWGraphicsView.modeChange")
        for item in self.scene().items():
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                continue
            if mode == "move":
                item.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
            else:
                item.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)


class ImageWriter(QtWidgets.QSplitter):
    """Class for displaying two images and writing on the one."""

    def __init__(self, args, config):
        """Setup toolbar and arrange the widgets for the two images in a splitter.

        Args:
            args (argparse.Namespace): arguments from command line
            config (list): configuration
        """
        super(ImageWriter, self).__init__()
        self.textlist = []
        self.db = DataHolder()
        self.toolWidget = ToolBar(self, config)
        self.toolWidget.initialize([])
        self.addWidget(self.toolWidget)

        self.imageLabel = TWGraphicsView(self)

        self.solutionLabel = QtWidgets.QLabel(self)
        self.solutionLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.solutionLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.solutionLabel.setScaledContents(True)
        self.scrollSolutionArea = QtWidgets.QScrollArea()
        self.scrollSolutionArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollSolutionArea.setWidget(self.solutionLabel)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        splitter.addWidget(self.imageLabel)
        splitter.addWidget(self.scrollSolutionArea)
        splitter.setStretchFactor(0, 1)
        self.addWidget(splitter)
        sizelist = splitter.sizes()
        splitter.setSizes(sizelist)

        self.setStretchFactor(1, 1)
        self.inputdialog = InputDialog()
        self.currentFontIndex = 0
        self.imageLabel.sig_mouseclicked.connect(self.mouseclicked)
        self.connected = False

    def initialize(self):
        """Initialize widget with selected lesson and session.
        """
        class Event(QtCore.QPoint):
            """Helper class to emulate event."""
            def pos(self):
                return self
        # new session need not to be copied
        self.toolWidget.initialize(self.db.database[self.db.lessonName]["config"])
        imageName = os.path.join(os.path.dirname(str(self.db.fileName)), self.db.database[self.db.lessonName]["image"])
        image = QtGui.QImage(imageName)
        if image.isNull():
            QtWidgets.QMessageBox.information(self, "TextWriter", "Cannot load %s." % self.db.database[self.db.lessonName]["image"])
            return
        self.imageLabel.initialize(imageName)
        if self.db.sessionindex > 0:
            for item in self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"]:
                event = Event(item['x'], item['y'])
                self.imageLabel.addText(event, item['text'], item["fontindex"], item['state'], False)
        self.connected = True
        if "solution" in self.db.database[self.db.lessonName]:
            imageName = os.path.join(os.path.dirname(str(self.db.fileName)), self.db.database[self.db.lessonName]["solution"]["image"])
            image = QtGui.QImage(imageName)
            if image.isNull():
                return
            self.solutionLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.solutionLabel.adjustSize()

    def reset(self):
        if self.connected:
            self.connected = False

    def mouseclicked(self, event):
        """Handle mouse click.

        Args:
            event (QtCore.QMouseEvent): the event

        Take actions depending on current mode.
        """
        if not self.connected:
            return
        logging.debug("ImageWriter.mouseclicked")
        screenpos = QtGui.QCursor.pos()
        mode = self.toolWidget.mode
        logging.debug("mode: {mode}".format(mode=mode))
        item = self.imageLabel.searchText(event)
        if item is None and mode == "edit":
            # place new text
            if self.inputdialog.exec_() == QtWidgets.QDialog.Accepted:
                text = self.inputdialog.getData()
                if len(text) <= 0:
                    return
                logging.debug("appended {}".format(text))
                self.imageLabel.addText(event, text, self.currentFontIndex)
        elif item is not None:
            if mode == "edit":
                # we like to edit existing text
                textitem, decoitem = self.imageLabel.extractItems(item)
                self.inputdialog.setData(textitem.text())
                if self.inputdialog.exec_() == QtWidgets.QDialog.Accepted:
                    text = self.inputdialog.getData()
                    self.imageLabel.updateItem(item, text, self.currentFontIndex)
            else:
                action = [self.imageLabel.markCorrectAction, self.imageLabel.markIncorrectAction,
                          self.imageLabel.markResetAction, self.imageLabel.deleteAction][["correct", "wrong", "reset", "delete"].index(mode)]
                self.imageLabel.execAction(action, item)
        QtGui.QCursor.setPos(screenpos)


class QCustomTableWidgetItem(QtWidgets.QTableWidgetItem):
    """Derived class to enable proper sorting of table widget items."""
    def __init__(self, value):
        super(QCustomTableWidgetItem, self).__init__('%s' % value)

    def __lt__(self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            selfDataValue = str(self.data(QtCore.Qt.EditRole)).split('-')[1][1:]
            otherDataValue = str(other.data(QtCore.Qt.EditRole)).split('-')[1][1:]
            return int(selfDataValue) < int(otherDataValue)
        else:
            return QtWidgets.QTableWidgetItem.__lt__(self, other)


class OverView(QtWidgets.QTableWidget):
    """Class implementing overview table."""
    def __init__(self):
        """Initialize object."""
        super(OverView, self).__init__()
        self.db = DataHolder()
        self.setColumnCount(4)
        self.setHeader()
        self.setSortingEnabled(True)

    def setHeader(self):
        """Set header and resize column width."""
        self.setHorizontalHeaderLabels(["Solution", "Executed", "Results", "Name"])
        self.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignLeft)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

    def populateTable(self, sort=False):
        """Fill the table from self.db"""
        self.clear()
        self.setHeader()
        self.setRowCount(len(self.db.database.keys()))
        # loop over all keys
        for row, item in enumerate(sorted(self.db.database.keys())):
            # set title or item in last column of table
            name = item if "title" not in self.db.database[item] else self.db.database[item]["title"]
            tableWidgetItem = QCustomTableWidgetItem(name)
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(row, 3, tableWidgetItem)
            # adding statistics data in column 2
            rlist, hassolution = self.analyze(self.db.database[item])
            rstrlist = []
            plist = []
            for cnt, name in sorted(rlist, key=lambda r: r[1], reverse=True):
                p = 0 if cnt.get(2, 0) + cnt.get(1, 0) == 0 else 100.0 * cnt.get(1, 0) / (cnt.get(2, 0) + cnt.get(1, 0))
                plist.append(p)
                rstrlist.append("{name}: ok:{ok}, nok:{nok} ({p:5.1f}%)"
                                .format(name=name, ok=cnt.get(1, 0), nok=cnt.get(2, 0), p=p))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            cb = QtWidgets.QComboBox()
            cb.addItems(rstrlist)
            self.setCellWidget(row, 2, cb)
            # adding number of executions in column 1
            tableWidgetItem = QtWidgets.QTableWidgetItem(str(len(rstrlist)))
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)

            # use gradient to show progress between the last two sessions
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
            # adding hassolution in column 0
            tableWidgetItem = QtWidgets.QTableWidgetItem(str(hassolution))
            tableWidgetItem._data = item
            tableWidgetItem.setFlags(QtCore.Qt.ItemIsEnabled)
            tableWidgetItem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(row, 0, tableWidgetItem)
        self.setCurrentCell(0, 3, QtCore.QItemSelectionModel.Select)
        self.setFocus()

    def analyze(self, lesson):
        """Analyze lesson.

        Args:
            lessen (dict): lesson to analyze

        Returns:
            (result, hassolution)
                result (list) -> [(counter, sessionname (str)), ...]
                    counter (collections.Counter): counter for correct/wrong/notset items in session
                    sessionname: name of session
                hassolution (bool): flaf if key 'solution' is in lesseon
        """
        result = []
        for index, item in enumerate(lesson["config"]):
            if item["name"].startswith("Default"):
                searchindex = index
                break
        for session in lesson["sessionlist"]:
            if session["name"] == "new":
                logging.debug("section 'new' skipped")
                continue
            cnt = Counter()
            for item in [i for i in session["textlist"] if i["fontindex"] == searchindex]:
                cnt[item["state"]] += 1
            result.append((cnt, session['name']))
        hassolution = "solution" in lesson
        return result, hassolution

    def selectRandomLesson(self):
        countlist = []
        for row, item in enumerate(sorted(self.db.database.keys())):
            rlist, _ = self.analyze(self.db.database[item])
            countlist.append((len(rlist), row))
        countlist.sort(key=lambda k: k[0])
        print(countlist)
        numoflowest = [item[0] for item in countlist].count(countlist[0][0])
        print(numoflowest)
        selected = countlist[random.randint(0, numoflowest - 1)]
        print(selected)
        self.setCurrentCell(selected[1], 3, QtCore.QItemSelectionModel.SelectCurrent)


class TextWriter(QtWidgets.QMainWindow):
    """Main class putting all together."""

    def __init__(self, args):
        """Initialize main window."""
        super(TextWriter, self).__init__()
        icon = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAA3NCSVQICAjb4U/"\
               "gAAAACXBIWXMAAABvAAAAbwHxotxDAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2"\
               "NhcGUub3Jnm+48GgAAAD9QTFRF/////wAAzAAz1gAp2AAn97I/2QAm2AAn2AAn2"\
               "AAn/9pF2AAn9aU9/9pE2AAn9qk+2AAn2AAn2AAn9qo+/9pEMA0V1gAAABJ0Uk5T"\
               "AAMFHyGBjJCRrLrF5ujs+Pn6ryxQhQAAAFRJREFUGFdlj0cOgDAMBDe9d/7/VgJ"\
               "IUYLn5pFs7wITYUPOwQp8MNP6SzPsmbnrC8en0H1DA7LuokqoWMaiRAV/HXikUy"\
               "QqyAo5St6SYDQ6KferfwNgeQ3hV9pJPwAAAABJRU5ErkJggg=="
        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(QtCore.QByteArray.fromBase64(bytes(icon, encoding="ascii")), "PNG"):
            self.setWindowIcon(QtGui.QIcon(pixmap))
        self.db = DataHolder()
        self.writerWidget = ImageWriter(args, self.config2Qt(defaultconfig))
        self.writerWidget.imageLabel.sig_modified.connect(self.checkModifications)
        self.overviewWidget = OverView()
        self.overviewWidget.cellDoubleClicked.connect(self.lessonSelected)
        self.overviewWidget.cellActivated.connect(self.lessonSelected)
        self.mainView = QtWidgets.QTabWidget()
        self.mainView.addTab(self.overviewWidget, "Overview")
        self.mainView.addTab(self.writerWidget, "Writer")
        self.mainView.currentChanged.connect(self.tabChanged)
        self.setCentralWidget(self.mainView)
        self.resize(1250, 800)

        self.createActions()
        self.createMenus()

        self.db.modified = False
        self.setTitle()
        if args.filename:
            args.filename = os.path.abspath(args.filename)
            self.lastfolder = os.path.dirname(args.filename)
            self.open(None, args.filename)
        else:
            self.lastfolder = str(QtCore.QDir.currentPath())

    def createActions(self):
        """Create required actions."""
        self.openAct = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.saveAct = QtWidgets.QAction("&Save...", self, shortcut="Ctrl+S", triggered=self.save, enabled=False)
        self.exportAct = QtWidgets.QAction("&Export...", self, shortcut="Alt+E", triggered=self.export, enabled=False)
        self.printAct = QtWidgets.QAction("&Print...", self, shortcut="Ctrl+P", triggered=self.print_, enabled=False)
        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.compatibleAct = QtWidgets.QAction("Compatible Mode", self, checkable=True, toggled=self.compatible)
        self.randomLesson = QtWidgets.QAction("Random Lesson", self, enabled=False, triggered=self.overviewWidget.selectRandomLesson)
        self.recentFileActList = []
        for index in range(MAXRECENTFILES):
            self.recentFileActList.append(QtWidgets.QAction(triggered=self.openRecentFile))
            self.recentFileActList[-1].setVisible(False)

    def createMenus(self):
        """Create menus."""
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.exportAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()

        self.separatorAct = self.fileMenu.addSeparator()
        for index in range(MAXRECENTFILES):
            self.fileMenu.addAction(self.recentFileActList[index])
        self.fileMenu.addSeparator()

        self.fileMenu.addAction(self.compatibleAct)
        self.fileMenu.addAction(self.randomLesson)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.menuBar().addMenu(self.fileMenu)
        self.sessionMenu = QtWidgets.QMenu("Session")
        self.sessionMenu.setEnabled(False)
        self.menuBar().addMenu(self.sessionMenu)

        self.updateRecentFileActions()

    def updateSessions(self, select=None):
        """Update session menu.

        Args:
            select(int): index of selected session if any, else None

        The existing session menu is cleared and a new one
        for the current lesson is generated. If a session is selected
        it is checked in the menu.
        """
        logging.info("updateSessions")
        self.sessionMenu.clear()
        sessiongroup = QtWidgets.QActionGroup(self)
        pairs = [(index + 1, item["name"]) for index, item in enumerate(self.db.database[self.db.lessonName]["sessionlist"])]
        sessionnamelist = [(0, "new")] + sorted(pairs, key=lambda t: t[1], reverse=True)
        for index, name in sessionnamelist:
            action = QtWidgets.QAction(name, self, checkable=True, triggered=self.selectSession)
            if index == select:
                action.setChecked(True)
                self.db.sessionindex = index
                self.db.sessionname = name
            action.setData((index, name))
            sessiongroup.addAction(action)
            self.sessionMenu.addAction(action)
        self.sessionMenu.setEnabled(True)

    def lessonSelected(self, row, col):
        """Slot for double click at a table item.

        Args:
            row (int): row of double clicked item
            col (int): col of double clicked item

        Reads the config according to selected lesson, update session menu,
        sets title, initialize writer widget and enables some actions.
        """
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
        #
        if col == 1 and nncharts.have_modules:
            self.mainView.setCurrentIndex(2)
        else:
            self.mainView.setCurrentIndex(1)
            self.writerWidget.initialize()
            #
            self.exportAct.setEnabled(True)
            self.printAct.setEnabled(True)

    def config2Qt(self, config):
        """Deserializer for config

        Args:
            config (list): configuration list

        Converts font in color in config items to Qt objects.
        """
        for item in config:
            if isinstance(item["color"], QtGui.QColor):
                continue
            if isinstance(item["color"], str):
                item["color"] = int(item["color"], 0)
            color = QtGui.QColor()
            color.setRgb(item["color"])
            item["color"] = color
            font = QtGui.QFont()
            font.fromString(item['font'])
            item["font"] = font
        return config

    def config2String(self, config):
        """Serializer for config

        Args:
            config (list): configuration list

        Converts font in color in config from Qt objects to strings.
        """
        for item in config:
            item["font"] = str(item["font"].toString())
            item["color"] = item["color"].rgb()
        return config

    def selectSession(self):
        """Slot for actions in session menu."""
        index, name = self.sender().data()
        logging.info("selectSession index={index}, name={name}".format(name=name, index=index))
        if index == self.db.sessionindex:
            return
        if self.db.modified:
            self.askToSave()
        self.db.sessionindex = index
        self.db.sessionname = name
        self.writerWidget.initialize()
        self.db.modified = False
        self.setTitle()

    def open(self, _, fileName=None):
        """Open a json file."""
        if self.db.modified:
            self.askToSave()
        if fileName is None:
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", self.lastfolder, "*.jsondata")[0]
        if fileName:
            self.db.fileName = str(fileName)
            self.lastfolder = os.path.dirname(self.db.fileName)
            try:
                self.db.database = json.load(open(fileName))
            except Exception:
                QtWidgets.QMessageBox.critical(self, "Error opening file", traceback.format_exc())
                return
            self.overviewWidget.populateTable(sort=True)
            self.writerWidget.reset()
            self.mainView.setCurrentIndex(0)
            self.sessionMenu.setEnabled(False)
            self.randomLesson.setEnabled(True)
            if hasattr(self.db, "lessonName"):
                del self.db.lessonName
            if hasattr(self.db, "sessionindex"):
                del self.db.sessionindex
            self.setTitle()

            settings = QtCore.QSettings()
            filelist = settings.value("recentFileList", [])
            if fileName in filelist:
                filelist.remove(fileName)
            filelist.insert(0, fileName)
            del filelist[MAXRECENTFILES:]
            settings.setValue("recentFileList", filelist)
            self.updateRecentFileActions()

    def openRecentFile(self):
        logging.debug("openRecentFile")
        self.open(None, self.sender().data())

    def updateRecentFileActions(self):
        logging.debug("updateRecentFileActions")
        settings = QtCore.QSettings()
        filelist = settings.value("recentFileList", [])
        logging.debug(filelist)
        numRecentFiles = min(len(filelist), MAXRECENTFILES)
        for index in range(MAXRECENTFILES):
            self.recentFileActList[index].setVisible(False)
        for index in range(numRecentFiles):
            self.recentFileActList[index].setText(os.path.basename(filelist[index]))
            self.recentFileActList[index].setData(filelist[index])
            self.recentFileActList[index].setVisible(True)
        self.separatorAct.setVisible(numRecentFiles > 0)

    def save(self):
        """Save database to json file and update status."""
        logging.info("save: {0}, {1}, {2}, {3}".format(self.db.lessonName, self.db.sessionindex, self.db.sessionname, self.db.modified))
        if self.db.sessionindex == 0:
            # new session, a new name is needed
            self.db.sessionname = self._getnewname()
            self.db.database[self.db.lessonName]["sessionlist"].append({"name": self.db.sessionname, "textlist": []})
            self.db.sessionindex = len(self.db.database[self.db.lessonName]["sessionlist"])
            self.updateSessions(self.db.sessionindex)
        # copy the data from scene into database
        self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"] = []
        for itemgroup in self.writerWidget.imageLabel.scene().items():
            if not isinstance(itemgroup, QtWidgets.QGraphicsItemGroup):
                continue
            textitem, decoitem = self.writerWidget.imageLabel.extractItems(itemgroup)
            pos = textitem.mapToScene(textitem.pos())
            # save with modified position to ensure compatibility
            bbox = textitem.boundingRect()
            pos.setY(pos.y() + (bbox.bottom() - bbox.top()))
            #
            self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"].append({
                "x": pos.x(),
                "y": pos.y(),
                "text": textitem.text(),
                "fontindex": textitem.data(1),
                "state": textitem.data(0)
            })
        # prepare config
        logging.debug(self.db.database[self.db.lessonName]["sessionlist"][self.db.sessionindex - 1]["textlist"])
        self.db.database[self.db.lessonName]["config"] = self.config2String(self.db.database[self.db.lessonName]["config"])
        # save database
        try:
            data = json.dumps(self.db.database, indent=4)
            with open(self.db.fileName, "w") as fh:
                fh.write(data)
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Error saving to file", traceback.format_exc())
        finally:
            self.db.database[self.db.lessonName]["config"] = self.config2Qt(self.db.database[self.db.lessonName]["config"])
        self.overviewWidget.populateTable()
        self.db.modified = False
        self.setTitle()

    def _getnewname(self):
        """Get a new session name.

        Returns
            (str) the name for the new session.
        """
        sessionlist = [item["name"] for item in self.db.database[self.db.lessonName]["sessionlist"]]
        for index in range(1, 0xFFF):
            sessionname = "{}-{}".format(datetime.datetime.now().strftime("%Y-%m-%d"), index)
            if sessionname not in sessionlist:
                break
        return sessionname

    def askToSave(self):
        """Queries if to save modifications."""
        if QtWidgets.QMessageBox.question(self, "Save Changes?", "File is modified. Save changes?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            self.save()
        self.db.modified = False

    def checkModifications(self):
        """Slot called when scene is modified.

        Updates status accordingly.
        """
        logging.debug("checkModifications")
        self.db.modified = True
        self.saveAct.setEnabled(True)
        if self.db.modified and not str(self.windowTitle()).startswith('*'):
            self.setWindowTitle('*' + self.windowTitle())
        if not self.db.modified and str(self.windowTitle()).startswith('*'):
            self.setWindowTitle(str(self.windowTitle())[1:])

    def closeEvent(self, event):
        """Ask to save if stgh. is modified on closing."""
        if self.db.modified:
            self.askToSave()
        super(TextWriter, self).closeEvent(event)

    def setTitle(self):
        """Set the window title from available fileName, lessonName, sessionname."""
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
        """Slot for export menu item."""
        logging.debug("export")
        fileName = "{0}_{1}_{2}.png".format(os.path.splitext(os.path.basename(self.db.fileName))[0], self.db.lessonName, self.db.sessionname)
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Export File", fileName, "*.png")[0]
        if not fileName:
            return
        self.writerWidget.imageLabel.export(fileName)

    def print_(self):
        """Slot for print menu item."""
        printer = QtPrintSupport.QPrinter()
        fileName = "{0}_{1}_{2}.pdf".format(os.path.splitext(os.path.basename(self.db.fileName))[0], self.db.lessonName, self.db.sessionname)
        fileName = os.path.join(os.getcwd(), fileName)
        # !printer.setOutputFileName(fileName)
        dlg = QtPrintSupport.QPrintDialog(printer)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.writerWidget.imageLabel.print_(dlg.printer())

    def compatible(self, checked):
        self.writerWidget.imageLabel.compatibleMode = checked

    def tabChanged(self, index):
        """Slot called if tab of mainView is changed."""
        if index == 1:
            self.writerWidget.imageLabel.setFocus()


if __name__ == '__main__':
    LOGDICT = {"info": logging.INFO, "critical": logging.CRITICAL, "debug": logging.DEBUG}
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", default=None, nargs='?')
    parser.add_argument("--log", choices=LOGDICT.keys(), default="critical", help="log level, default '%(default)s'")
    args = parser.parse_args()
    logging.basicConfig(level=LOGDICT[args.log],
                        format='%(levelname)s:%(lineno)d:%(message)s')
    textwriter = TextWriter(args)
    #nncharts.init(textwriter)
    textwriter.show()
    sys.exit(app.exec_())

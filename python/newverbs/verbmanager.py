import argparse
import pathlib
import json
import sys
from PySide2 import QtWidgets, QtCore


PROGNAME = "verbmanager"


class Common():
    def __init__(self, inputfile):
        with inputfile.open("r") as fh:
            self.json_db = json.load(fh)
        # print(self.json_db[0].keys())

    def save(self):
        pass


class NormalVerbs(Common):
    # keys are 'id', 'german', 'english', 'infinitivo', 'priority', 'gerundio', 'gerundioreflexiv', 'participio',
    # 'anterior', 'condicional', 'condicionalperfecto', 'futuro', 'futuroperfecto', 'imperativoafirmativo', 'imperativoafirmativoreflexiv',
    # 'imperativonegativo', 'imperfecto', 'indefinido', 'perfecto', 'pluscuamperfecto', 'presente', 'subjuntivofuturo', 'subjuntivofuturoperfecto',
    # 'subjuntivoimperfecto', 'subjuntivoperfecto', 'subjuntivopluscuamperfecto', 'subjuntivopresente', '_export']
    def __init__(self, inputfile):
        super().__init__(inputfile)
        self.display_keys = ["infinitivo", "german"]

    def export(self, item):
        pass

    def get_export_flag(self, verbitem):
        return any(item == 2 for item in verbitem["_export"].values())


class ReflexiveVerbs(Common):
    # keys are '_complete', '_export', 'spain', 'infinitivo', 'german',
    # 'Indicativo Presente', 'Indicativo Futuro', 'Indicativo Pretérito imperfecto', 'Indicativo Pretérito perfecto compuesto',
    # 'Indicativo Pretérito pluscuamperfecto', 'Indicativo Pretérito anterior', 'Indicativo Futuro perfecto', 'Indicativo Condicional perfecto',
    # 'Indicativo Condicional', 'Indicativo Pretérito indefinido', 'Imperativo', 'Subjuntivo Presente', 'Subjuntivo Futuro',
    # 'Subjuntivo Pretérito imperfecto', 'Subjuntivo Pretérito pluscuamperfecto', 'Subjuntivo Futuro perfecto', 'Subjuntivo Pretérito imperfecto (2)',
    # 'Subjuntivo Pretérito pluscuamperfecto (2)', 'Subjuntivo Pretérito perfecto', 'Gerundio', 'Gerundio compuesto', 'Infinitivo', 'Infinitivo compuesto',
    # 'Participio Pasado'])
    def __init__(self, inputfile):
        super().__init__(inputfile)
        self.display_keys = ["spain", "german"]

    def export(self, item):
        pass

    def get_export_flag(self, verbitem):
        return verbitem["_export"] == 2


ALLOWED_INPUT_DICT = {
    pathlib.Path(__file__).parent.joinpath("normale_verben.json").resolve(): NormalVerbs,
    pathlib.Path(__file__).parent.joinpath("reflexive_verben.json").resolve(): ReflexiveVerbs
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, inputfile=None):
        super().__init__()
        self.setWindowTitle(PROGNAME)
        self.setMinimumSize(640, 480)
        self.action_open = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openFile, enabled=True)
        self.action_save = QtWidgets.QAction("&Export and save...", self, shortcut="Ctrl+S", triggered=self.save, enabled=False)
        self.action_export = QtWidgets.QAction("&Export only...", self, shortcut="Ctrl+Alt+S", triggered=self.export, enabled=False)
        self.action_exit = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.action_mark = QtWidgets.QAction("&Mark", self, shortcut="Ctrl+M", triggered=self.mark, enabled=False)
        self.action_unmark = QtWidgets.QAction("&Unmark", self, shortcut="Ctrl+U", triggered=self.unmark, enabled=False)
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.action_open)
        self.fileMenu.addAction(self.action_mark)
        self.fileMenu.addAction(self.action_unmark)
        self.fileMenu.addAction(self.action_save)
        self.fileMenu.addAction(self.action_export)
        self.fileMenu.addAction(self.action_exit)
        self.menuBar().addMenu(self.fileMenu)
        #
        self.table_widget = QtWidgets.QTableWidget()
        #
        self.setCentralWidget(self.table_widget)
        # self.setWindowState(QtCore.Qt.WindowMaximized)
        #
        self.openFile(inputfile)

    def openFile(self, inputfile=None):
        if inputfile is None:
            inputfile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", str(pathlib.Path(__file__).parent), "JSON (*.json)")
            if len(inputfile) == 0:
                return
        path = pathlib.Path(inputfile).resolve()
        if path not in ALLOWED_INPUT_DICT:
            QtWidgets.QMessageBox.critical(self, "File not supported", "Allowed input files are {}".format(", ".join(str(item) for item in ALLOWED_INPUT_DICT)))
            return
        self.verbsFactory = ALLOWED_INPUT_DICT[path](path)
        self.setWindowTitle(f"{PROGNAME} - {str(path.name)}")
        [action.setEnabled(True) for action in (self.action_mark, self.action_unmark, self.action_save, self.action_export)]
        self.populateTable()

    def populateTable(self):
        self.table_widget.setRowCount(len(self.verbsFactory.json_db))
        self.table_widget.setColumnCount(2)
        for row, verbitem in enumerate(self.verbsFactory.json_db):
            for col in [0, 1]:
                widget = QtWidgets.QTableWidgetItem(verbitem[self.verbsFactory.display_keys[col]])
                if col == 0:
                    if not self.verbsFactory.get_export_flag(verbitem):
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                        widget.setCheckState(QtCore.Qt.Unchecked)
                    else:
                        widget.setFlags(QtCore.Qt.ItemIsUserCheckable)
                        widget.setCheckState(QtCore.Qt.Checked)
                self.table_widget.setItem(row, col, widget)

    def save(self):
        pass

    def export(self):
        pass

    def mark(self):
        pass

    def unmark(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", nargs="?", help="JSON input file")
    args = parser.parse_args()
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    mainwin = MainWindow(args.inputfile)
    mainwin.show()
    sys.exit(app.exec_())


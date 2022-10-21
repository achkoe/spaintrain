import argparse
import pathlib
import json
import random
import gzip
import sys
from PySide2 import QtWidgets, QtCore


PROGNAME = "verbmanager"


class Common():
    def __init__(self, inputfile):
        self.inputfile = inputfile
        with gzip.open(str(inputfile), "rt") as fh:
            self.json_db = json.load(fh)

    def save(self):
        with gzip.open(str(self.inputfile), "wt") as fh:
            json.dump(self.json_db, fh, indent=4, ensure_ascii=False)

    def searchItem(self, key: str, value: str):
        for index, item in enumerate(self.json_db):
            if item[key] == value:
                break
        else:
            index = None
        return index


class NormalVerbs(Common):
    # keys are 'id', 'german', 'english', 'infinitivo', 'priority', 'gerundio', 'gerundioreflexiv', 'participio',
    # 'anterior', 'condicional', 'condicionalperfecto', 'futuro', 'futuroperfecto', 'imperativoafirmativo', 'imperativoafirmativoreflexiv',
    # 'imperativonegativo', 'imperfecto', 'indefinido', 'perfecto', 'pluscuamperfecto', 'presente', 'subjuntivofuturo', 'subjuntivofuturoperfecto',
    # 'subjuntivoimperfecto', 'subjuntivoperfecto', 'subjuntivopluscuamperfecto', 'subjuntivopresente', '_export']
    def __init__(self, inputfile):
        super().__init__(inputfile)
        self.display_keys = ["infinitivo", "german"]
        self.replacement_dict = {
            'anterior': 'Pretérito anterior',
            'subjuntivoimperfecto': 'Subjuntivo Imperfecto',
            'imperativoafirmativo': 'Imperativo afirmativo',
            'imperativonegativo': 'Imperativo negativo',
            'A_infinitivo': 'Infinitivo',
            'gerundio': 'Gerundio',
            'indefinido': 'Pretérito indefinido',
            'subjuntivofuturo': 'Subjuntivo Futuro',
            'subjuntivoperfecto': 'Subjuntivo Perfecto',
            'participio': 'Participio',
            'subjuntivopluscuamperfecto': 'Subjuntivo Pluscuamperfecto',
            'futuroperfecto': 'Futuro perfecto',
            'condicionalperfecto': 'Condicional perfecto',
            'imperativoafirmativoreflexiv': 'Imperativo afirmativo reflexivo',
            'imperfecto': 'Pretérito imperfecto',
            'condicional': 'Condicional',
            'pluscuamperfecto': 'Pretérito pluscuamperfecto',
            'gerundioreflexiv': 'Gerundio reflexivo',
            'perfecto': 'Pretérito perfecto compuesto',
            'subjuntivopresente': 'Subjuntivo Presente',
            'presente': 'Presente',
            'A_english': 'Ingles',
            'subjuntivofuturoperfecto': 'Subjuntivo Futuro Perfecto',
            'A_german': 'Aleman',
            'futuro': 'Futuro',
        }
        self.pronomen_list = [
            "yo", "tú", "él/ella/usted", "nosotros/-as", "vosotros/-as", "ellos/ellas/ustedes"
        ]
        self.export_list = ["subjuntivoimperfecto", "imperativoafirmativo", "indefinido", "imperfecto",
            "condicional", "subjuntivopresente", "presente", "futuro", "participio", "gerundio"]

    def export(self):
        """Export all items where _export == 1 and set _export = 2
        """
        linebreak = "<br/>"
        rlist = []
        for index, item in enumerate(self.json_db):
            if self.get_export_flag(item, 1):
                self.set_export_flag(index, 2)
            else:
                continue
            for key in ["gerundio", "participio"]:
                question = "<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                    german=item["german"],
                    linebreak=linebreak,
                    tense=self.replacement_dict[key])
                rlist.append([question, "{}{}{}".format(item["infinitivo"], linebreak, item[key])])
            for key in ["imperativoafirmativo", "indefinido", "imperfecto", "condicional", "subjuntivopresente", "presente", "futuro"]:
                question = '<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="{color}">{tense}</font></u></b>?'.format(
                    german=item["german"],
                    linebreak=linebreak,
                    tense=self.replacement_dict[key],
                    color="#000000")
                tlist = [item["infinitivo"], ""]
                for pronomen, subkey in zip(self.pronomen_list, item[key]):
                    if item[key][subkey] is None:
                        continue
                    tlist.append("{} {}".format(pronomen, item[key][subkey]))
                rlist.append([question, linebreak.join(tlist)])
            for key in ["subjuntivoimperfecto"]:
                question = '<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="{color}">{tense}</font></u></b>?'.format(
                    german=item["german"],
                    linebreak=linebreak,
                    tense=self.replacement_dict[key],
                    color="#ef2929")
                tlist = [item["infinitivo"], ""]
                for pronomen, subkey in zip(self.pronomen_list, item[key]):
                    tlist.append("{} {}".format(pronomen, item[key][subkey]))
                tlist.append("")
                for pronomen, subkey, repl in zip(self.pronomen_list, item[key], ["se", "ses", "se", "semos", "seis", "sen"]):
                    conjugation = item[key][subkey]
                    tlist.append("{} {}{}".format(pronomen, item[key][subkey][:-len(repl)], repl))
                rlist.append([question, linebreak.join(tlist)])
        random.shuffle(rlist)
        ostr = "\n".join(u"{}|{}|{}".format(ritem[0], ritem[1], "Verb") for ritem in rlist)
        with self.inputfile.with_name(f"{self.inputfile.stem}_out.txt").open("w") as fh:
            fh.write(ostr)
        return fh.name

    def get_export_flag(self, verbitem, value=2):
        return any(item == value for item in verbitem["_export"].values())

    def set_export_flag(self, index: int, value=1):
        for key in self.export_list:
            self.json_db[index]["_export"][key] = value

    def searchItem(self, searchkey):
        return super().searchItem("infinitivo", searchkey)


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
        self.inputfile = inputfile
        self.display_keys = ["spain", "german"]
        self.replacement_dict = {
            'infinitiv': None,
            'german': None,
            '_complete': None,
            'Indicativo Presente': 'Presente',
            'Indicativo Futuro': 'Futuro',
            'Indicativo Pretérito imperfecto': 'Pretérito imperfecto',
            'Indicativo Pretérito perfecto compuesto': None,
            'Indicativo Pretérito pluscuamperfecto': None,
            'Indicativo Pretérito anterior': None,
            'Indicativo Futuro perfecto': None,
            'Indicativo Condicional perfecto': None,
            'Indicativo Condicional': 'Condicional',
            'Indicativo Pretérito indefinido': 'Pretérito indefinido',
            'Imperativo': 'Imperativo',
            'Subjuntivo Presente': 'Subjuntivo Presente',
            'Subjuntivo Futuro': None,
            'Subjuntivo Pretérito imperfecto': 'Subjuntivo Pretérito imperfecto',
            'Subjuntivo Pretérito pluscuamperfecto': None,
            'Subjuntivo Futuro perfecto': None,
            'Subjuntivo Pretérito imperfecto (2)': 'Subjuntivo Pretérito imperfecto (2)',
            'Subjuntivo Pretérito pluscuamperfecto (2)': None,
            'Subjuntivo Pretérito perfecto': None,
            'Gerundio': 'Gerundio ',
            'Gerundio compuesto': None,
            'Infinitivo': None,
            'Infinitivo compuesto ': None,
            'Participio Pasado': 'Participio',
        }

    def export(self):
        linebreak = "<br/>"
        rlist = []
        for index, item in enumerate(self.json_db):
            if self.get_export_flag(item, 1):
                self.set_export_flag(index, 2)
            else:
                continue
            for tense in self.replacement_dict.keys():
                if self.replacement_dict[tense] is None:
                    continue
                try:
                    if item["german"].endswith("RV"):
                        typefield = "Verb (reziprok)"
                        item_german = item["german"][:-2].strip()
                    elif item["german"].endswith("PV"):
                        typefield = "Verb (nur reflexive)"
                        item_german = item["german"][:-2].strip()
                    else:
                        typefield = "Verb"
                        item_german = item["german"]
                    if tense in ["Participio Pasado", "Gerundio"]:
                        question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                            german=item_german,
                            linebreak=linebreak,
                            tense=self.replacement_dict[tense])
                        rlist.append([question, "{}{}{}".format(item["spain"], linebreak, linebreak.join(item[tense])), typefield])
                    elif tense in ['Subjuntivo Pretérito imperfecto']:
                        question = u'<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="#ef2929">{tense}</font></u></b>?'.format(
                            german=item_german,
                            linebreak=linebreak,
                            tense=self.replacement_dict[tense])
                        item[tense].insert(0, item["spain"])
                        rlist.append([question, "{0}{1}{1}{2}".format(linebreak.join(item[tense]), linebreak, linebreak.join(item['Subjuntivo Pretérito imperfecto (2)'])), typefield])
                    elif tense in ['Subjuntivo Pretérito imperfecto (2)']:
                        pass
                    else:
                        question = u'<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="#000">{tense}</font></u></b>?'.format(
                            german=item_german,
                            linebreak=linebreak,
                            tense=self.replacement_dict[tense])
                        item[tense].insert(0, item["spain"])
                        rlist.append([question, linebreak.join(item[tense]), typefield])
                except Exception:
                    print(item)
                    raise
        random.shuffle(rlist)
        ostr = "\n".join("{}|{}|{}".format(ritem[0], ritem[1], ritem[2]) for ritem in rlist)
        with self.inputfile.with_name(f"{self.inputfile.stem}_out.txt").open("w") as fh:
            fh.write(ostr)
        return fh.name

    def get_export_flag(self, verbitem, value=2):
        return verbitem["_export"] == value

    def set_export_flag(self, index: int, value=1):
        self.json_db[index]["_export"] = value

    def searchItem(self, searchkey):
        return super().searchItem("spain", searchkey)


ALLOWED_INPUT_DICT = {
    pathlib.Path(__file__).parent.joinpath("normale_verben.json.gz").resolve(): NormalVerbs,
    pathlib.Path(__file__).parent.joinpath("reflexive_verben.json.gz").resolve(): ReflexiveVerbs
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, inputfile=None):
        super().__init__()
        self.setWindowTitle(PROGNAME)
        self.setMinimumSize(640, 480)
        settings = QtCore.QSettings()
        #
        self.table_widget = QtWidgets.QTableWidget()

        settings.beginGroup("MainWindow");
        self.resize(settings.value("size", QtCore.QSize(640, 480)))
        self.move(settings.value("pos", QtCore.QPoint(200, 200)))
        self.table_widget.horizontalHeader().restoreState(settings.value("twhh"))
        settings.endGroup();

        self.action_open = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openFile, enabled=True)
        self.action_save = QtWidgets.QAction("&Export and save...", self, shortcut="Ctrl+S", triggered=self.exportAndSave, enabled=False)
        self.action_export = QtWidgets.QAction("&Export only...", self, shortcut="Ctrl+Alt+S", triggered=self.exportOnly, enabled=False)
        self.action_exit = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.action_open)
        self.fileMenu.addAction(self.action_save)
        self.fileMenu.addAction(self.action_export)
        self.fileMenu.addAction(self.action_exit)
        self.menuBar().addMenu(self.fileMenu)
        #
        self.setCentralWidget(self.table_widget)
        # self.setWindowState(QtCore.Qt.WindowMaximized)
        #
        self.openFile(inputfile)

    def openFile(self, inputfile=None):
        if inputfile is None:
            inputfile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", str(pathlib.Path(__file__).parent), "Files (*.json.gz)")
            if len(inputfile) == 0:
                return
        path = pathlib.Path(inputfile).resolve()
        if path not in ALLOWED_INPUT_DICT:
            QtWidgets.QMessageBox.critical(self, "File not supported", "Allowed input files are {}".format(", ".join(str(item) for item in ALLOWED_INPUT_DICT)))
            return
        self.verbsFactory = ALLOWED_INPUT_DICT[path](path)
        self.setWindowTitle(f"{PROGNAME} - {str(path.name)}")
        [action.setEnabled(True) for action in (self.action_save, self.action_export)]
        self.populateTable()

    def populateTable(self):
        self.table_widget.setRowCount(len(self.verbsFactory.json_db))
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(self.verbsFactory.display_keys)
        self.table_widget.horizontalHeader().setStretchLastSection(True)

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

    def exportAndSave(self):
        self.exportOnly()
        self.verbsFactory.save()

    def exportOnly(self):
        for row in range(self.table_widget.rowCount()):
            widget = self.table_widget.item(row, 0)
            if not widget or int(widget.flags()) & QtCore.Qt.ItemIsEnabled == 0 or widget.checkState() == 0:
                continue
            self.verbsFactory.set_export_flag(self.verbsFactory.searchItem(widget.text()))
        name = self.verbsFactory.export()
        self.statusBar().showMessage(f"exported to file {name}")

    def closeEvent(self, event):
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow");
        settings.setValue("size", self.size());
        settings.setValue("pos", self.pos());
        settings.setValue("twhh", self.table_widget.horizontalHeader().saveState())
        settings.endGroup();
        event.accept()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", nargs="?", help="JSON input file")
    args = parser.parse_args()
    QtCore.QCoreApplication.setOrganizationName("achimk")
    QtCore.QCoreApplication.setApplicationName(PROGNAME)
    app = QtWidgets.QApplication([sys.argv[0]] + ["-style", "Fusion"] + sys.argv[1:])
    mainwin = MainWindow(args.inputfile)
    mainwin.show()
    sys.exit(app.exec_())

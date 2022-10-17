import argparse
import pathlib
import json


class Common():
    def __init__(self, inputfile):
        with path.open("r") as fh:
            self.json_db = json.load(fh)
        # print(self.json_db[0].keys())

    def save(self):
        pass


class NormalVerbs(Common):
    # keys are 'id', 'german', 'english', 'infinitivo', 'priority', 'gerundio', 'gerundioreflexiv', 'participio',
    # 'anterior', 'condicional', 'condicionalperfecto', 'futuro', 'futuroperfecto', 'imperativoafirmativo', 'imperativoafirmativoreflexiv',
    # 'imperativonegativo', 'imperfecto', 'indefinido', 'perfecto', 'pluscuamperfecto', 'presente', 'subjuntivofuturo', 'subjuntivofuturoperfecto',
    # 'subjuntivoimperfecto', 'subjuntivoperfecto', 'subjuntivopluscuamperfecto', 'subjuntivopresente', '_export']
    def __init__(self):
        super().__init__()
        self.display_keys = ["infinitivo", "german"]

    def export(self, item):
        pass


class ReflexiveVerbs(Common):
    # keys are '_complete', '_export', 'spain', 'infinitivo', 'german',
    # 'Indicativo Presente', 'Indicativo Futuro', 'Indicativo Pretérito imperfecto', 'Indicativo Pretérito perfecto compuesto',
    # 'Indicativo Pretérito pluscuamperfecto', 'Indicativo Pretérito anterior', 'Indicativo Futuro perfecto', 'Indicativo Condicional perfecto',
    # 'Indicativo Condicional', 'Indicativo Pretérito indefinido', 'Imperativo', 'Subjuntivo Presente', 'Subjuntivo Futuro',
    # 'Subjuntivo Pretérito imperfecto', 'Subjuntivo Pretérito pluscuamperfecto', 'Subjuntivo Futuro perfecto', 'Subjuntivo Pretérito imperfecto (2)',
    # 'Subjuntivo Pretérito pluscuamperfecto (2)', 'Subjuntivo Pretérito perfecto', 'Gerundio', 'Gerundio compuesto', 'Infinitivo', 'Infinitivo compuesto',
    # 'Participio Pasado'])
    def __init__(self):
        super().__init__()
        self.display_keys = ["spain", "german"]

    def export(self, item):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="JSON input file")
    args = parser.parse_args()
    allowed_input_dict = {
        pathlib.Path(__file__).parent.joinpath("normale_verben.json").resolve(): NormalVerbs,
        pathlib.Path(__file__).parent.joinpath("reflexive_verben.json").resolve(): ReflexiveVerbs
    }
    path = pathlib.Path(args.inputfile).resolve()
    if path not in allowed_input_dict:
        parser.print_usage()
        parser.exit(1, "allowed input files are {}".format(", ".join(str(item) for item in allowed_input_dict)))
    verbs = allowed_input_dict[path](args.inputfile)


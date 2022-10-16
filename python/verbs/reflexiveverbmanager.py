import argparse
import pathlib
import json
import random


inputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.out.json")
inputcopyfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.out.copy.json")
outputfile = pathlib.Path(__file__).parent.joinpath("reflexiveverbmanager.out.txt")
selectionfile = pathlib.Path(__file__).parent.joinpath("reflexiveverbmanager.select.json")

replacementdict = {
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


def write_select():
    """write all items with '_complete==1' and 'export==0, 2' to selectionfile"""
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    odata = dict()
    for item in data:
        if item["_complete"] == 1 and item["_export"] in [0, 2]:
            odata.update({item["spain"]: item["_export"]})
    odata = {k: v for k, v in sorted(odata.items(), key=lambda item: item[1])}
    with selectionfile.open("w") as fh:
        json.dump(odata, fh, indent=4, ensure_ascii=False)
    print(f"selection file written to {selectionfile}")


def read_select():
    """transfer settings from selectionfile to inputfile"""
    with selectionfile.open("r") as fh:
        sdata = json.load(fh)
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    for item in data:
        if item["spain"] in sdata and item["_export"] != sdata[item["spain"]]:
            print(item["spain"])
            item["_export"] = sdata[item["spain"]]
    with open(inputcopyfile, "w") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)
    print(f"updated inputfile written to {inputcopyfile}")


def export():
    linebreak = "<br/>"
    rlist = []
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    for item in data:
        if item["_complete"] == 0:
            continue
        # _export 0: not exported
        # _export 1: do export
        # _export 2: already exported
        if item["_export"] in [0, 2]:
            continue
        item["_export"] == 2
        for tense in replacementdict.keys():
            if replacementdict[tense] is None:
                continue
            try:
                if item["german"].endswith("RV"):
                    typefield = "Verb (reziprok)"
                    item["german"] = item["german"][:-2].strip()
                elif item["german"].endswith("PV"):
                    typefield = "Verb (nur reflexive)"
                    item["german"] = item["german"][:-2].strip()
                else:
                    typefield = "Verb"
                if tense in ["Participio Pasado", "Gerundio"]:
                    question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                        german=item["german"],
                        linebreak=linebreak,
                        tense=replacementdict[tense])
                    rlist.append([question, "{}{}{}".format(item["spain"], linebreak, linebreak.join(item[tense])), typefield])
                elif tense in ['Subjuntivo Pretérito imperfecto']:
                    question = u'<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="#ef2929">{tense}</font></u></b>?'.format(
                        german=item["german"],
                        linebreak=linebreak,
                        tense=replacementdict[tense])
                    item[tense].insert(0, item["spain"])
                    rlist.append([question, "{0}{1}{1}{2}".format(linebreak.join(item[tense]), linebreak, linebreak.join(item['Subjuntivo Pretérito imperfecto (2)'])), typefield])
                elif tense in ['Subjuntivo Pretérito imperfecto (2)']:
                    pass
                else:
                    question = u'<b>{german}</b>{linebreak}Konjugation des Verbs im <b><u><font color="#000">{tense}</font></u></b>?'.format(
                        german=item["german"],
                        linebreak=linebreak,
                        tense=replacementdict[tense])
                    item[tense].insert(0, item["spain"])
                    rlist.append([question, linebreak.join(item[tense]), typefield])
            except Exception:
                print(item)
                raise
        random.shuffle(rlist)
    ostr = "\n".join("{}|{}|{}".format(ritem[0], ritem[1], ritem[2]) for ritem in rlist)
    with open(outputfile, "w", encoding="utf-8") as fh:
        fh.write(ostr)
    print(f"Written to file {outputfile}")
    with open(inputcopyfile, "w") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)
    print(f"updated inputfile written to {inputcopyfile}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--export", action="store_true", help=f"export items with '_complete==1' and 'export==1' to {outputfile}")
    group.add_argument("-w", "--write-select", action="store_true", help=f"write all items with '_complete==1' and 'export==0, 2' to {selectionfile}")
    group.add_argument("-r", "--read-select", action="store_true", help=f"transfer settings from {selectionfile} to {inputfile}")
    args = parser.parse_args()
    if args.export:
        export()
    elif args.write_select:
        write_select()
    elif args.read_select:
        read_select()
    else:
        print("What should I do?")

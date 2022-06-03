import pathlib
import json
import random


inputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.out.json")
outputfile = pathlib.Path(__file__).parent.joinpath("reflexiveverbmanager.out.txt")

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
    'Indicativo Pretérito perfecto simple': 'Pretérito perfecto',
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


def main():
    linebreak = "<br/>"
    rlist = []
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    for item in data:
        if item["_complete"] == 0:
            continue
        for tense in replacementdict.keys():
            if replacementdict[tense] is None:
                continue
            try:
                if item["german"].endswith("RV"):
                    typefield = "Verb (reziprok)"
                    item["german"] = item["german"][:-2].strip()
                elif item["german"].endswith("PV"):
                    typefield = "Verb (pronominale)"
                    item["german"] = item["german"][:-2].strip()
                else:
                    typefield = "Verb"
                if tense in ["Participio Pasado", "Gerundio"]:
                    question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                        german=item["german"],
                        linebreak=linebreak,
                        tense=replacementdict[tense])
                    rlist.append([question, "{}{}{}".format(item["spain"], linebreak, item[tense]), typefield])
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



if __name__ == '__main__':
    main()

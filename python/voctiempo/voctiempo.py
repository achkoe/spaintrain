
# -*- coding: utf-8 -*-

import random
import codecs
from collections import OrderedDict

filename = "voctrain.txt"
resultname = "voctrain.json"

exclude_tiempolist = [u"Pretérito perfecto compuesto", u"Pretérito pluscuamperfecto",
                      u"Pretérito anterior", u"Futuro perfecto", u"Condicional perfecto",
                      u"Infinitivo compuesto", u"Gerundio compuesto",
                      u"Subjuntivo Pretérito imperfecto",
                      u"Subjuntivo Pretérito imperfecto (2)", u"Subjuntivo Futuro",
                      u"Subjuntivo Pretérito perfecto", u"Subjuntivo Pretérito pluscuamperfecto",
                      u"Subjuntivo Pretérito pluscuamperfecto (2)", u"Subjuntivo Futuro perfecto"]

export_tempus = {
    u"Subjuntivo Presente": (True, 6),
    u'Presente': (False, 6),
    u'Pretérito imperfecto': (False, 6),
    u'Pretérito perfecto simple': (False, 6),
    u'Participio pasado': (False, 1),
    u'Gerundio': (False, 1),
    u'Futuro': (False, 6),
    u'Condicional': (False, 6),
    u'Imperativo': (False, 5),
    u'Infinitivo': (False, 1),
}

replacement = {u"Participio pasado": u"Participio", u"Pretérito perfecto simple": u"Pretérito indefinido"}


def read_vocdata(filename):
    """Return list of dict objects.
    """
    rlist = []
    with codecs.open(filename, 'r', encoding="utf-8") as fh:
        buf = fh.read().splitlines()
        rdict = OrderedDict()
        for line in buf:
            if len(line.strip()) == 0:
                if len(rdict) > 0:
                    rlist.append(rdict)
                    rdict = OrderedDict()
            else:
                left, right = line.split(':')
                left = left.strip()
                if left not in exclude_tiempolist:
                    rdict[left] = [item.strip() for item in right.split(',')]
        if len(rdict) > 0:
            rlist.append(rdict)
        return rlist


def get_question(rlist, qdict):
    personlist = [u"1. Person Singular (yo)", u"2. Person Singular (tú)", u"3. Person Singular (el/ella/usted)",
                  u"1. Person Plural (nosotros)",
                  u"2. Person Plural (vosotros)", u"3. Person Plural (ellos/ellas/ustedes)"]
    if qdict["tempus"] == u"Imperativo":
        personofs = 1
    else:
        personofs = 0
    rdict = rlist[qdict["listindex"]]
    try:
        ldict = {
            "word": rdict[u"Infinitivo"][0],
            "word": ', '.join(rdict[u'Alem\xe1n']),
            "person": personlist[qdict["person"] + personofs],
            "tempus": replacement.get(qdict["tempus"], qdict["tempus"])
        }
    except:
        print qdict
        print rdict
        raise
    if len(rdict[qdict["tempus"]]) == 1:
        fmt = u"<b>{word}</b><br/>Wie lautet das <u>{tempus}</u>?"
    else:
        fmt = u"<b>{word}</b><br/><small>im</small><br/><u>{tempus}</u><br/><small>in der</small><br/><u>{person}</u>?"
    try:
        question = fmt.format(**ldict)
        answer = rdict[qdict["tempus"]][qdict["person"]]
    except:
        print qdict
        question = "Problem occured"
        answer = "see console"
    return question, answer


def export_single_person(rlist, rfile):
    """Single person per export item."""
    elist = []
    for index, rdict in enumerate(rlist):
        for tempus in export_tempus:
            if not export_tempus[tempus][0]:
                continue
            for person in range(len(rdict[tempus])):
                qdict = {"listindex": index, "tempus": tempus, "person": person}
                pair = get_question(rlist, qdict)
                elist.append(u"{}&{}".format(*pair))
    random.shuffle(elist)
    with codecs.open(rfile, 'w', encoding="utf-8") as fh:
        fh.write("\n".join(elist))


def export_all_person(rlist, rfile):
    """All persons per export item."""
    elist = []
    prefix = [u"yo", u"tú", u"él/ella/usted", u"nosotros/-as", u"vosotros/-as", u"ellos/ellas/ustedes"]
    for index, rdict in enumerate(rlist):
        for tempus in export_tempus:
            if not export_tempus[tempus][0]:
                continue
            ptempus = replacement.get(tempus, tempus)
            if export_tempus[tempus][1] > 1:
                question = u"<b>{german}</b><br/>Konjugation im <u>{tempus}</u>?".format(tempus=ptempus, german=', '.join(rdict[u"Alemán"]))
                answer = [u"{} <b>{}</b>".format(p, i) for p, i in zip(prefix[::-1], rdict[tempus][::-1])][::-1]
            else:                
                question = u"<b>{german}</b><br/>Wie lautet das <u>{tempus}</u>?".format(tempus=ptempus, german=', '.join(rdict[u"Alemán"]))
                answer = [u"<b>{}</b>".format(i) for i in rdict[tempus]]
            elist.append(u"{}&{}".format(question, '<br/>'.join(answer)))
    random.shuffle(elist)
    with codecs.open(rfile, 'w', encoding="utf-8") as fh:
        fh.write("\n".join(elist))


if __name__ == '__main__':
    rlist = read_vocdata(filename)
    export_single_person(rlist, "import_s.txt")
    export_all_person(rlist, "import_a.txt")

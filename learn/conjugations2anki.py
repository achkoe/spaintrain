# -*- coding: UTF-8 -*-
import json
import codecs

NO, YES = 0, 1
EXPORT_IRREGULAR = True
EXPORT_REGULAR = False


def is_to_export(item):
    return item["A_priority"] <= 1
    return item["A_irregular"]["presente"] is True and item["A_priority"] <= 10


export = {
    u'anterior': NO,
    u'subjuntivoimperfecto': NO,
    u'imperativoafirmativo': NO,
    u'imperativonegativo': NO,
    u'gerundio': NO,
    u'indefinido': NO,
    u'subjuntivofuturo': NO,
    u'subjuntivoperfecto': NO,
    u'participio': NO,
    u'subjuntivopluscuamperfecto': NO,
    u'futuroperfecto': NO,
    u'condicionalperfecto': NO,
    u'imperativoafirmativoreflexiv': NO,
    u'imperfecto': NO,
    u'condicional': NO,
    u'pluscuamperfecto': NO,
    u'gerundioreflexiv': NO,
    u'perfecto': NO,
    u'subjuntivopresente': NO,
    u'presente': YES,
    u'subjuntivofuturoperfecto': NO,
    u'futuro': NO,
    u'A_infinitivo': NO,
    u'A_english': NO,
    u'A_german': NO,
}

infile = "verben.json"
outfile = "verben4anki.txt"

replacementdict = {
    u'anterior': u'Pretérito anterior',
    u'subjuntivoimperfecto': u'Subjuntivo Imperfecto',
    u'imperativoafirmativo': u'Imperativo afirmativo',
    u'imperativonegativo': u'Imperativo negativo',
    u'A_infinitivo': u'Infinitivo',
    u'gerundio': u'Gerundio',
    u'indefinido': u'Pretérito indefinido',
    u'subjuntivofuturo': u'Subjuntivo Futuro',
    u'subjuntivoperfecto': u'Subjuntivo Perfecto',
    u'participio': u'Participio',
    u'subjuntivopluscuamperfecto': u'Subjuntivo Pluscuamperfecto',
    u'futuroperfecto': u'Futuro perfecto',
    u'condicionalperfecto': u'Condicional perfecto',
    u'imperativoafirmativoreflexiv': u'Imperativo afirmativo reflexivo',
    u'imperfecto': u'Pretérito imperfecto',
    u'condicional': u'Condicional',
    u'pluscuamperfecto': u'Pretérito pluscuamperfecto',
    u'gerundioreflexiv': u'Gerundio reflexivo',
    u'perfecto': u'Pretérito perfecto compuesto',
    u'subjuntivopresente': u'Subjuntivo Presente',
    u'presente': u'Presente',
    u'A_english': u'Ingles',
    u'subjuntivofuturoperfecto': u'Subjuntivo Futuro Perfecto',
    u'A_german': u'Aleman',
    u'futuro': u'Futuro',
}

pronomenlist = [
    ("s1", u"yo"), ("s2", u"tú"), ("s3", u"él/ella/usted"),
    ("p1", u"nosotros/-as"), ("p2", u"vosotros/-as"), ("p3", u"ellos/ellas/ustedes")
]

if __name__ == '__main__':
    rlist = json.load(open(infile))
    olist = []
    linebreak = u"\n"
    linebreak = u"<br/>"
    exportlist = [key for key in export if export[key] == YES]
    for item in rlist:
        if not is_to_export(item):
            continue
        for key in exportlist:
            assert not key.startswith(u"A_")
            if key in item.get("A_exported", []):
                print(u"{}, {} already exported").format(item["A_infinitivo"], key)
                continue
            item["A_exported"] = item.get("A_exported", [])
            item["A_exported"].append(key)
            answerlist = []
            question = u"<b>{german}</b>{linebreak}Konjugation des Verbs im <b>{tense}</b>?"
            if key.startswith("imperativo"):
                for pitem in pronomenlist[1:]:
                    answerlist.append(u"{p} {s}".format(p=pitem[1], s=item[key][pitem[0]]))
            elif key in ["gerundio", "gerundioreflexiv", "participio"]:
                question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b> des Verbs?"
                answerlist.append(item[key])
            else:
                for pitem in pronomenlist:
                    answerlist.append(u"{p} {s}".format(p=pitem[1], s=item[key][pitem[0]]))
            question = question.format(linebreak=linebreak, german=item["A_german"], tense=replacementdict[key])
            olist.append(
                u"{question}|"
                u"{infinitivo}{linebreak}{answer}|Verb".format(
                    question=question,
                    linebreak=linebreak,
                    infinitivo=item["A_infinitivo"],
                    answer=linebreak.join(answerlist))
            )
    with codecs.open(outfile, "w", encoding="utf-8") as fh:
        fh.write(u"\n".join(olist))

    with codecs.open("verben.json", "w", encoding="utf-8") as fh:
        json.dump(rlist, fh, sort_keys=True, indent=4, ensure_ascii=False)



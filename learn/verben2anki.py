# -*- coding: UTF-8 -*-
import random
import codecs
import sqlite3
import argparse
from verbenedit import getmapping


infile = "verben.db"
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
    u"yo", u"tú", u"él/ella/usted", u"nosotros/-as", u"vosotros/-as", u"ellos/ellas/ustedes"
]


def export():
    linebreak = u"<br/>"
    mapping = getmapping()
    querylist = [u'anterior', u'subjuntivoimperfecto', u'imperativoafirmativo',
                 u'imperativonegativo', u'gerundio', u'indefinido', u'subjuntivofuturo',
                 u'subjuntivoperfecto', u'participio', u'subjuntivopluscuamperfecto',
                 u'futuroperfecto', u'condicionalperfecto', u'imperativoafirmativoreflexiv',
                 u'imperfecto', u'condicional', u'pluscuamperfecto', u'perfecto',
                 u'subjuntivopresente', u'presente', u'subjuntivofuturoperfecto',
                 u'gerundioreflexiv', u'futuro']
    dbname = infile
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    rlist = []
    for query in querylist:
        cursor.execute("SELECT id from export WHERE {} == 1".format(query))
        idlist = cursor.fetchall()
        if len(idlist) == 0:
            continue
        for id_ in idlist:
            if query in ["participio", "gerundio", "gerundioreflexiv"]:
                result = cursor.execute("""SELECT german, infinitivo, {} FROM verben WHERE id == ?""".format(query), id_).fetchone()
                question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                    german=result[0],
                    linebreak=linebreak,
                    tense=replacementdict[query])
                rlist.append([question, "{}{}{}".format(result[1], linebreak, result[-1])])
            else:
                result_a = cursor.execute("""SELECT german, infinitivo FROM verben WHERE id == ?""".format(query), id_).fetchone()
                result_b = cursor.execute("""SELECT s1, s2, s3, p1, p2, p3 FROM {} WHERE id == ?""".format(query), id_).fetchone()
                question = u"<b>{german}</b>{linebreak}Konjugation des Verbs im <b>{tense}</b>?".format(
                    german=result_a[0],
                    linebreak=linebreak,
                    tense=replacementdict[query])
                tlist = [result_a[1]]
                for pronomen, result in zip(pronomenlist, result_b):
                    if result is None:
                        continue
                    tlist.append("{} {}".format(pronomen, result))
                rlist.append([question, linebreak.join(tlist)])
            cursor.execute("UPDATE export set {} = 2 WHERE id == ?".format(query), id_)
    conn.commit()
    conn.close()

    random.shuffle(rlist)
    ostr = "\n".join(u"{}|{}|{}".format(ritem[0], ritem[1], "Verb") for ritem in rlist)
    with codecs.open(outfile, "w", encoding="utf-8") as fh:
        fh.write(ostr)

    #print(rlist)
    return
    if 0:
        fieldmapping = ["german", "infinitiv"]
        if isinstance(mapping[query], dict):
            fieldmapping.extend(mapping[query].values())
        else:
            fieldmapping.append(mapping[query])
        cursor.execute("SELECT {} FROM verben WHERE {}_export == 1".format(",".join(fieldmapping), query))
        for result in cursor.fetchall():
            if query in ["participio", "gerundio", "gerundioreflexiv"]:
                question = u"<b>{german}</b>{linebreak}Wie lautet das <b>{tense}</b>?".format(
                    german=result[0],
                    linebreak=linebreak,
                    tense=replacementdict[query])
                rlist.append([question, "{}{}{}".format(result[1], linebreak, result[-1])])
            else:
                question = u"<b>{german}</b>{linebreak}Konjugation des Verbs im <b>{tense}</b>?".format(
                    german=result[0],
                    linebreak=linebreak,
                    tense=replacementdict[query])
                tlist = [result[1]]
                for pronomen in pronomenlist:
                    try:
                        index = fieldmapping.index("{}_{}".format(query, pronomen[0]))
                    except ValueError:
                        continue
                    tlist.append(u"{} {}".format(pronomen[1], result[index]))
                rlist.append([question, linebreak.join(tlist)])

        cursor.execute("UPDATE verben SET {0}_export = 2 WHERE {0}_export == 1".format(query))
    conn.commit()
    conn.close()

    ostr = "\n".join(u"{}|{}|{}".format(ritem[0], ritem[1], "Verb") for ritem in rlist)
    with codecs.open(outfile, "w", encoding="utf-8") as fh:
        fh.write(ostr)


def test(infinitiv, exporttime):
    dbname = "verben.db"
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM verben WHERE infinitiv == ?", (infinitiv, ))
    print(cursor.fetchall())
    cursor.execute("UPDATE verben SET {}_export = 0".format(exporttime))
    cursor.execute("UPDATE verben SET {}_export = 1 WHERE infinitiv == ?".format(exporttime), (infinitiv, ))
    cursor.execute("SELECT infinitiv FROM verben WHERE {}_export == 1".format(exporttime))
    print(cursor.fetchall())
    conn.commit()
    conn.close()


def mark(verblist, tenselist):
    dbname = infile
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    query = ",".join(repr(v) for v in verblist)
    if 1:
        cursor.execute("SELECT id, infinitivo FROM verben WHERE infinitivo IN ({})".format(query))
        resultlist = cursor.fetchall()
        for result in resultlist:
            if cursor.execute("SELECT id FROM export WHERE id == ?", (result[0], )).fetchone() is not None:
                continue
            fieldlist = ["id"] + tenselist
            valuelist = [str(result[0])] + ["1"] * len(tenselist)
            cursor.execute("""INSERT INTO export ({}) VALUES ({})""".format(",".join(fieldlist), ",".join(valuelist)))
    conn.commit()
    conn.close()


def markselected():
    tenselist = [
        "condicional", "futuro", "imperativoafirmativo", "imperfecto", "indefinido",
        "presente", "subjuntivopresente", "gerundio", "participio"]
    verblist = [
        "explicar", "deletrear", "costar", "vestir", "aconsejar", "cansar", "funcionar",
        "hartar", "interesar", "limpiar", "mandar", "notar", "ocurrir", "preocupar",
        "quejar", "reservar", "suponer", "tirar"]
    mark(verblist, tenselist)


def show_unexported():
    dbname = infile
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id, infinitivo, german FROM verben WHERE id NOT IN (SELECT id FROM export)")
    for item in cursor.fetchall():
        cursor.execute("SELECT presente FROM irregular WHERE id == ?", (item[0], ))
        irregular = ["", "[i]"][cursor.fetchone()[0]]
        item = list(item) + [irregular]
        print("{1}: {2} {3}".format(*item))
    #print([item[0] for item in cursor.fetchall()])
    print(u"\n".join(u"{0}: {1}".format(*item) for item in cursor.fetchall()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--markselected", action="store_true")
    parser.add_argument("-e", "--export", action="store_true")
    parser.add_argument("-s", "--showunexported", action="store_true")
    args = parser.parse_args()
    if args.markselected:
        markselected()
    if args.export:
        export()
    if args.showunexported:
        show_unexported()

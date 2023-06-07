#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verb Conjugations

Step 1: update database
Step 2: update translations
Step 3: export all in one
"""

from __future__ import print_function
import json
import argparse
import codecs
import requests
from bs4 import BeautifulSoup
import random


JSON_DB = "voctiempo.json"


def get_conjugations(word):
    # fiter unwanted informations
    filterlist = [u"(", u")", u"yo", u"tú", u"él/ella/Ud.", u"nosotros", u"vosotros", u"ellos/ellas/Uds."]
    # times we are interested in
    mergelist = [u'Pretérito perfecto compuesto', u'Pretérito pluscuamperfecto', u'Pretérito anterior',
                 u'Futuro perfecto', u'Condicional perfecto', u'Pretérito pluscuamperfecto',
                 u'Pretérito pluscuamperfecto (2)', u'Futuro perfecto']
    # read from website
    URL = "https://konjugator.reverso.net/konjugation-spanisch-verb-{}.html".format(word)
    r = requests.get(URL)
    print(r.status_code)
    soup = BeautifulSoup(r.text, "lxml")
    entrylist = soup.find_all("div", class_="responsive-sub")
    rlist = []
    for e in entrylist:
        # strip unwanted informations
        tl = [item for item in e.get_text("\n", strip=True).splitlines() if item not in filterlist]
        # if it is time we are interested in
        if tl[0] in mergelist:
            ttl = [tl[0]]
            if ttl[0] == 'Infinitivo compuesto':
                print(">h")
            for index in range(1, len(tl) - 1, 2):
                ttl.append(u"{} {}".format(tl[index], tl[index + 1]))
            tl = ttl
        tl.insert(0, e.parent.find_all("h3")[0].get_text(strip=True))
        if tl[0] in ['Infinitivo compuesto', 'Gerundio compuesto', ]:
            tl = [tl[0], u"{} {}".format(*tl[1:])]
        rlist.append(tl)
    return rlist


def read_database(dbname):
    return json.load(open(dbname))


def write_database(dbname, database):
    json.dump(database, open(dbname, 'w'), indent=4)


def update_database(database, wordlist):
    print("update_database")
    for word in wordlist:
        conjugate_list = get_conjugations(word)
        dbitem = database.get(word, {})
        for item in conjugate_list:
            mode = item[0]
            if item[0] in ("Indicativo", "Subjuntivo"):
                tempus = item[1]
                conjugate = item[2:]
                dbitem.update({mode: dbitem.get(mode, {})})
                dbitem[mode].update({tempus: dbitem[mode].get(tempus, conjugate)})
            else:
                conjugate = item[1:]
                dbitem.update({mode: dbitem.get(mode, conjugate)})
        dbitem.update({"_translate": dbitem.get("_translate", "")})
        database.update({word: dbitem})
        write_database(JSON_DB, database)


def export_all_in_one(database, exportobj, resultfilename):
    print("export for TempusTrain2")
    prefix = [u"yo", u"tú", u"él/ella/usted", u"nosotros/-as", u"vosotros/-as", u"ellos/ellas/ustedes"]
    replacement = {u"Participio pasado": u"Participio", u"Pretérito perfecto simple": u"Pretérito indefinido"}
    elist = []
    for word, dictobj in database.items():
        for key in dictobj.keys():
            if not exportobj[key].get("_export", False):
                continue
            tempus_list = [_ for _ in exportobj[key] if not _.startswith('_')]
            if len(tempus_list) > 0:
                for tempus in tempus_list:
                    if not exportobj[key][tempus].get("_export", False):
                        continue
                    # print(key, tempus, word, dictobj[key][tempus])
                    question = u"<b>{german}</b><br/>Konjugation im <u>{mode} {tempus}</u>?".format(
                        mode=key, tempus=replacement.get(tempus, tempus), german=dictobj[u"_translate"])
                    answer = "<br/>".join([u"{} <b>{}</b>".format(p, i) for p, i in zip(
                        prefix[::-1], dictobj[key][tempus][::-1])][::-1])
            else:
                # print(key, word, dictobj[key])
                if len(dictobj[key]) > 1:
                    question = u"<b>{german}</b><br/>Konjugation im <u>{tempus}</u>?".format(
                        tempus=replacement.get(key, key), german=dictobj[u"_translate"])
                    answer = "<br/>".join([u"{} <b>{}</b>".format(p, i) for p, i in zip(
                        prefix[::-1], dictobj[key][::-1])][::-1])
                    pass
                else:
                    question = u"<b>{german}</b><br/>Wie lautet das <u>{tempus}</u>?".format(
                        tempus=replacement.get(key, key), german=dictobj[u"_translate"])
                    answer = "<br/>".join([u"<b>{}</b>".format(p) for p in dictobj[key][::-1]][::-1])
            elist.append(u"{}&{}".format(question, answer))
    random.shuffle(elist)
    with codecs.open(resultfilename, 'w', encoding="utf-8") as fh:
        fh.write("\n".join(elist))


def translate(word, lang):
    URL = "http://dict.leo.org/dictQuery/m-vocab/%(lang)s/query.xml?" \
          "tolerMode=nof&lp=%(lang)s&lang=de&rmWords=off&rmSearch=on&search=%(word)s&" \
          "searchLoc=0&resultOrder=basic&multiwordShowSingle=on"
    r = requests.get(URL % {'lang': lang, 'word': word})
    soup = BeautifulSoup(r.text, 'xml')
    entries = soup.find_all('entry')
    if entries:
        return [tuple([side.find('word').get_text()
                       for side in entry.find_all('side')])
                for entry in entries]


def update_translations(database):
    print("update translations")
    for word in database:
        translation = translate(word, "esde")
        if not translation:
            continue
        translation = [t[1] for t in translation[:min(3, len(translation))]]
        database[word]["_translate"] = ', '.join(translation)
    write_database(JSON_DB, database)


exportobj = {
    "Infinitivo": {"_export": False, "_title": ""},
    "_translate": {"_export": False, "_title": ""},
    "Participio pasado": {"_export": False, "_title": ""},
    "Imperativo": {"_export": False, "_title": ""},
    "Gerundio compuesto": {"_export": False, "_title": ""},
    "Infinitivo compuesto": {"_export": False, "_title": ""},
    "Gerundio": {"_export": False, "_title": ""},
    "Subjuntivo": {
        "_export": True, "_title": "",
        u'Pret\xe9rito perfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito pluscuamperfecto (2)': {"_export": False, "_title": ""},
        u'Presente': {"_export": True, "_title": ""},
        u'Pret\xe9rito imperfecto (2)': {"_export": False, "_title": ""},
        u'Futuro perfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito imperfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito pluscuamperfecto': {"_export": False, "_title": ""},
        u'Futuro': {"_export": False, "_title": ""},
    },
    "Indicativo": {
        "_export": False, "_title": "",
        u'Condicional perfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito anterior': {"_export": False, "_title": ""},
        u'Presente': {"_export": False, "_title": ""},
        u'Pret\xe9rito perfecto simple': {"_export": False, "_title": ""},
        u'Condicional': {"_export": False, "_title": ""},
        u'Futuro perfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito imperfecto': {"_export": False, "_title": ""},
        u'Pret\xe9rito pluscuamperfecto': {"_export": False, "_title": ""},
        u'Futuro': {"_export": False, "_title": ""},
        u'Pret\xe9rito perfecto compuesto': {"_export": False, "_title": ""},
    }
}

wordlist = [
    "abrir", "agradecer", "ampliar", "andar", "anunciar", "buscar", "caber",
    "caer", "cambiar", "comenzar", "comer", "conducir", "confiar", "conocer",
    "construir", "copiar", "crecer", "dar", "decir", "descubrir", "desviar",
    "doler", "dormir", "eligir", "empezar", "enviar", "escribir", "esquiar",
    "estar", "estudiar", "guiar", "haber", "hablar", "hacer", "imprimir",
    "introducir", "ir", "leer", "limpiar", "llegar", "mentir", "morir", "nacer",
    "negociar", "odiar", "oir", "pagar", "pedir", "poder", "poner", "preferir",
    "producir", "querer", "reducir", "resfriarse", "romper", "saber", "sacar",
    "salir", "sentir", "ser", "servir", "tener", "vaciar", "valer", "variar",
    "venir", "ver", "volver"]
wordlist = ["seguir"]
wordlist = ["pensar", "poder", "sentir", "dormir", "servir", "volver", "empezar", "seguir", "entender", "contar", "preferir"]
wordlist = ["creer", "seguir"]
wordlist = ["venir", "hacer", "poner", "salir", "tener", "saber", "caer", "traer", "oír", "construir", "decir", "conocer", "estar", "ir", "haber", "ser"]
wordlist = ["precipitar"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__.splitlines()[0], epilog="\n".join(__doc__.splitlines()[1:]))
    parser.add_argument("-s", "--step", type=int, nargs='*', choices=[1, 2, 3], help="perform step number")
    args = parser.parse_args()
    database = read_database(JSON_DB)
    if args.step is None or 1 in args.step:
        update_database(database, wordlist)
    if args.step is None or 2 in args.step:
        update_translations(database)
    if args.step is None or 3 in args.step:
        export_all_in_one(database, exportobj, "import_a.txt")

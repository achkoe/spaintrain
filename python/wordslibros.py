
"""Database tools for handling words from libros."""

import sys
import argparse
import os
import glob
import sqlite3
import re
import locale
import random
import json
from functools import partial
from datetime import datetime

assert sys.version_info[0] == 3
DBNAME = "wordslibros.db"

print(locale.getpreferredencoding())
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')


def collect_words():
    rootfolder = os.path.join(os.path.dirname(__file__), "..", "word")
    searchfile = "contents.txt"
    filelist = glob.glob(os.path.join(rootfolder, "**", searchfile))
    #for f in filelist: print(f)
    #sys.exit(0)
    filelist = [
        "../word/desaparecidas/contents.txt",
        "../word/un_dia_en_malaga/contents.txt",
        "../word/recetas_con_gusto/contents.txt",
        "../word/un_dia_en_barcelona/contents.txt",
        "../word/teruel/contents.txt",
        "../word/historia_gaviota/contents.txt",
        "../word/asesinato_en_cadiz/contents.txt",
        "../word/descubre_el_caribe/contents.txt",
        "../word/negocio_mortal/contents.txt",
        "../word/curriculum/contents.txt",
        "../word/ataque_en_la_montana/contents.txt",
        "../word/cocina/contents.txt",
        "../word/historia_caracol/contents.txt",
        "../word/una_siesta_fatal/contents.txt",
        "../word/crimen_de_la_giralda/contents.txt",
    ]

    regexp = re.compile(u"\[[^\]]*\]")

    infodict = {
        "../word/recetas_con_gusto/contents.txt": {"n": "Recetas con gusto", "s": False},
        "../word/un_dia_en_barcelona/contents.txt": {"n": "Un dia en barcelona", "s": True},
        "../word/teruel/contents.txt": {"n": "teruel", "s": False},
        "../word/historia_gaviota/contents.txt": {"n": "Historia gaviota", "s": False},
        "../word/descubre_el_caribe/contents.txt": {"n": "Descubre el caribe", "s": False},
        "../word/curriculum/contents.txt": {"n": "Curriculum", "s": False},
        "../word/historia_caracol/contents.txt": {"n": "Historia caracol", "s": False},
        "../word/desaparecidas/contents.txt": {"n": "Desaparecidas", "s": True},
        "../word/un_dia_en_malaga/contents.txt": {"n": "Un dia en Malaga", "s": True},
        "../word/asesinato_en_cadiz/contents.txt": {"n": "Asesinato en Cadiz", "s": False},
        "../word/negocio_mortal/contents.txt": {"n": "Negocio mortal", "s": True},
        "../word/ataque_en_la_montana/contents.txt": {"n": "Ataque en la montana", "s": True},
        "../word/cocina/contents.txt": {"n": "Cocina", "s": True},
        "../word/una_siesta_fatal/contents.txt": {"n": "Una siesta fatal", "s": True},
        "../word/crimen_de_la_giralda/contents.txt": {"n": "Crimen de la giralda", "s": False},
    }
    wordlist = []
    for fileitem in filelist:
        assert fileitem in infodict, fileitem

        with open(fileitem, "r") as fh:
            text = fh.read()
        matchlist = regexp.findall(text)
        for matchitem in matchlist:
            if matchitem.count("|") < 2:
                continue
            word = matchitem.strip("[]").split("|")
            if infodict[fileitem]["s"]:
                word[1], word[2] = word[2], word[1]
            if "Subst" in word[-1] and not (word[1].startswith("el") or word[1].startswith("la") or word[1].startswith("los") or word[1].startswith("las")):
                print("   {}: {}".format(infodict[fileitem]["n"], repr(word)))
            word.append(infodict.get(fileitem, fileitem)["n"])
            assert len(word) == 5, word
            wordlist.append(word[1:])
    sortfn = partial(keyfn, 0)
    return sorted(wordlist, key=sortfn)


def keyfn(index, a):
    a_ = a[index]
    if a_.startswith("el ") or a_.startswith("la ") or a_.startswith("las ") or a_.startswith("los ") or a_.startswith("a ") or a_.startswith("en ") or a_.startswith("el/la "):
        a_ = a_.split()[1]
        #print(a_)
    return locale.strxfrm(a_)
    return a_


def create_database():
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS words")
    cur.execute("CREATE TABLE WORDS (id INTEGER PRIMARY KEY AUTOINCREMENT, spain TEXT, german TEXT, type TEXT, source TEXT, exported INTEGER, created INTEGER, updated INTEGER)")
    con.commit()
    con.close()


def import_database(wordlist):
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    for word in wordlist:
        cur.execute("SELECT * FROM words WHERE spain LIKE ?", (word[0],))
        result = cur.fetchall()
        if len(result) != 0:
            #print(result)
            print("{!r} already in database".format(word[0]))
        else:
            word.append(0)
            try:
                now = datetime.now().timestamp()
                word.append(now)
                word.append(now)
                cur.execute("INSERT INTO WORDS (spain, german, type, source, exported, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?)", word)
                #print("OKAY: {}".format(word))
            except:
                print("FAIL: {}".format(word))
                raise
    con.commit()
    con.close()


def import_merged():
    with open("wordslibros_merged.json") as fh:
        wordlist = json.load(fh)
    return wordlist


def export_database():
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM words")
    wordlist = cur.fetchall()
    print(wordlist)
    sortfn = partial(keyfn, 1)
    wordlist = sorted(wordlist, key=sortfn)
    with open("wordslibros.txt", "w") as fh:
        for word in wordlist:
            print(word[:-2], file=fh)
    con.close()


def update_database():
    with open("wordslibros.txt") as fh:
        textlist = fh.readlines()
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    for line in textlist:
        arg = eval(line)
        #print("UPDATE words SET spain = {1!r}, german = {2!r}, type = {3!r}, source = {4!r}, exported = {5!r} WHERE id == {0}".format(*arg))
        cur.execute("UPDATE words SET spain = {1!r}, german = {2!r}, type = {3!r}, source = {4!r}, exported = {5!r} WHERE id == {0}".format(*arg))
        cur.execute("UPDATE words SET updated = {1} WHERE id == {0}".format(arg[0], datetime.now().timestamp()))
    con.commit()
    con.close()


def exportanki(args):
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    cur.execute("SELECT id FROM words WHERE exported == 0")
    idlist = [item[0] for item in cur.fetchall()]
    number = min(args.number, len(idlist))
    slist = [str(s) for s in random.sample(idlist, number)]
    # print(slist)
    cur.execute("SELECT spain, german, type, source FROM words WHERE id in ({})".format(",".join(slist)))
    with open("wordslibros4anki.txt", "w") as fh:
        for item in cur.fetchall():
            print("{0}|{1}|{2}|{3}".format(*item), file=fh)

    #cur.execute("UPDATE words SET exported = 1 WHERE id in ({})".format(",".join(slist)))
    con.commit()
    con.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--collect", help="collect words from word folder and update to database", action="store_true", default=False)
    parser.add_argument("--create", help="create database", action="store_true", default=False)
    parser.add_argument("--import", dest="imp", help="update database from wordslibros.txt", action="store_true", default=False)
    parser.add_argument("--export", help="export database to wordslibros.txt", action="store_true", default=False)
    parser.add_argument("--exportanki", help="export for anki", action="store_true", default=False)
    parser.add_argument("--importmerged", help="import from wordslibros_merged.json", action="store_true", default=False)
    parser.add_argument("-n", "--number", help="number of exports", action="store", type=int, default=10)

    args = parser.parse_args()
    print(args)
    if args.create:
        create_database()
    if args.collect:
        wordlist = collect_words()
        import_database(wordlist)
    if args.export:
        export_database()
    if args.imp:
        update_database()
    if args.importmerged:
        import_database(import_merged())
    if args.exportanki:
        exportanki(args)

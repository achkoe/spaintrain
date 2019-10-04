# -*- coding: utf-8 -*-
"""Different utilities for anki."""
import argparse
import sys
import codecs
import json
import re
sys.path.insert(0, "/usr/share/anki")
from anki import Collection
from collections import Counter
import pprint

PATH = "/home/achim/Anki/Achim/collection.anki2"
PATH = "/home/achim/Dokumente/Anki/Benutzer 1/collection.anki2"


def duestat(args):
    col = Collection(args._path)
    idlist = col.findCards(args.query)
    lbllist = ("new", "learning", "due")
    cnt = Counter({0: 0, 1: 0, 2: 0})
    for id_ in idlist:
        card = col.getCard(id_)
        cnt[card.type] += 1
    for index, lbl in enumerate(lbllist):
        print "{1:5}: {0}".format(lbl, cnt[index])


def listitems(args):
    col = Collection(args._path)
    idlist = col.findCards(args.query)
    print len(idlist)
    for id_ in idlist:
        card = col.getCard(id_)
        note = card.note()
        print note.items()
    col.close()


def setsource(args):
    col = Collection(args._path)
    idlist = col.findCards(args.query)
    args.source = unicode(args.source)
    print len(idlist)
    for id_ in idlist:
        card = col.getCard(id_)
        note = card.note()
        sourcelist = [s.strip() for s in note["source"].split(",")]
        sourcelist = [s.replace("&nbsp;", "") for s in sourcelist]
        if args.source not in sourcelist:
            sourcelist.append(args.source)
        note["source"] = ", ".join(sourcelist)
        print note["source"]
        if args.write:
            note.flush()
    col.close()


def delsource(args):
    col = Collection(args._path)
    idlist = col.findCards(args.query)
    args.source = unicode(args.source)
    print len(idlist)
    for id_ in idlist:
        card = col.getCard(id_)
        note = card.note()
        sourcelist = [s.strip() for s in note["source"].split(",")]
        sourcelist = [s.replace("&nbsp;", "") for s in sourcelist]
        if args.source in sourcelist:
            sourcelist.remove(args.source)
        note["source"] = ", ".join(sourcelist)
        print note["source"]
        if args.write:
            note.flush()
    col.close()


def prepimport2anki(args):
    with open(args.inputfile, 'r') as fh:
        textlist = fh.read().splitlines()
    with open(args.output, "w") as fh:
        for line in textlist:
            fh.write(line.replace("|", " @ "))
            fh.write("\n")


def import2anki(args):
    # with help from https://www.juliensobczak.com/tell/2016/12/26/anki-scripting.html
    config = {
        "path": "/home/achim/Dokumente/Anki/Benutzer 1/collection.anki2",
        "deckname": "SpainTrain2",
        "modelname": u'Einfach (beide Richtungen)',
        # mapping dataitem > anki field (0:Vorderseite, 1:Rückseite, 2:wordtype)
        "mappinglist": [0, 1, 2],
        "delimiter": u"|"
    }
    if args.config:
        with open("ankiutils.configurations") as fh:
            config = json.load(fh, encoding="utf-8")[args.config]
            assert("path" in config and "deckname" in config and "modelname" in config)
            assert("mappinglist" in config and "delimiter" in config)
    print config
    with codecs.open(args.inputfile, 'r', encoding="utf-8") as fh:
        textlist = fh.read().splitlines()
    datalist = [item.split(config["delimiter"]) for item in textlist]
    col = Collection(config["path"], log=True)
    model = col.models.byName(config["modelname"])
    col.decks.current()["mid"] = model["id"]
    deck = col.decks.byName(config["deckname"])

    for itemlist in datalist:
        ##print itemlist
        assert(len(itemlist) == len(config["mappinglist"]))
        note = col.newNote()
        note.model()["did"] = deck["id"]

        for item, mapping in zip(itemlist, config["mappinglist"]):
            ##print item, mapping
            ##print(note.fields)
            note.fields[mapping] = item
        note.fields[3] = unicode(args.source, "utf-8")

        col.addNote(note)
    if not args.dry_run:
        print "saving"
        col.save()
    else:
        print "dry run"
    # deck.close()


def makeworksheet(args):
    def replace(item):
        replacement = (
            ("<div>", " "), ("</div>", " "), ("<br\s*/?>", ", "), ("&nbsp;", " "),
            ("&auml;", u"ä"), ("&ouml;", u"ö"), ("&uuml;", u"ü"), ("<span[^>]*>", " "), ("</span>", " "), ("<b>", ""), ("</b>", ""))
        for pair in replacement:
            #item = item.replace(*pair)
            item = re.sub(pair[0], pair[1], item)
        return item

    resultdict = {"Subst": [], "Verb": [], "Adj": [], "Adv": []}
    col = Collection(args._path)
    # query = "deck:SpainTrain2 OR deck:Spaintrain1"
    # query = "rated:1"
    idlist = col.findCards(args.query)
    print len(idlist)
    for id_ in idlist:
        card = col.getCard(id_)
        note = card.note()
        itemdict = dict(note.items())
        # print itemdict.keys()
        for key in resultdict.keys():
            wordclass = itemdict.get(u"wordclass", itemdict.get(u"WordClass", None))
            if wordclass is None:
                print itemdict
                continue
            if key in wordclass:
                resultdict[key].append((replace(itemdict[u'Vorderseite']), replace(itemdict[u'R\xfcckseite'])))
    col.close()
    #
    maxlen = max([len(resultdict[key]) for key in resultdict])
    for key in resultdict:
        resultdict[key].extend([("", "")] * (maxlen - len(resultdict[key]) + 0))
    #
    outname = "worksheet.js"
    with codecs.open(outname, 'w', encoding="utf-8") as fh:
        fh.write(u"num = {};\n".format(int(len(idlist) * args.percentage / 100.0)))
        fh.write(u"obj = {{\n{}\n}};".format(
            ",\n".join(u"'{}': [{}]".format(
                key, u", ".join(u"['{}', '{}']".format(r[0], r[1]) for r in resultdict[key])) for key in resultdict)))


def ankitest(args):
    col = Collection(args._path)
    print dir(col)
    print help(col.findReplace)
    cnt = Counter()
    # query = "deck:SpainTrain2 OR deck:Spaintrain1"
    # query = "rated:1"
    idlist = col.findCards(unicode(args.query))
    #print len(idlist)
    for id_ in idlist:
        card = col.getCard(id_)
        note = card.note()
        itemdict = dict(note.items())
        #if "verb" in itemdict.get("wordclass", "").lower():
        if 1:
            #print itemdict[u"Rückseite"]
            #print itemdict[u"Vorderseite"]
            note.fields[0] = note.fields[0] + "."
            cnt[itemdict[u"Vorderseite"]] += 1
    col.save()
    col.close()
    #print u"\n".join(cnt.keys())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()
    #
    parser_sets = subparsers.add_parser("setsource", help="set source")
    parser_sets.add_argument("-w", "--write", action="store_true")
    parser_sets.add_argument("-q", "--query", action="store", help="for example deck:TempusTrain")
    parser_sets.add_argument("source")
    parser_sets.set_defaults(func=setsource)
    #
    parser_dsrc = subparsers.add_parser("delsource", help="del source")
    parser_dsrc.add_argument("-w", "--write", action="store_true")
    parser_dsrc.add_argument("-q", "--query", action="store", help="for example deck:TempusTrain")
    parser_dsrc.add_argument("source")
    parser_dsrc.set_defaults(func=delsource)
    #
    parser_duestat = subparsers.add_parser("duestat", help="due statistics")
    parser_duestat.add_argument("-q", "--query", action="store", help="for example deck:TempusTrain")
    parser_duestat.set_defaults(func=duestat)
    #
    parser_list = subparsers.add_parser("list", help="list")
    parser_list.add_argument("-q", "--query", action="store")
    parser_list.set_defaults(func=listitems)
    #
    parser_prepimport = subparsers.add_parser("prepimport", help="prepare for import into anki")
    parser_prepimport.add_argument("-o", "--output", action="store", default="ankiimport.txt", help="output file, default %(default)s")
    parser_prepimport.add_argument("inputfile")
    parser_prepimport.set_defaults(func=prepimport2anki)
    #
    parser_import = subparsers.add_parser("import", help="import items separated with | to anki")
    parser_import.add_argument("-c", "--config", action="store", default=None, help="config file, default %(default)s")
    parser_import.add_argument("-d", "--dry-run", action="store_true", help="dry run")
    parser_import.add_argument("inputfile", help="input file to be imported")
    parser_import.add_argument("source", help="value of source field")
    parser_import.set_defaults(func=import2anki)
    #
    parser_work = subparsers.add_parser("work", help="make work sheet")
    parser_work.set_defaults(func=makeworksheet)
    parser_work.add_argument("-p", "--percent", dest="percentage", action="store", default=10, type=int, help="percentage to do, default %(default)s")
    parser_work.add_argument("-q", "--query", action="store", default="rated:1")
    #
    parser_test = subparsers.add_parser("test", help="misc test")
    parser_test.add_argument("-q", "--query", action="store", default="deck:Spaintrain1")
    parser_test.set_defaults(func=ankitest)
    #
    args = parser.parse_args()
    args._path = PATH
    args.func(args)

# python ankiutils.py setsource --query="deck:Spaintrain2 source:*Kurs2*" Kurs2
# python ankiutils.py duestat --query="deck:TempusTrain"

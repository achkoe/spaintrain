from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import json
import codecs
import argparse


URL = u"http://www.spanisch-zeiten.de/konjugator/konjugieren/verb/{}"
URL_DB = u"http://www.spanisch-zeiten.de/konjugator/datenbank/verbregister"


def query_verb(verb):

    r = requests.get(URL.format(verb))
    soup = BeautifulSoup(r.content, "html.parser")

    table = soup.find(class_="konjugator")
    irregular = table.find(class_="irreg") is not None

    search = []
    for tr in table.find_all("tr", attrs={"class": ""}):
        for td in tr.find_all("td"):
            tdtext = td.text
            if tdtext:
                search.append(tdtext)

    base = []
    for index, s in enumerate(search):
        if s.endswith(':'):
            base.append(s)
            base.append(search[index + 1])

    base = [base[index:index + 2] for index in range(0, len(base), 2)]
    replacementlist = [
        ("Infinitiv:", "A_infinitivo"),
        ("Participio:", "participio"),
        ("Deutsch:", "A_german"),
        ("Gerundio:", "gerundio"),
        ("Englisch:", "A_english"),
        ("Gerundio (reflexiv):", "gerundioreflexiv")]
    assert len(base) == len(replacementlist)
    for t, r in zip(base, replacementlist):
        assert t[0] == r[0], "{!r} != {!r}".format(t[0], r[0])
        t[0] = r[1]
    # ---
    tense = []
    for ul in table.find_all("ul", attrs={"class": "tense"}):
        tense.append([li.text for li in ul.select("li")])

    replacementlist = [
        ("Presente", "presente"),
        ("Indefinido", "indefinido"),
        ("Imperfecto", "imperfecto"),
        ("Anterior", "anterior"),
        ("Perfecto", "perfecto"),
        ("Pluscuamperfecto", "pluscuamperfecto"),
        ("Futuro", "futuro"),
        ("Futuro Perfecto", "futuroperfecto"),
        ("Presente", "subjuntivopresente"),
        ("Imperfecto", "subjuntivoimperfecto"),
        ("Perfecto", "subjuntivoperfecto"),
        ("Pluscuamperfecto", "subjuntivopluscuamperfecto"),
        ("Futuro", "subjuntivofuturo"),
        ("Futuro Perfecto", "subjuntivofuturoperfecto"),
        ("Condicional", "condicional"),
        ("Condicional Perfecto", "condicionalperfecto"),
        ("Afirmativo", "imperativoafirmativo"),
        ("Afirmativo (reflexiv)", "imperativoafirmativoreflexiv"),
        ("Negativo", "imperativonegativo"),]
    assert len(tense) == len(replacementlist)
    for t, r in zip(tense, replacementlist):
        assert t[0] == r[0], "{!r} != {!r}".format(t[0], r[0])
        t[0] = r[1]

    rdict = dict(base)
    rdict.update({"A_irregular": irregular})

    for index in range(len(tense)):
        t = tense[index]
        keylist = ["s1", "s2", "s3", "p1", "p2","p3"]
        if t[0].startswith("imperativo"):
            keylist = keylist[1:]
        valuelist = t[1:]
        assert len(keylist) == len(valuelist)
        value = dict(zip(keylist, valuelist))
        rdict[t[0]] = value

    return rdict


def get_allverbs():
    r = requests.get(URL_DB)
    soup = BeautifulSoup(r.content, "html.parser")
    return list(set([item.text for item in soup.select("table tr td a")]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--getverbs", action="store_true", help="get verbs from internet")
    parser.add_argument("--verbfile", action="store", help="use verbs from file")
    args = parser.parse_args()
    print(args)

    verblistfile = "verblist.json"

    if args.getverbs:
        allverbs = get_allverbs()

        with codecs.open(verblistfile, "w", encoding="utf-8") as fh:
            json.dump(allverbs, fh, sort_keys=True, indent=4, ensure_ascii=False)

    if args.verbfile:
        allverbs = json.load(open("{}".format(args.verbfile)))
    else:
        allverbs = json.load(open("{}".format(verblistfile)))

    outputfile = "_verben.json"
    try:
        rlist = json.load(open(outputfile, "r"))
    except:
        rlist = []

    verblist = [item["A_infinitivo"] for item in rlist]

    for verb in allverbs:
        print(verb, end=" ... ")
        if verb in verblist:
            print("already stored")
        else:
            print("")

            try:
                rlist.append(query_verb(verb))
                verblist.append(verb)
            except Exception as e:
                print(e)
                break

    with codecs.open(outputfile, "w", encoding="utf-8") as fh:
        json.dump(rlist, fh, sort_keys=True, indent=4, ensure_ascii=False)


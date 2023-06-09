"""Get conjugations based on https://github.com/ian-hamlin/verb-data/tree/master/json/spanish/content

Download zip from https://github.com/ian-hamlin/verb-data, extract
folder verb-data-master/json/spanish/content from downloaded verb-data-master.zip to folder content.

zip 'content' folder to file spanish_conjugations.zip
"""

import argparse
import json
import pathlib
import zipfile
import requests
from bs4 import BeautifulSoup


URL = "https://raw.githubusercontent.com/ian-hamlin/verb-data/master/json/spanish/content/{firstletter}/{infinitiv}.json"
#      https://raw.githubusercontent.com/ian-hamlin/verb-data/master/json/spanish/content/a/arponar.json

prefix = ["yo", "tú", "él/ella/usted", "nosotros/-as", "vosotros/-as", "ellos/ellas/ustedes"]
replacement = {"Participio pasado": "Participio", "Pretérito perfecto simple": "Pretérito indefinido"}


def get_json(infinitiv):
    firstletter = infinitiv[0]
    path = pathlib.Path(__file__).parent.joinpath("spanish_conjugations.zip")
    with zipfile.ZipFile(path, mode="r") as db:
        namelist = db.namelist()
        search = f"content/{firstletter}/{infinitiv}.json"
        assert search in namelist
        with db.open(search) as fh:
            dbitem = json.load(fh)
    assert dbitem.get("conjugations", None) is not None, dbitem
    return dbitem


def _get_json(infinitiv):
    firstletter = infinitiv[0]
    url = URL.format(firstletter=firstletter, infinitiv=infinitiv)
    # print(url)
    response = requests.get(url)
    assert response.status_code == 200, response.status_code
    return response.json()


def is_reflexive(conjugations):
    for conjugation in conjugations["conjugations"]:
        if conjugation.get("form", "") == "s1" and conjugation["group"] == "indicative/present":
            return conjugation["value"].startswith("me ")
    else:
        assert "Not found form/group"


def make_output_list(german, conjugations, reflexive):
    rdict = {
        "German": german,
        "Infinitivo": None,
        "Gerundium": None,
        "Participio": None,
        "Presente": dict(),
        "Pretérito indefinido": dict(),
        "Pretérito imperfecto": dict(),
        "Presente de Subjuntivo": dict(),
        "Imperfecto de Subjuntivo se": dict(),
        "Imperfecto de Subjuntivo ra": dict(),
        "Futuro simple": dict(),
        "Condicional simple": dict(),
        "Imperativo": dict(),
    }
    prefix = dict(s1="", s2="", s3="", p1="", p2="", p3="") if reflexive else dict(s1="yo ", s2="tú ", s3="él/ella/usted ", p1="nosotros/-as ", p2="vosotros/-as ", p3="ellos/ellas/ustedes ")
    for conjugation in conjugations["conjugations"]:
        if conjugation.get("group", "") == "infinitive":
            rdict["Infinitivo"] = "{}".format(conjugation["value"])
        elif conjugation.get("group", "") == "gerund":
            rdict["Gerundium"] = "{}".format(conjugation["value"])
        elif conjugation["group"] == "pastparticiple/singular" and conjugation["form"] == "masculine":
            rdict["Participio"] = "{}".format( conjugation["value"])
        elif conjugation["group"] == "indicative/present":
            if conjugation["form"] == "s2":
                conjugation["value"] = conjugation["value"].split("(")[0].strip()
            rdict["Presente"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "indicative/imperfect":
            rdict["Pretérito imperfecto"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "indicative/preterite":
            rdict["Pretérito indefinido"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "indicative/future":
            rdict["Futuro simple"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "indicative/conditional":
            rdict["Condicional simple"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "subjunctive/present":
            if conjugation["form"] == "s2":
                conjugation["value"] = conjugation["value"].split("(")[0].strip()
            rdict["Presente de Subjuntivo"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "subjunctive/imperfect_ra":
            rdict["Imperfecto de Subjuntivo ra"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "subjunctive/imperfect_se":
            rdict["Imperfecto de Subjuntivo se"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "imperative/affirmative":
            if conjugation["form"] != "s1":
                if conjugation["form"] == "s2":
                    conjugation["value"] = conjugation["value"].split("(")[0].strip()
                rdict["Imperativo"][conjugation["form"]] = "{}{}".format(prefix[conjugation["form"]], conjugation["value"])
        elif conjugation["group"] == "imperative/negative":
            # ignored
            pass
        elif conjugation["group"] == "subjunctive/future":
            # ignored
            pass
        elif conjugation["group"].startswith("pastparticiple"):
            # ignored
            pass
        else:
            print(conjugation)
    rlist = list()
    for key in ["Infinitivo"]:
        question = "<b>{0}</b><br/>Wie lautet das <b>{1}</b>?".format(rdict["German"], key)
        answer = rdict[key]
        rlist.append(f"{question}|{answer}")
    for key in ["Gerundium", "Participio"]:
        question = "<b>{0}</b><br/>Wie lautet das <b>{1}</b>?".format(rdict["German"], key)
        answer = "{1}<br/><br/>{0}".format(rdict[key], rdict["Infinitivo"])
        rlist.append(f"{question}|{answer}")
    for key in ["Presente", "Pretérito indefinido", "Pretérito imperfecto", "Presente de Subjuntivo", "Futuro simple", "Condicional simple"]:
        question = "<b>{0}</b><br/>Konjugation im <b>{1}</b>?".format(rdict["German"], key)
        answer = "{0}<br/><br/>{1}".format(rdict["Infinitivo"], "<br/>".join(rdict[key][t] for t in ["s1", "s2", "s3", "p1", "p2", "p3"]))
        rlist.append(f"{question}|{answer}")

    key = "Imperativo"
    question = '<b>{0}</b><br/>Konjugation im <b>{1}</b>?'.format(rdict["German"], key)
    answer = answer = "{0}<br/><br/>{1}".format(rdict["Infinitivo"], "<br/>".join(rdict[key][t] for t in ["s2", "s3", "p1", "p2", "p3"]))
    rlist.append(f"{question}|{answer}")

    question = '<b>{0}</b><br/>Konjugation im <b><u><font color="#ef2929">{1}</font></u></b>?'.format(rdict["German"], "Imperfecto de Subjuntivo")
    answer = answer = "{0}<br/><br/>{1}".format(rdict["Infinitivo"],
             "<br/>".join(rdict["Imperfecto de Subjuntivo ra"][t] for t in ["s1", "s2", "s3", "p1", "p2", "p3"])
             + "<br/><br/>"
             + "<br/>".join(rdict["Imperfecto de Subjuntivo se"][t] for t in ["s1", "s2", "s3", "p1", "p2", "p3"]))
    rlist.append(f"{question}|{answer}")
    return rlist


def list_all_keys(conjugations):
    for conjugation in conjugations["conjugations"]:
        print("{} - {}".format(conjugation.get("group", None), conjugation.get("form", None)))


def translate(word, lang):
    URL = "http://dict.leo.org/dictQuery/m-vocab/%(lang)s/query.xml?" \
          "tolerMode=nof&lp=%(lang)s&lang=de&rmWords=off&rmSearch=on&search=%(word)s&" \
          "searchLoc=0&resultOrder=basic&multiwordShowSingle=on"
    r = requests.get(URL % {'lang': lang, 'word': word})
    soup = BeautifulSoup(r.text, 'xml')
    entries = soup.find_all('entry')
    translation = None
    if entries:
        translation = [tuple([side.find('word').get_text() for side in entry.find_all('side')]) for entry in entries]
    assert translation is not None
    return ", ".join([t[1] for t in translation[:min(3, len(translation))]])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__.splitlines()[0], epilog="\n".join(__doc__.splitlines()[1:]))
    parser.add_argument("infinitiv", type=str, nargs='+', help="infinitiv")
    parser.add_argument("-s", dest="save", action="store_true", help="store conjugations to file")
    args = parser.parse_args()
    rlist = list()
    for infinitiv in args.infinitiv:
        print(infinitiv)
        translation = translate(infinitiv, "esde")
        conjugation = get_json(infinitiv)
        if args.save:
            with open(f"{infinitiv}.json", "w", encoding="utf-8") as fh:
                json.dump(conjugation, fh, indent=4, ensure_ascii=False)
        reflexive = is_reflexive(conjugation)
        print(f"{infinitiv} (reflexive: {reflexive}): {translation}")
        rlist.extend(make_output_list(translation, conjugation, reflexive))

    with pathlib.Path(__file__).with_suffix(".txt").open("w", encoding="utf-8") as fh:
        for item in rlist:
            print(item, file=fh)
    print(f"\n{fh.name} written")

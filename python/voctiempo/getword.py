#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import codecs
import requests
from bs4 import BeautifulSoup



def translate(word):
    def classsearch(name):
        return name.startswith("responsive-sub")

    URL = "http://konjugator.reverso.net/konjugation-spanisch-verb-{}.html".format(word)
    r = requests.get(URL)
    if 0:
        print (r.text)
    soup = BeautifulSoup(r.text, "lxml")
    entrylist = soup.find_all("div", class_="responsive-sub")
    rlist = []
    filterlist = [u"(", u")", u"yo", u"tú", u"él/ella/Ud.", u"nosotros", u"vosotros", u"ellos/ellas/Uds."]
    mergelist = [u'Pretérito perfecto compuesto', u'Pretérito pluscuamperfecto', u'Pretérito anterior', u'Futuro perfecto',
                 u'Condicional perfecto', u'Pretérito pluscuamperfecto', u'Pretérito pluscuamperfecto (2)',
                 u'Futuro perfecto',
                ]
    for e in entrylist:
        tl = [item for item in e.get_text("\n", strip=True).splitlines() if item not in filterlist]
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


def fmt(rlist):
    r = []
    rlist = [item for item in rlist if not item[0].startswith("Subjuntivo")]
    for item in rlist:
        if item[0].startswith("Indicativo"):
            r.append(u"{}: {}".format(item[1], ", ".join(item[2:])))
        else:
            r.append(u"{}: {}".format(item[0], ", ".join(item[1:])))
    return r


def fmt_subjuntivo(rlist):
    r = []
    rlist = [item for item in rlist if item[0].startswith("Subjuntivo")]
    for item in rlist:
        r.append(u"Subjuntivo {}: {}".format(item[1], ", ".join(item[2:])))
    return r


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
wordlist = ["creer"]
wordlist = ["pensar", "poder", "sentir", "dormir", "servir", "volver", "empezar", "seguir", "entender", "contar", "preferir"]


if __name__ == '__main__':
    if 0:
        parser = argparse.ArgumentParser()
        parser.add_argument("word")
        args = parser.parse_args()
        r = translate(args.word)
        r = fmt(r)
        with open("wordlist.txt", "a") as fh:
            print("\n".join(r) + "\n", file=fh)
    else:
        with codecs.open("wordlist.txt", "a", encoding="utf-8") as fh:
            for word in wordlist:
                ro = translate(word)
                r = fmt(ro)
                print(u"\n".join(r) + u"\n", file=fh)
                r = fmt_subjuntivo(ro)
                print(u"\n".join(r) + u"\n", file=fh)


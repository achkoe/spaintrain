#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Postprocessor for text to HTML."""

import argparse
import json
import logging
from functools import partial
import pathlib
import re

TEMPLATE = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>{title}</title>
        <style>
        {css}
        </style>
        <script>
        {script}
        </script>
    </head>

    <body>
        <header><button id="gotopage">Goto last position</button></header>
        <main>
            <section class="left">
            {text}
            </section>
            <aside class="right">
            {dictionary}
            </aside>
        </main>
    </body>
</html>
"""
# dict telling how special characters are sorted
SORTDICT = {"á": "a", chr(195): "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}


def get_script():
    with (pathlib.Path(__file__).parent.parent.joinpath("html", "script.js").open("r") as fh):
        script = fh.read()
    return script


def get_css():
    with (pathlib.Path(__file__).parent.parent.joinpath("html", "style.css").open("r") as fh):
        css = fh.read()
    return css


def get_html(text):
    """Replace special tags with their html equivalent."""
    
    def replace_function(adict, what, replacement, matchobj):    
        if what == "word":
            # print(f"what: {what}\nreplacement: {replacement}\nmatchobj: {matchobj}\n{matchobj.expand(replacement)}")
            # [previamente|previamente|zuvor, im Voraus|Adv]
            # [ppreviamente|previamente|zuvor, im Voraus|Adv|*] -> don't add to wordlist
            if matchobj.group(0).count("|") in [2, 3, 4]:
                tr = matchobj.group(2).split("|")
                add_to_wordlist = len(tr) < 4
                if matchobj.group(2).count("|") in [2, 3]:
                    try:
                        tr = [item.replace("::", "|") for item in tr]
                        if add_to_wordlist:
                            wordlist.append((tr[0].strip(), tr[1].strip(), tr[2].strip()))
                    except Exception:
                        print(tr)
                        raise
                return '<a href="#{2}" title="{0}" class="dict">{1}</a>'.format(
                    tr[1], 
                    matchobj.group(1), 
                    tr[0].replace(" ", "$").replace("/", "$"))
            elif matchobj.group(0).count("|") > 1:
                raise ValueError("invalid translation tag: {}".format(matchobj.group(0)))  
        elif what == "paragraph":
            adict["counter"] += 1
            return f'<a href="#" class="bookmark"> <hr id="b{adict["counter"]}" /> </a>'
            
        return matchobj.expand(replacement)
        
    adict = {"counter": 0, "alist": []}
    wordlist = []
    replacement_map = {
        r"^\s*$": {
            "what": "paragraph",
            "replace": "ZZZZ",  # handled in replace_function
            "flags": re.MULTILINE
        },
        r"\[([^|]+)\|([^\]]+)\]": {
            "what": "word",
            "replace": r"",  # handled in replace_function
            "flags": 0
        },
        r"^%(.*)": {
            "what": "comment",
            "replace": r"<!-- \1 -->",
            "flags": re.MULTILINE
        },
        r"^-([^-]+)-$": {   
            "what": "section",
            "replace": r"<h1>\1</h1>", 
            "flags": re.MULTILINE
        },
        r"_(.+?)_": {
            "what": "italic",
            "replace": r"<em>\1</em>", 
            "flags": 0
        },
        r"\s*/(\d+)/\s*": {
            "what": "pagenumber",
            "replace": " ",
            "flags": 0
        },
        r"^- ":  {
            "what": "speech",
            "replace": "<br/>&ndash;&nbsp;", 
            "flags": re.MULTILINE
        },
        r"---":  {
            "what": "speech",
            "replace": "&ndash;", 
            "flags": re.MULTILINE
        },
        r"\\clearpage":  {
            "what": "tex",
            "replace": "", 
            "flags": re.MULTILINE
        },
    }
    for key, replacement in replacement_map.items():
        rf = partial(replace_function, adict, replacement["what"], replacement["replace"])
        text = re.sub(key, rf, text, flags=replacement["flags"])
    return text, wordlist


def get_dictionary(wordlist):
    
    def keyfn(item):
        printitem = item[0]
        wlist = printitem.split()
        if (len(wlist) > 1 and wlist[0].startswith("(") or wlist[0] in ("lo", "la", "los", "las", "el", "a", "de")):
            printitem = wlist[1]
        for k, r in SORTDICT.items():
            printitem = printitem.replace(k, r)
        return printitem.lower()

    wordlist.sort(key=keyfn)
    links = set()
    text = []
    for item in wordlist:
        target = keyfn(item)[0].upper()
        if target not in links:
            text.append(f'<h1 id="{target}">{target}</h1>')
        text.append(f'<dl>\n<dt id="{item[0].replace(' ', '$').replace('/', '$')}">{item[0]}</dt>\n<dd>{item[1]}</dd>\n</dl>\n')
        links.add(target)
    links = sorted(list(links))
    links = [f'<a href="#{item}">{item}</a>' for item in links]
    links.extend(text)
    return "\n".join(links)


def process():
    """Read contents.txt, process it and write result to html file"""
    with pathlib.Path("contents.txt").open("r", encoding="utf-8") as fh:
        text = fh.read()
    # region search meta information
    rdict = {"author": "---", "title": "---", "bookname": "book"}
    for search in rdict:
        mo = re.search(f"^%\\s*{search}:\\s*(.*)", text, re.M)
        if mo is None:
            print(f"NO {search} FOUND")
            continue
        rdict[search] = mo.group(1)
    # endregion
    title = rdict["bookname"]
    script = get_script()
    css = get_css()
    html, wordlist = get_html(text)
    dictionary = get_dictionary(wordlist)
    with pathlib.Path(f"{rdict['bookname']}.html").open("w") as fh:
        fh.write(TEMPLATE.format(title=title, script=script, css=css, text=html, dictionary=dictionary))


if __name__ == "__main__":
    process()

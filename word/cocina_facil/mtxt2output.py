#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Postprocessor for text to LaTex."""
import argparse
import sys
import re
import logging
import textwrap
import json
from collections import OrderedDict
from functools import partial

logging.basicConfig(level=logging.INFO, format="%(lineno)d: %(msg)s")


# dict telling how special characters are sorted
SORTDICT = {'á': 'a', chr(195): 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}


def check_duplicates(wordlist):
    """Check for duplicates in wordlist.

    To be improved.
    """
    comparelist = []
    for word in wordlist:
        item = word[0]
        if item.startswith("el ") or item.startswith("la "):
            item = item[3:]
        p = item.find("<br")
        if p == -1:
            p = len(item)
        q = item.find(" ")
        if q == -1:
            q = len(item)
        comparelist.append(item)
    for index, item in enumerate(comparelist):
        if comparelist.count(item) > 1:
            print("WARNING: {}".format(wordlist[index][0]))


def process_replace_tex(text):
    """Replace special tags with their latex equivalent.
    """
    adict = {
        "counter": 0,
        "alist": []
    }
    wordlist = []
    subdict = OrderedDict([
        (r"“", {"r": r'"', "flags": 0}),
        (r"”", {"r": r'"', "flags": 0}),
        (u'…', {"r": "\\\\ndots~", "flags": 0}),
        (u'\.\.\.', {"r": "\\\\ndots~", "flags": 0}),
        (r"[\s\[\"]\[([^|]+)\|([^\]]+)\]", {"r": r"\2\\footnote{\1}", "flags": 0}),
        (r"[\s\[\"]\{([^|]+)\|([^\}]+)\}", {"r": r"endnote", "flags": 0}),
        (r"\*\*([^*]+)\*\*", {"r": r"\\textbf{\1}", "flags": 0}),
        (r"__([^_]+)__", {"r": r"\\uline{\1}", "flags": 0}),
        (r'\"([^\"]+)\"', {"r": r"\\glqq{}\1\\grqq{}", "flags": 0}),
        (r"-->", {"r": r"$\\rightarrow$ ", "flags": 0}),
        (r"\.att", {"r": r"\\danger{}", "flags": 0}),
        (r"\.rem", {"r": r"\\eye{}", "flags": 0}),
        ###(r"\.\.\.", {"r": r"$\\ndots$ ", "flags": 0}),
        (r"//(.+?)//", {"r": r"\\textit{\1}", "flags": 0}),
        (r"_(.+?)_", {"r": r"\\textit{\1}", "flags": 0}),
        (r"\|\|([^|]+)\|\|", {"r": r"\\fbox{\1}", "flags": 0}),
        (r"<(.+)>", {"r": r"\\begin{small}\1\\end{small}", "flags": 0}),
        (r"^=([^=]+)=\s*(label{\w+})?\s*$", {"r": r"\\section{\1}", "flags": re.MULTILINE}),
        (r"^-([^-]+)-\s*(label{\w+})?\s*$", {"r": r"\\begin{multicols}{2}[\\section*{\1}]", "flags": re.MULTILINE}),
        (r"^==([^=]+)==\s*(label{\w+})?\s*$", {"r": r"\\subsection{\1}", "flags": re.MULTILINE}),
        (r"^--([^-]+)--\s*(label{\w+})?\s*$", {"r": r"\\subsection*{\1}", "flags": re.MULTILINE}),
        (r"^---([^-]+)---\s*(label{\w+})?\s*$", {"r": r"\\subsubsection*{\1}", "flags": re.MULTILINE}),

        (r"^- ", {"r": "---", "flags": re.MULTILINE}),
        (r"^\*", {"r": r"\\item", "flags": re.MULTILINE}),

        (r"\s*/(\d+)/\s*", {"r": r"~\\sidenote{\1}", "flags": 0}),
        (r"\s*%(\d+)\s*", {"r": r"~\\grammarnote{\1}", "flags": 0}),
        (r"^\.beginitemize", {"r": r"\\begin{compactitem}", "flags": re.MULTILINE}),
        (r"^\.enditemize", {"r": r"\\end{compactitem}", "flags": re.MULTILINE}),
        (r"^\\beginenum", {"r": r"\\begin{compactenum}", "flags": re.MULTILINE}),
        (r"^\\endenum", {"r": r"\\end{compactenum}", "flags": re.MULTILINE}),
        (r"^\\beginitshape", {"r": r"\\begin{itshape}", "flags": re.MULTILINE}),
        (r"^\\enditshape", {"r": r"\\end{itshape}", "flags": re.MULTILINE}),
        (r"/~", {"r": r"\\begin{itshape}", "flags": re.MULTILINE}),
        (r"~/", {"r": r"\\end{itshape}", "flags": re.MULTILINE}),
        (r"/:", {"r": r"\\begin{slshape}", "flags": re.MULTILINE}),
        (r":/", {"r": r"\\end{slshape}", "flags": re.MULTILINE}),
        (r"^\\beginquote", {"r": r"\\begin{quote}", "flags": re.MULTILINE}),
        (r"^\\endquote", {"r": r"\\end{quote}", "flags": re.MULTILINE}),

        (r"^::fin", {"r": r"\\end{multicols}\\begin{multicols}{2}\\parskip0pt\\theendnotes\\end{multicols}\\clearpage", "flags": re.MULTILINE}),
        (r"^::bintro", {"r": r"\\begin{eitemize}", "flags": re.MULTILINE}),
        (r"^::eintro", {"r": r"\\end{eitemize}", "flags": re.MULTILINE}),
        (r"^::blista", {"r": r"\\begin{iitemize}", "flags": re.MULTILINE}),
        (r"^::elista", {"r": r"\\end{iitemize}", "flags": re.MULTILINE}),
        (r"^::bbox", {"r": r"\\begin{boxit}", "flags": re.MULTILINE}),
        (r"^::ebox", {"r": r"\\end{boxit}", "flags": re.MULTILINE}),
    ])

    def replfn(adict, r, matchobj):
        if r.find("footnote") != -1:
            if matchobj.group(0).count("|") in [2, 3]:
                tr = matchobj.group(2).split("|")
                if matchobj.group(2).count("|") == 2:
                    try:
                        tr = [item.replace("::", "<br/>") for item in tr]
                        wordlist.append((tr[0].strip(), tr[1].strip(), tr[2].strip()))
                    except Exception:
                        print(tr)
                        raise
                return ' ' + matchobj.group(1) + "\\footnote{{{}}}".format(re.sub(r"<br\s*/>", ", ", tr[1]))
            elif matchobj.group(0).count("|") > 1:
                raise ValueError("invalid translation tag: {}".format(matchobj.group(0)))
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        if r.find("endnote") != -1 and matchobj.group(0).count("|") == 1:
            adict["counter"] += 1
            adict["alist"].append((adict["counter"], matchobj.group(1), matchobj.group(2)))
            return matchobj.group(1) + "$^{{g{}}}$".format(adict["counter"])
        return matchobj.expand(r)

    def keyfn(a):
        a_ = a[0]
        wlist = a_.split()
        if len(wlist) > 1 and wlist[0].startswith("(") or wlist[0] in ("lo", "la", "los", "las", "el", "a", "de"):
            a_ = wlist[1]
        for k, r in SORTDICT.items():
            a_ = a_.replace(k, r)
        return a_.lower()

    for key, replacement in subdict.items():
        rf = partial(replfn, adict, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])

    wordlist.sort(key=keyfn)
    check_duplicates(wordlist)
    with open("_words.txt", "w") as fh:
        for w in wordlist:
            if wordlist.count(w[0]) > 1:
                print("ATT: {}".format(w[0]))
            try:
                print("{0}|{1}|{2}".format(*w), file=fh)
            except Exception:
                print(repr(w))
                raise
    return text, adict["alist"]


def process_replace_html(text):
    """Replace special tags with their html equivalent.
    """
    adict = {
        "counter": 0,
        "alist": []
    }
    wordlist = []
    subdict = OrderedDict([
        # replace quote characters
        (r"“", {"r": r'"', "flags": 0}),
        (r"”", {"r": r'"', "flags": 0}),
        #(r"<(.+)>", {"r": r"\\begin{small}\1\\end{small}", "flags": 0}),
        #(r'\"([^\"]+)\"', {"r": r"\\glqq{}\1\\grqq{}", "flags": 0}),
        # comments
        (r"%.*$", {"r": "", "flags": re.MULTILINE}),
        # replace translation tags
        (r"[\s\[\"]\[([^|]+)\|([^\]]+)\]", {"r": r'<abbr class="translation", title="\1">\2</abbr>', "flags": 0}),
        # do not know if we need it
        (r"[\s\[\"]\{([^|]+)\|([^\}]+)\}", {"r": r"endnote", "flags": 0}),
        # ** is bold
        (r"\*\*([^*]+)\*\*", {"r": r"<b>\1</b>", "flags": 0}),
        #
        (r"__([^_]+)__", {"r": r"\\uline{\1}", "flags": 0}),
        (r"-->", {"r": r"$\\rightarrow$ ", "flags": 0}),
        (r"\.att", {"r": r"\\danger{}", "flags": 0}),
        (r"\.rem", {"r": r"\\eye{}", "flags": 0}),
        (r"\.\.\.", {"r": r"$\\ndots$ ", "flags": 0}),
        (r"//(.+?)//", {"r": r"<i>\1</i>", "flags": 0}),
        (r"\|\|([^|]+)\|\|", {"r": r"\\fbox{\1}", "flags": 0}),
        # headers
        (r"^=([^=]+)=\s*(label{\w+})?\s*$", {"r": r"<h1<\1</h1>", "flags": re.MULTILINE}),
        (r"^-([^-]+)-\s*(label{\w+})?\s*$", {"r": r"<h1>\1</h1>", "flags": re.MULTILINE}),
        (r"^==([^=]+)==\s*(label{\w+})?\s*$", {"r": r"<h2>\1</h2>", "flags": re.MULTILINE}),
        (r"^--([^-]+)--\s*(label{\w+})?\s*$", {"r": r"<h2>\1</h2>", "flags": re.MULTILINE}),
        (r"^---([^-]+)---\s*(label{\w+})?\s*$", {"r": r"<h3>\1</h3>", "flags": re.MULTILINE}),
        # Spiegelstrich
        (r"^-\s+(.*)$", {"r": r"<br/>- \1", "flags": re.MULTILINE}),
        # line breaks
        (r"\\\\", {"r": "<br/>", "flags": 0}),
        # empty lines
        ("^$", {"r": "<br/><!-- --><br/>", "flags": re.MULTILINE}),
        # original page number
        (r"\s*/(\d+)/\s*", {"r": r" ", "flags": 0}),
        # ndots
        (r"\\ndots", {"r": r"&hellip;", "flags": 0}),
        (r"...", {"r": r"&hellip;", "flags": 0}),
        (u'…', {"r": r"&hellip;", "flags": 0}),
        # vskip, phantom
        (r"\\vskip([^\s])", {"r": r"<br/>", "flags": 0}),
        (r"\\phantom\{[^\}]*\}", {"r": r"", "flags": 0}),

        #
        (r"\s*%(\d+)\s*", {"r": r"~\\grammarnote{\1}", "flags": 0}),
        # itemize
        (r"^\\beginitemize", {"r": r"<ul>", "flags": re.MULTILINE}),
        (r"^\\enditemize", {"r": r"</ul>", "flags": re.MULTILINE}),
        (r"^\\beginenum", {"r": r"<ol>", "flags": re.MULTILINE}),
        (r"^\\endenum", {"r": r"</ol>", "flags": re.MULTILINE}),
        (r"^\s*\\item\s+(.*)$", {"r": r"<li>\1</li>", "flags": re.MULTILINE}),
        # italic style
        (r"^\\beginitshape", {"r": r"<i>", "flags": re.MULTILINE}),
        (r"^\\enditshape", {"r": r"</i>", "flags": re.MULTILINE}),
        # quoted
        (r"^\\beginquote", {"r": r'<div class="quote"><i>', "flags": re.MULTILINE}),
        (r"^\\endquote", {"r": r"</i></div>", "flags": re.MULTILINE}),
        # important: this has to be last
        (r"<br/>(?:\s*<br/>)+", {"r": "<br/>", "flags": 0})
    ])

    def replfn(adict, r, matchobj):
        if r.find("translation") != -1:
            if matchobj.group(0).count("|") in [2, 3]:
                tr = matchobj.group(2).split("|")
                if matchobj.group(2).count("|") == 2:
                    try:
                        tr = [item.replace("::", "<br/>") for item in tr]
                    except Exception:
                        print(tr)
                        raise
                return ' <abbr title="{1}">{0}</abbr>'.format(matchobj.group(1), "{}".format(re.sub(r"<br\s*/>", ", ", tr[1])))
                return ' ' + matchobj.group(1) + "\\footnote{{{}}}".format(re.sub(r"<br\s*/>", ", ", tr[1]))
            elif matchobj.group(0).count("|") > 1:
                raise ValueError("invalid translation tag: {}".format(matchobj.group(0)))
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        if r.find("endnote") != -1 and matchobj.group(0).count("|") == 1:
            adict["counter"] += 1
            adict["alist"].append((adict["counter"], matchobj.group(1), matchobj.group(2)))
            return matchobj.group(1) + "$^{{g{}}}$".format(adict["counter"])
        return matchobj.expand(r)

    for key, replacement in subdict.items():
        rf = partial(replfn, adict, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])

    return text


def process_dashes(text):
    """Special handling af dashes indicating verbal speech
    """
    s_in, s_out = 0, 1
    state = s_out
    textlist = text.splitlines()
    textlist.append("\n")
    for index in range(len(textlist)):
        line = textlist[index].strip()
        if line.startswith("-") and not line.endswith("-"):
            # it is the first line in verbal speech
            state = s_in
            if textlist[index - 1].strip() != "":
                # previous line in empty
                textlist[index] = "\\par{}-" + textlist[index][1:]
        if state == s_in:
            # we are in subsequent lines of verbal speech
            if line.endswith("~\\\\"):
                # explicit marked end of verbal speech
                textlist[index] += "\\par"
                state = s_out
            elif line.endswith("\\\\"):
                # explicit marked end of verbal speech
                state = s_out
                textlist[index + 1] = "\\rule{1em}{0pt}" + textlist[index + 1]
            elif textlist[index + 1].strip() == "":
                # next line is empty
                state = s_out
                #textlist[index] += "\\\\"
            else:
                # none of the above
                textlist[index] += " %"
    text = "\n".join(textlist)
    return text


def make_cleanup(args):
    """Read file contents.in.txt, process t and write result to
       contents.out.txt
    """
    maxwidth = 72

    def fmt(text):
        w = textwrap.TextWrapper(width=maxwidth, break_long_words=False)
        buf = []
        for paragraph in text.splitlines():
            buf.append(w.fill(paragraph))
        return textwrap.dedent('\n'.join(p.strip() for p in buf))

    def prepare(text):
        replacementlist = ((r'\(\s+', '('), (u'“', '"'), (u'”', '"'),
                           (' {2,}', ' '), (' +" +', ' "')) #, (u'…', '\\\\ndots'))
        for replacement in replacementlist:
            text = re.sub(replacement[0], replacement[1], text)
        text = re.sub(r"\.(\n?\s*\w)", lambda m: m.group(0).upper(), text, flags=re.U)
        text = re.sub(r"^-\s*([a-z])(.*)", lambda m: "- {}{}".format(m.group(1).upper(), m.group(2)), text, flags=re.M)
        text = re.sub(r"\?\?\s*", "¿", text)
        text = re.sub(r"!!\s*", "¡", text)
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"!\s+([a-z])", lambda m: "! {}".format(m.group(1).upper()), text)
        return text

    with open("contents.in.txt", encoding="utf-8") as fh:
        text = fh.read()

    with open("contents.out.txt", "w") as fh:
        fh.write(fmt(prepare(text)))

    return "output written to contents.out.txt"


def make_dictionary(args):
    with open("_words.txt") as fh:
        wordlist = fh.read().splitlines()
        outlist = []
        firstletterlist = []
        for index, line in enumerate(wordlist):
            line = line.replace("<br/>", "; ")
            wlist = line.split("|")
            wlist[1] = "\\foreignlanguage{{german}}{{{}}}".format(wlist[1])
            esword = wlist[0]
            if esword.startswith("el ") or esword.startswith("la ") or esword.startswith("los ") or esword.startswith("las ") or esword.startswith("a ") or esword.startswith("de "):
                firstletter = esword.split(" ")[1][0]
            else:
                firstletter = esword[0]
            firstletter = SORTDICT.get(firstletter, firstletter)
            firstletter = firstletter.upper()
            if firstletter not in firstletterlist:
                firstletterlist.append(firstletter)
                outlist.append("\\hypertarget{{a{}}}{{\\section*{{{}}}}}".format(len(firstletterlist), firstletter))
            outlist.append("\\textbf{{{0}}}\\enspace--\\enspace{{{1}}}\\hfill~\\\\".format(*wlist))
    link = " - ".join("\\hyperlink{{a{}}}{{{}}}".format(i, a) for i, a in enumerate(firstletterlist))
    with open("ddictionary.tex", "w", encoding="utf-8") as fh:
        fh.write(r"""
            {link}

            {d}
            """.format(d="\n".join(outlist), link=link if args.with_link else ""))
    return "output writen to ddictionary.tex"


def analyze(text):
    outlist = []
    linelist = text.splitlines()
    for lineno, line in enumerate(linelist):
        if line.strip().startswith(".g"):
            outlist.append("\\switchcolumn[1]")
        elif line.strip().startswith(".e"):
            outlist.append("\\switchcolumn[0]*")
        else:
            outlist.append(line)
    return "\n".join(outlist)


def process_tex(args):
    """Read contents.txt, process it and write result to content.tex"""
    with open("contents.txt", "r", encoding="utf-8") as fh:
        text = fh.read()
    text, alist = process_replace_tex(text)
    text = process_dashes(text)
    text = analyze(text)
    with open("contents.tex", "w", encoding="utf-8") as fh:
        fh.write(text)
    with open("book_template.tex", "r") as fh:
        template = fh.read()
    rdict = {"author": "---", "title": "---"}
    for search in rdict:
        mo = re.search(f"^%\\s*{search}:\\s*(.*)", text, re.M)
        if mo is None:
            print(f"NO {search} FOUND")
            continue
        rdict[search] = mo.group(1)
        mo = re.search(f"^\\\\{search}{{}}", template, re.M)
        template = re.sub(f"\\\\{search}{{}}", f"\\\\{search}{{{rdict[search]}}}", template, re.M)
    with open("book.tex", "w", encoding="utf-8") as fh:
        fh.write(template)
        print("book.tex written")
    return "output written to contents.tex"


def process_ebook(args):
    from ebooklib import epub
    import uuid

    with open("contents.txt", "r", encoding="utf-8") as fh:
        text = fh.read()
    text = process_replace_html(text)

    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid1()))
    title = args.config.get("title", "No title")
    book.set_title(title)
    book.set_language('es')
    author = args.config.get("author", "No author")
    book.add_author(author)
    book.add_metadata('DC', 'description', "This is my private version of '{}' from {}".format(title, author))

    # defube style
    style = 'abbr {text-decoration: underline; color: blue}'
    default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)
    book.add_item(default_css)

    toclist = []
    textlist = text.split("\\clearpage")
    for index, chapter in enumerate(textlist):
        chaptertitle = 'Capítulo {}'.format(index + 1) if args.config.get("chapterlist", None) is None else args.config["chapterlist"][index]
        ebookchapter = epub.EpubHtml(title=chaptertitle,
                   file_name='chapter{:02}.xhtml'.format(index + 1),
                   lang='es')
        ebookchapter.set_content(chapter)
        ebookchapter.add_item(default_css)
        toclist.append(ebookchapter)
        book.add_item(ebookchapter)

    book.toc = (
        tuple(toclist)
    )

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # create spine
    toclist.insert(0, 'nav')
    book.spine = tuple(toclist)

    # create epub file
    epub.write_epub('book.epub', book, {})

    return "output written to book.epub"


if __name__ == '__main__':
    choicesdict = {
        "tex": process_tex,
        "ebook": process_ebook,
        "dictionary": make_dictionary,
        "cleanup": make_cleanup
    }
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=choicesdict.keys())
    parser.add_argument("--with-link", action="store_true", help="create links in dictionary")
    parser.add_argument("--configfile", "-c", action="store", help="configuration file", dest="configfile")
    args = parser.parse_args()
    args.config = {} if args.configfile is None else json.load(open(args.configfile))
    result = choicesdict[args.action](args)
    print(result)

import argparse
import sys
import re
import logging
import textwrap
from collections import OrderedDict
from functools import partial


infile = "contents.txt"
outfile = "book.html"
templatefile = "book_template.html"

SORTDICT = {'á': 'a', chr(195): 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}


def process():
    with open(infile, "r", encoding="utf-8") as fh:
        text = fh.read()
    text = process_replace(text)
    return text


def process_replace(text):
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
        # vskip, phantom
        (r"\\vskip([^\s])", {"r": r"<br/>", "flags": 0}),
        (r"\\phantom\{[^\}]*\}", {"r": r"", "flags": 0}),

        #
        (r"\s*%(\d+)\s*", {"r": r"~\\grammarnote{\1}", "flags": 0}),
        # itemize
        (r"^\.beginitemize", {"r": r"<ul>", "flags": re.MULTILINE}),
        (r"^\.enditemize", {"r": r"</ul>", "flags": re.MULTILINE}),
        (r"^\s*\\item\s+(.*)$", {"r": r"<li>\1</li>", "flags": re.MULTILINE}),
        # italic style
        (r"^\.beginitshape", {"r": r"<i>", "flags": re.MULTILINE}),
        (r"^\.enditshape", {"r": r"</i>", "flags": re.MULTILINE}),
        # quoted
        (r"^\.beginquote", {"r": r"<q>", "flags": re.MULTILINE}),
        (r"^\.endquote", {"r": r"</q>", "flags": re.MULTILINE}),
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

    def keyfn(a):
        a_ = a[0]
        wlist = a_.split()
        if len(wlist) > 1 and wlist[0].startswith("(") or wlist[0] in ("lo", "la", "los", "las", "el", "a", "de"):
            a_ = wlist[1]
        for k, r in SORTDICT.items():
            a_ = a_.replace(k, r)
        return a_

    for key, replacement in subdict.items():
        rf = partial(replfn, adict, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])

    return text


def make_ebook(text):
    from ebooklib import epub

    book = epub.EpubBook()
    book.set_identifier('achkoe123456')
    book.set_title('Como agua para chocolate')
    book.set_language('es')
    book.add_author('Laura Esquivel')
    book.add_metadata('DC', 'description', 'This is my private version of "Como agua para chocolate" from Laura Esquivel')

    toclist = []
    textlist = text.split("\\clearpage")
    for index, chapter in enumerate(textlist):
        ebookchapter = epub.EpubHtml(title='Capítulo {}'.format(index + 1),
                   file_name='chapter{:02}.xhtml'.format(index + 1),
                   lang='es')
        ebookchapter.set_content(chapter)
        toclist.append(ebookchapter)
        book.add_item(ebookchapter)

    style = 'abbr {text-decoration: underline;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

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

    print("Written to book.epub")


if __name__ == '__main__':
    with open(templatefile, "r", encoding="utf-8") as fh:
        template = fh.read()
    make_ebook(process())
#    with open(outfile, "w", encoding="utf-8") as fh:
 #       fh.write(template.format(**tdict))

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Postprocessor for LaTex."""
from __future__ import print_function
import argparse
import sys
import re
import logging
import textwrap
import codecs
from collections import OrderedDict
from functools import partial
import unittest

logging.basicConfig(level=logging.INFO, format="%(lineno)d: %(msg)s")

PAIRSSTART = ur"""
\beforeeledchapter
\begin{pairs}
"""

PAIRSSTOP = ur"""
\end{pairs}
\Columns
"""

CHAPTERSTART = ur"""
    \begin{{{side}}}
    \beginnumbering
    \pstart
    {line}
    \pend
"""

CHAPTERSTOP = ur"""
    \endnumbering
    \end{{{side}}}
"""

SIDE = ["Leftside", "Rightside"]

ESPANIOL, GERMAN = 0, 1


def analyze(args, linelist):
    for lineno, line in enumerate(linelist):
        if line.strip().startswith(".g"):
            print("\\switchcolumn[1]", file=args.outfile)
        elif line.strip().startswith(".begintwocol"):
            print("\\begin{paracol}{2}", file=args.outfile)
        elif line.strip().startswith(".endtwocol"):
            print("\\end{paracol}", file=args.outfile)
        elif line.strip().startswith(".e"):
            print("\\switchcolumn[0]*", file=args.outfile)
        else:
            print(line, file=args.outfile)


def process_environment(text, ddict):
    inenvironment = False
    linelist = text.splitlines()
    for index, line in enumerate(linelist):
        if line.strip().startswith(ddict["b"]):
            inenvironment = True
            linelist[index] = ddict["br"].format(line.strip()[3:].strip())
        elif line.strip().startswith(ddict["e"]) and inenvironment:
            inenvironment = False
            linelist[index] = ddict["er"]
        elif inenvironment:
            linelist[index] = re.sub("<([^>]*)>", r"\item[\1]", line)
    return "\n".join(linelist)


envdict = {
    "description": {
        "b": ":bd",
        "e": ":ed",
        "br": r"{{"
              r"\definecolor{{light}}{{gray}}{{0.9}}"
              r"\colorbox{{light}}{{"
              r"\begin{{minipage}}{{0.45\textwidth}}"
              r"{}"
              r"\begin{{description}}[font=\normalfont, itemsep=0ex, parsep=0ex]",
        "er": "\end{description}\end{minipage}}}"
    },
    "sabiasque": {
        "b": ":bs",
        "e": ":es",
        "br": u"{{"
              u"\\definecolor{{light}}{{gray}}{{0.95}}"
              u"\\colorbox{{light}}{{"
              u"\\begin{{minipage}}{{0.45\\textwidth}}"
              u"\\hrule\\vskip0.5em"
              u"{}\\\\",
        "er": u"\\vskip0.5em\\hrule\\end{minipage}}}"
    }
}


def process(args):
    with codecs.open(args.infile, 'r', "utf-8") as fh:
        text = fh.read()
    text = process_environment(text, envdict["description"])
    text = process_environment(text, envdict["sabiasque"])
    text = process_dashes(process_replace(text))
    # text = process_replace(text)
    linelist = text.splitlines()
    analyze(args, linelist)


def process_replace(text):
    subdict = OrderedDict([
            (u"“", {"r": ur'"', "flags": 0}),
            (u"”", {"r": ur'"', "flags": 0}),
            (u"[\s\[\"]\[([^|]+)\|([^\]]+)\]", {"r": ur"\2\\footnote{\1}", "flags": 0}),
            (u"\*\*([^*]+)\*\*", {"r": ur"\\textbf{\1}", "flags": 0}),
            (u"__([^_]+)__", {"r": ur"\\uline{\1}", "flags": 0}),
            (u'\"([^\"]+)\"', {"r": ur"\\glqq{}\1\\grqq{}", "flags": 0}),
            (u"-->", {"r": ur"$\\rightarrow$ ", "flags": 0}),
            (u"\.att", {"r": ur"\\danger{}", "flags": 0}),
            (u"\.rem", {"r": ur"\\eye{}", "flags": 0}),
            (u"\.\.\.", {"r": ur"$\\ldots$ ", "flags": 0}),
            (u"//(.+?)//", {"r": ur"\\textit{\1}", "flags": 0}),
            (u"\|\|([^|]+)\|\|", {"r": ur"\\fbox{\1}", "flags": 0}),
            (u"<(.+)>", {"r": ur"\\begin{small}\1\\end{small}", "flags": 0}),
            (u"^=([^=]+)=\s*(label{\w+})?\s*$", {"r": ur"\\section{\1}", "flags": re.MULTILINE}),
            (u"^-([^-]+)-\s*(label{\w+})?\s*$", {"r": ur"\\section*{\1}", "flags": re.MULTILINE}),
            (u"^==([^=]+)==\s*(label{\w+})?\s*$", {"r": ur"\\subsection{\1}", "flags": re.MULTILINE}),
            (u"^--([^-]+)--\s*(label{\w+})?\s*$", {"r": ur"\\subsection*{\1}", "flags": re.MULTILINE}),
            (u"^---([^-]+)---\s*(label{\w+})?\s*$", {"r": ur"\\subsubsection*{\1}", "flags": re.MULTILINE}),
            (u"\s*/(\d+)/\s*", {"r": ur"~\\sidenote{\1}", "flags": 0})])

    _subdict = {
        u"“": {"r": ur'"', "flags": 0},
        u"”": {"r": ur'"', "flags": 0},
        u"\*\*([^*]+)\*\*": {"r": ur"\\textbf{\1}", "flags": 0},
        u"__([^_]+)__": {"r": ur"\\uline{\1}", "flags": 0},
        u'\"([^\"]+)\"': {"r": ur"\\glqq{}\1\\grqq{}", "flags": 0},
        u"-->": {"r": ur"$\\rightarrow$ ", "flags": 0},
        u"\.att": {"r": ur"\\danger{}", "flags": 0},
        u"\.rem": {"r": ur"\\eye{}", "flags": 0},
        u"\.\.\.": {"r": ur"$\\ldots$ ", "flags": 0},
        u"//(.+?)//": {"r": ur"\\textit{\1}", "flags": 0},
        u"\|\|([^|]+)\|\|": {"r": ur"\\fbox{\1}", "flags": 0},
        u"<(.+)>": {"r": ur"\\begin{small}\1\\end{small}", "flags": 0},
        u"^=([^=]+)=\s*(label{\w+})?\s*$": {"r": ur"\\section{\1}", "flags": re.MULTILINE},
        u"^-([^-]+)-\s*(label{\w+})?\s*$": {"r": ur"\\section*{\1}", "flags": re.MULTILINE},
        u"^==([^=]+)==\s*(label{\w+})?\s*$": {"r": ur"\\subsection{\1}", "flags": re.MULTILINE},
        u"^--([^-]+)--\s*(label{\w+})?\s*$": {"r": ur"\\subsection*{\1}", "flags": re.MULTILINE},
        u"^---([^-]+)---\s*(label{\w+})?\s*$": {"r": ur"\\subsubsection*{\1}", "flags": re.MULTILINE},
        u"[\s\[\"]\[([^|]+)\|([^\]]+)\]": {"r": ur"\2\\footnote{\1}", "flags": 0},
        u"\s*/(\d+)/\s*": {"r": ur"~\\sidenote{\1}", "flags": 0}
    }

    def replfn(r, matchobj):
        if r.find("footnote") != -1 and matchobj.group(2).count("|") == 2:
            tr = matchobj.group(2).split("|")
            try:
                print("{1}|{0}|{2}".format(tr[0].encode('utf-8'), tr[1].encode('utf-8'), tr[2].encode('utf-8')))
            except:
                print(tr)
                raise
            return ' ' + matchobj.group(1) + u"\\footnote{{{}}}".format(tr[1])
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        return matchobj.expand(r)

    for key, replacement in subdict.iteritems():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])
    return text


def process_dashes(text):
    return re.sub("([^\\\\])\n-", "\\1 \\\\\\\\\n-", re.sub("^(-.*)$", r"\1 \\\\", text, flags=re.M), flags=re.M)


def _cleanup(args):
    def main(text):
        def fn_capital_after_fullstop(mo):
            return u". {}".format(mo.group(1).upper())

        def fn_capital_after_dash(mo):
            return u"- {}{}".format(mo.group(1).upper(), mo.group(2))

        regexp_fs = re.compile(r"\.\s+([a-z])")
        regexp_cm = re.compile(r"\,\s+")
        regexp_qm = re.compile(r"\?\?\s*")
        regexp_ex = re.compile(r"!!\s*")
        regexp_ld = re.compile(r"…")
        regexp_sp = re.compile(r"[ ]+")
        regexp_nl = re.compile(r"\.(?!\n)")
        regexp_ds = re.compile(r"^-\s*([a-z])(.*)", re.M)

        text = regexp_ds.sub(fn_capital_after_dash, text)
        text = regexp_fs.sub(fn_capital_after_fullstop, text)
        text = regexp_cm.sub(", ", text)
        text = regexp_qm.sub(u"¿", text)
        text = regexp_ex.sub(u"¡", text)
        text = regexp_ld.sub(u"\\ldots", text)
        text = regexp_sp.sub(u" ", text)
        text = regexp_nl.sub(u".\n", text)

        return text

    with codecs.open(args.infile, encoding="utf-8") as fh:
        text = fh.read()
    args.outfile.write(main(text))


def cleanup(args):
    maxwidth = 72

    def fmt(text):
        w = textwrap.TextWrapper(width=maxwidth, break_long_words=False)
        buf = []
        for paragraph in text.splitlines():
            buf.append(w.fill(paragraph))
        return textwrap.dedent('\n'.join(p.strip() for p in buf))

    def prepare(text):
        replacementlist = (('\(\s+', '('), (u'“', '"'), (u'”', '"'), (u'“', '"')
                           (' {2,}', ' '), (' +" +', ' "'), (u'…', '\\ldots'))
        for replacement in replacementlist:
            text = re.sub(replacement[0], replacement[1], text)
        text = re.sub(r"\.(\n?\s*\w)", lambda m: m.group(0).upper(), text, flags=re.U)
        text = re.sub(r"\?\?\s*", u"¿", text)
        text = re.sub(r"!!\s*", u"¡", text)
        text = re.sub(r"\s+,", ",", text)
        return text

    with codecs.open(args.infile, encoding="utf-8") as fh:
        text = fh.read()

    args.outfile.write(fmt(prepare(text)))


class Test(unittest.TestCase):
    def setUp(self):
        refmarker = "%%REFERENCE\n"
        with open("sample.txt") as fh:
            text = fh.read()
        pos = text.find(refmarker)
        self.testpattern = text[:pos]
        pos += len(refmarker)
        self.refpattern = text[pos:]

    def __test_process_replace(self):
        #print(self.testpattern)
        self.testpattern = process_replace(self.testpattern)
        #print(self.testpattern)
        #return
        testlist = self.testpattern.splitlines()
        reflist = self.refpattern.splitlines()
        # print(reflist)
        #self.assertEqual(len(testlist), len(reflist))
        print()
        index = 1
        for refline, testline in zip(reflist, testlist):
            print("r{:05}: {}".format(index, repr(refline)))
            print("a{:05}: {}".format(index, repr(testline)))
            self.assertEqual(testline, refline)
            index += 1

    def test_process_dashes(self):
        self.testpattern = process_dashes(process_replace(self.testpattern))
        testlist = self.testpattern.splitlines()
        reflist = self.refpattern.splitlines()
        print()
        index = 1
        for refline, testline in zip(reflist, testlist):
            print("r{:05}: {}".format(index, repr(refline)))
            print("a{:05}: {}".format(index, repr(testline)))
            self.assertEqual(testline, refline, "\n{!r}\n!=\n{!r}".format(testline, refline))
            index += 1

    def test_pattern_dashes(self):
        testpattern = "1234\n-abc\n12345"
        resultpattern = process_dashes(testpattern)
        print(resultpattern)
        self.assertEqual(resultpattern, "1234 \\\\\n-abc \\\\\n12345")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("infile", help="input file")
    parser.add_argument("--outfile", "-o", help="output file")
    parser.add_argument("--cleanup", "-c", action="store_true", help="write dirty input file to clean output file")
    args = parser.parse_args()
    if args.outfile is None:
        args.outfile = sys.stdout
    else:
        args.outfile = codecs.open(args.outfile, "wb", encoding="utf-8")
    if args.cleanup:
        cleanup(args)
    else:
        process(args)
    print("Wrote output to {}".format(args.outfile.name))

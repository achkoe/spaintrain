#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Postprocessor for LaTex to."""
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

PAIRSSTART = u"""
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



def process(args):
    with codecs.open(args.infile, 'r', "utf-8") as fh:
        text = fh.read()
    #text = process_environment(text, envdict["description"])
    #text = process_environment(text, envdict["sabiasque"])
    text = process_dashes(process_replace(text))
    # text = process_replace(text)
    linelist = text.splitlines()
    analyze(args, linelist)


def process_replace(text):
    wordlist = []
    subdict = OrderedDict([
            (ur"“", {"r": ur'"', "flags": 0}),
            (ur"”", {"r": ur'"', "flags": 0}),
            (ur"[\s\[\"]\[([^|]+)\|([^\]]+)\]", {"r": ur"\2\\footnote{\1}", "flags": 0}),
            (ur"\*\*([^*]+)\*\*", {"r": ur"\\textbf{\1}", "flags": 0}),
            (ur"__([^_]+)__", {"r": ur"\\uline{\1}", "flags": 0}),
            (ur'\"([^\"]+)\"', {"r": ur"\\glqq{}\1\\grqq{}", "flags": 0}),
            (ur"-->", {"r": ur"$\\rightarrow$ ", "flags": 0}),
            (ur"\.att", {"r": ur"\\danger{}", "flags": 0}),
            (ur"\.rem", {"r": ur"\\eye{}", "flags": 0}),
            (ur"\.\.\.", {"r": ur"$\\ndots$ ", "flags": 0}),
            (ur"//(.+?)//", {"r": ur"\\textit{\1}", "flags": 0}),
            (ur"\|\|([^|]+)\|\|", {"r": ur"\\fbox{\1}", "flags": 0}),
            (ur"<(.+)>", {"r": ur"\\begin{small}\1\\end{small}", "flags": 0}),
            (ur"^=([^=]+)=\s*(label{\w+})?\s*$", {"r": ur"\\section{\1}", "flags": re.MULTILINE}),
            (ur"^-([^-]+)-\s*(label{\w+})?\s*$", {"r": ur"\\section*{\1}", "flags": re.MULTILINE}),
            (ur"^==([^=]+)==\s*(label{\w+})?\s*$", {"r": ur"\\subsection{\1}", "flags": re.MULTILINE}),
            (ur"^--([^-]+)--\s*(label{\w+})?\s*$", {"r": ur"\\subsection*{\1}", "flags": re.MULTILINE}),
            (ur"^---([^-]+)---\s*(label{\w+})?\s*$", {"r": ur"\\subsubsection*{\1}", "flags": re.MULTILINE}),
            (ur"\s*/(\d+)/\s*", {"r": ur"~\\sidenote{\1}", "flags": 0})])

    def replfn(r, matchobj):
        if r.find("footnote") != -1 and matchobj.group(2).count("|") in [2, 3]:
            tr = matchobj.group(2).split("|")
            if matchobj.group(2).count("|") == 2:
                try:
                    #wordlist.append("{1}|{0}|{2}".format(tr[0].encode('utf-8'), tr[1].encode('utf-8'), tr[2].encode('utf-8')))
                    tr = [item.replace("::", "<br/>") for item in tr]
                    wordlist.append((tr[0].strip().encode('utf-8'), tr[1].strip().encode('utf-8'), tr[2].strip().encode('utf-8')))
                    #print("{1}|{0}|{2}".format(tr[0].encode('utf-8'), tr[1].encode('utf-8'), tr[2].encode('utf-8')))
                except Exception:
                    print(tr)
                    raise
            return ' ' + matchobj.group(1) + u"\\footnote{{{}}}".format(re.sub(r"<br\s*/>", ", ", tr[1]))
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        return matchobj.expand(r)

    for key, replacement in subdict.iteritems():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])

    def cmpfn(a, b):
        a_ = a[0]
        b_ = b[0]
        wlist = a_.split()
        if len(wlist) > 1 and wlist[0].startswith("(") or wlist[0] in ("lo", "la", "los", "las", "el"):
            a_ = wlist[1]
        wlist = b_.split()
        if len(wlist) > 1 and wlist[0].startswith("(") or wlist[0] in ("lo", "la", "los", "las", "el"):
            b_ = wlist[1]
        return cmp(a_.lower(), b_.lower())

    wordlist.sort(cmp=cmpfn)
    with open("_words.txt", "w") as fh:
        for w in wordlist:
            if wordlist.count(w[0]) > 1:
                print("ATT: {}".format(w[0]))
            print("{0}|{1}|{2}".format(*w), file=fh)
        return text


def process_dashes(text):
    """
    First append to all lines starting with "-" [pattern matching "^(-.*)$"] the characters "\\"
    Second substitute all line pairs where first line not ends with "\\" and second line starts with '-'
    with stgh
    """
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
        replacementlist = (('\(\s+', '('), (u'“', '"'), (u'”', '"'),
                           (' {2,}', ' '), (' +" +', ' "'), (u'…', '\\ldots'))
        for replacement in replacementlist:
            text = re.sub(replacement[0], replacement[1], text)
        text = re.sub(r"\.(\n?\s*\w)", lambda m: m.group(0).upper(), text, flags=re.U)
        text = re.sub(r"^-\s*([a-z])(.*)", lambda m: u"- {}{}".format(m.group(1).upper(), m.group(2)), text, flags=re.M)
        text = re.sub(r"\?\?\s*", u"¿", text)
        text = re.sub(r"!!\s*", u"¡", text)
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"!\s+([a-z])", lambda m: u"! {}".format(m.group(1).upper()), text)
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

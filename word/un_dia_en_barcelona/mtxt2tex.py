"""Postprocessor for LaTex."""
from __future__ import print_function
import argparse
import sys
import os
import re
import logging
import codecs
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
        elif line.strip().startswith(".e"):
            print("\\switchcolumn[0]*", file=args.outfile)
        else:
            print(line, file=args.outfile)


def process(args):
    with codecs.open(args.infile, 'r', "utf-8") as fh:
        text = fh.read()
    text = process_dashes(process_replace(text))
    # text = process_replace(text)
    linelist = text.splitlines()
    analyze(args, linelist)


def process_replace(text):
    subdict = {
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
        u"\s\[([^|]+)\|([^\]]+)\]": {"r": ur"\1\\footnote{\2}", "flags": 0}
    }

    def replfn(r, matchobj):
        if r.find("footnote") != -1 and matchobj.group(2).count("|") == 2:
            tr = matchobj.group(2).split("|")
            print("{}|{}|{}".format(tr[0].encode('utf-8'), tr[1].encode('utf-8'), tr[2]))
            return ' ' + matchobj.group(1) + u"\\footnote{{{}}}".format(tr[0])
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        return matchobj.expand(r)

    for key, replacement in subdict.iteritems():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])
    return text


def process_dashes(text):
    return re.sub("([^\\\\])\n-", "\\1 \\\\\\\\\n-", re.sub("^(-.*)$", r"\1 \\\\", text, flags=re.M), flags=re.M)


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
    args = parser.parse_args()
    if args.outfile is None:
        args.outfile = sys.stdout
    else:
        args.outfile = codecs.open(args.outfile, "wb", encoding="utf-8")
    process(args)
    print("Wrote output to {}".format(args.outfile.name))

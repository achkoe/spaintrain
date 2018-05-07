"""Postprocessor for LaTex."""
from __future__ import print_function
import argparse
import sys
import os
import re
import logging
import codecs
from functools import partial

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
    subdict = {
        u"\*\*([^*]+)\*\*": {"r": ur"\\textbf{\1}", "flags": 0},
        u"__([^_]+)__":     {"r": ur"\\uline{\1}", "flags": 0},
        u'\"([^\"]+)\"':    {"r": ur"\\glqq{}\1\\grqq{}", "flags": 0},
        u"-->":             {"r": ur"$\\rightarrow$ ", "flags": 0},
        u"\.att":           {"r": ur"\\danger{}", "flags": 0},
        u"\.rem":           {"r": ur"\\eye{}", "flags": 0},
        u"\.\.\.":          {"r": ur"$\\ldots$ ", "flags": 0},
        u"//(.+?)//":     {"r": ur"\\textit{\1}", "flags": 0},
        u"\|\|([^|]+)\|\|": {"r": ur"\\fbox{\1}", "flags": 0},
        u"<(.+)>": {"r": ur"\\begin{small}\1\\end{small}", "flags": 0},
        u"^=([^=]+)=\s*(label{\w+})?\s*$":     {"r": ur"\\section{\1}", "flags": re.MULTILINE},
        u"^-([^-]+)-\s*(label{\w+})?\s*$":     {"r": ur"\\section*{\1}", "flags": re.MULTILINE},
        u"^==([^=]+)==\s*(label{\w+})?\s*$":   {"r": ur"\\subsection{\1}", "flags": re.MULTILINE},
        u"^--([^-]+)--\s*(label{\w+})?\s*$":   {"r": ur"\\subsection*{\1}", "flags": re.MULTILINE},
        u"^---([^-]+)---\s*(label{\w+})?\s*$":   {"r": ur"\\subsubsection*{\1}", "flags": re.MULTILINE},
        u"\[([^|]+)\|([^\]]+)\]": {"r": ur"\1\\footnote{\2}", "flags": 0}
    }
    def replfn(r, matchobj):
        if r.find("footnote") != -1 and matchobj.group(2).count("|") == 2:
            tr = matchobj.group(2).split("|")
            print("{}|{}|{}".format(tr[0].encode('utf-8'), tr[1].encode('utf-8'), tr[2]))
            return matchobj.group(1) + u"\\footnote{{{}}}".format(tr[0])
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            #print( matchobj.expand(r) + "\\" + matchobj.group(2))
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        return matchobj.expand(r)

    with codecs.open(args.infile, 'r', "utf-8") as fh:
        text = fh.read()
    for key, replacement in subdict.iteritems():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])
    #print(text)
    linelist = text.splitlines()
    analyze(args, linelist)


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

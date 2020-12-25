#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Postprocessor for text to LaTex."""
import argparse
import sys
import re
import logging
import textwrap
from collections import OrderedDict
from functools import partial
import unittest

logging.basicConfig(level=logging.INFO, format="%(lineno)d: %(msg)s")

PAIRSSTART = """
\beforeeledchapter
\begin{pairs}
"""

PAIRSSTOP = r"""
\end{pairs}
\Columns
"""

CHAPTERSTART = r"""
    \begin{{{side}}}
    \beginnumbering
    \pstart
    {line}
    \pend
"""

CHAPTERSTOP = r"""
    \endnumbering
    \end{{{side}}}
"""

SIDE = ["Leftside", "Rightside"]

ESPANIOL, GERMAN = 0, 1

SORTDICT = {'á': 'a', chr(195): 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}


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


def process(args):
    with open(args.infile, "r", encoding="utf-8") as fh:
        text = fh.read()
    text, alist = process_replace(text)
    text = process_dashes(text)
    linelist = text.splitlines()
    analyze(args, linelist)
    for item in alist:
        print("\\paragraph{{g{0}: {1}}}~\\\\{2}\\\\".format(*item), file=args.outfile)


def check_duplicates(wordlist):
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


def process_replace(text):
    adict = {
        "counter": 0,
        "alist": []
    }
    wordlist = []
    subdict = OrderedDict([
        (r"“", {"r": r'"', "flags": 0}),
        (r"”", {"r": r'"', "flags": 0}),
        (r"[\s\[\"]\[([^|]+)\|([^\]]+)\]", {"r": r"\2\\footnote{\1}", "flags": 0}),

        (r"[\s\[\"]\{([^|]+)\|([^\}]+)\}", {"r": r"endnote", "flags": 0}),

        (r"\*\*([^*]+)\*\*", {"r": r"\\textbf{\1}", "flags": 0}),
        (r"__([^_]+)__", {"r": r"\\uline{\1}", "flags": 0}),
        (r'\"([^\"]+)\"', {"r": r"\\glqq{}\1\\grqq{}", "flags": 0}),
        (r"-->", {"r": r"$\\rightarrow$ ", "flags": 0}),
        (r"\.att", {"r": r"\\danger{}", "flags": 0}),
        (r"\.rem", {"r": r"\\eye{}", "flags": 0}),
        (r"\.\.\.", {"r": r"$\\ndots$ ", "flags": 0}),
        (r"//(.+?)//", {"r": r"\\textit{\1}", "flags": 0}),
        (r"\|\|([^|]+)\|\|", {"r": r"\\fbox{\1}", "flags": 0}),
        (r"<(.+)>", {"r": r"\\begin{small}\1\\end{small}", "flags": 0}),
        (r"^=([^=]+)=\s*(label{\w+})?\s*$", {"r": r"\\section{\1}", "flags": re.MULTILINE}),
        (r"^-([^-]+)-\s*(label{\w+})?\s*$", {"r": r"\\section*{\1}", "flags": re.MULTILINE}),
        (r"^==([^=]+)==\s*(label{\w+})?\s*$", {"r": r"\\subsection{\1}", "flags": re.MULTILINE}),
        (r"^--([^-]+)--\s*(label{\w+})?\s*$", {"r": r"\\subsection*{\1}", "flags": re.MULTILINE}),
        (r"^---([^-]+)---\s*(label{\w+})?\s*$", {"r": r"\\subsubsection*{\1}", "flags": re.MULTILINE}),
        (r"\s*/(\d+)/\s*", {"r": r"~\\sidenote{\1}", "flags": 0}),
        (r"\s*%(\d+)\s*", {"r": r"~\\grammarnote{\1}", "flags": 0}),
        (r"^\.beginitemize", {"r": r"\\begin{compactitem}", "flags": re.MULTILINE}),
        (r"^\.enditemize", {"r": r"\\end{compactitem}", "flags": re.MULTILINE}),
        (r"^\.beginenum", {"r": r"\\begin{compactenum}", "flags": re.MULTILINE}),
        (r"^\.endenum", {"r": r"\\end{compactenum}", "flags": re.MULTILINE}),
        (r"^\.beginitshape", {"r": r"\\begin{itshape}", "flags": re.MULTILINE}),
        (r"^\.enditshape", {"r": r"\\end{itshape}", "flags": re.MULTILINE}),
        (r"^\.beginquote", {"r": r"\\begin{quote}", "flags": re.MULTILINE}),
        (r"^\.endquote", {"r": r"\\end{quote}", "flags": re.MULTILINE}),
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
        return a_

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


def process_dashes(text):
    s_in, s_out = 0, 1
    state = s_out
    textlist = text.splitlines()
    textlist.append("\n")
    for index in range(len(textlist)):
        line = textlist[index].strip()
        if line.startswith("-") and not line.endswith("-"):
            state = s_in
            if textlist[index - 1].strip() != "":
                textlist[index] = "\\\\" + textlist[index]
        if state == s_in:
            if line.endswith("~\\\\"):
                textlist[index] += "\\par"
                state = s_out
            elif line.endswith("\\\\"):
                state = s_out
                textlist[index + 1] = "\\rule{1em}{0pt}" + textlist[index + 1]
            elif textlist[index + 1].strip() == "":
                state = s_out
                textlist[index] += "\\\\"
            else:
                textlist[index] += " %"
    return "\n".join(textlist)


def cleanup(args):
    maxwidth = 72

    def fmt(text):
        w = textwrap.TextWrapper(width=maxwidth, break_long_words=False)
        buf = []
        for paragraph in text.splitlines():
            buf.append(w.fill(paragraph))
        return textwrap.dedent('\n'.join(p.strip() for p in buf))

    def prepare(text):
        replacementlist = ((r'\(\s+', '('), (u'“', '"'), (u'”', '"'),
                           (' {2,}', ' '), (' +" +', ' "'), (u'…', '\\\\ndots'))
        for replacement in replacementlist:
            text = re.sub(replacement[0], replacement[1], text)
        text = re.sub(r"\.(\n?\s*\w)", lambda m: m.group(0).upper(), text, flags=re.U)
        text = re.sub(r"^-\s*([a-z])(.*)", lambda m: "- {}{}".format(m.group(1).upper(), m.group(2)), text, flags=re.M)
        text = re.sub(r"\?\?\s*", "¿", text)
        text = re.sub(r"!!\s*", "¡", text)
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"!\s+([a-z])", lambda m: "! {}".format(m.group(1).upper()), text)
        return text

    with open(args.infile, encoding="utf-8") as fh:
        text = fh.read()

    args.outfile.write(fmt(prepare(text)))


def make_dictionary(withlink=True):
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
            """.format(d="\n".join(outlist), link=link if withlink else ""))
    pass


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
        args.outfile = open(args.outfile, "w", encoding="utf-8")
    if args.cleanup:
        cleanup(args)
    else:
        process(args)
    print("Wrote output to {}".format(args.outfile.name))

# -*- coding: utf-8 -*-
from collections import OrderedDict
import re
from functools import partial
import argparse


def process_table(linelist, transpose=False):
    itemlist = []
    tablecols = -1
    # split lines containing & into list
    for line in linelist:
        if line.strip().startswith('\\hline'):
            itemlist.append(line)
        else:
            itemlist.append(line.rstrip(' \\').split('&'))
            if tablecols != -1 and len(itemlist[-1]) != tablecols:
                raise Exception("table cols")
            else:
                tablecols = len(itemlist[-1])

    # transpose if requested
    if transpose:
        titemlist = []
        [titemlist.append([''] * len([item for item in itemlist if isinstance(item, list)])) for _ in range(tablecols)]
        colindex = 0
        for line in itemlist:
            if not isinstance(line, list):
                continue
            for rowindex, item in enumerate(line):
                titemlist[rowindex][colindex] = item
            colindex += 1
        tablecols = colindex
        itemlist = titemlist

    # prepare collenlist
    collenlist = [0] * tablecols
    # strip blanks from every list item in itemlist
    # and determine maximum length of each column
    for index, item in enumerate(itemlist):
        if isinstance(item, list):
            itemlist[index] = [t.strip(' ') for t in item]
            collenlist = [max(len(t), c) for t, c in zip(itemlist[index], collenlist)]
    print (collenlist)

    # fill each column
    for index, item in enumerate(itemlist):
        if isinstance(item, list):
            itemlist[index] = ["{{:<{}}}".format(c).format(t) for t, c in zip(item, collenlist)]
    # join itemlist:
    for index, item in enumerate(itemlist):
        if isinstance(item, list):
            item[-1] = item[-1] + " \\\\"
            itemlist[index] = ' & '. join(item)
    return '\n'.join(itemlist)


def prepocess_table(text, transpose=False):
    OUTTABLE, INTABLE = 0, 1
    mode = OUTTABLE
    textlist = []
    tablelist = []
    for line in text.splitlines():
        if line.strip().startswith(r"\begin{tabular}"):
            textlist.append(line)
            mode = INTABLE
        elif line.strip().startswith(r"\end{tabular}"):
            textlist.append(process_table(tablelist, transpose))
            textlist.append(line)
            mode = OUTTABLE
            tablelist = []
        elif mode == INTABLE:
            tablelist.append(line)
        else:
            textlist.append(line)
    return '\n'.join(textlist)


def prepocess_replacements(text):
    subdict = OrderedDict([
            (r"\*\*([^*]+)\*\*", {"r": r"\\textbf{\1}", "flags": 0}),
            ("__([^_]+)__", {"r": r"\\uline{\1}", "flags": 0}),
            ("-->", {"r": r"$\\rightarrow$ ", "flags": 0}),
            ("//(.+?)//", {"r": r"\\textit{\1}", "flags": 0}),
    ])

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

    for key, replacement in subdict.items():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="prepocess LaTeX file")
    parser.add_argument("infile", help="input file")
    parser.add_argument("outfile", help="output file")
    parser.add_argument("-t", action="store_true", help="process tables")
    parser.add_argument("--transpose", action="store_true", help="transpose tables if processed")
    parser.add_argument("-r", action="store_true", help="process replacements")

    args = parser.parse_args()
    with open(args.infile, 'r', encoding="utf-8") as fh:
        text = fh.read()
    if args.r:
        text = prepocess_replacements(text)
    if args.t:
        text = prepocess_table(text, transpose=args.transpose)
    with open(args.outfile, 'w', encoding="utf-8") as fh:
        fh.write(text)

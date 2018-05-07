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


def process_table(args, linelist, btable, etable, mode, options={}):
    """Convert the range linelist[btable:etable] to LaTeX table.

    mode, options are ignored so far.
    Table format:
    - Table may start and/or end with a toprule and bottomrule when first and/or last line is %|===
    - midrules are placed when line is %|---
    - A line containing %|_____ leads to joined preceding columns
    - clines are placed for columns with ---
    """
    outtex = []
    cnt, tabformat = 0, None
    bjoin = None
    for index, line in enumerate(linelist[btable:etable]):
        # iterate lines
        line = line[1:].strip('|')
        if line.startswith("==="):
            outtex.append([r"\toprule", r"\bottomrule"][index > 0])
            if index == 0:
                # first line, read format if any
                match = re.search("([^=]+)", line)
                if match is not None:
                    tabformat = match.group(1)
            bjoin = index + 1
        elif line.startswith("---"):
            outtex[-1] = outtex[-1] + r"\midrule"
            bjoin = index + 1
        elif line.startswith("___"):
            if bjoin is None:
                return (False, "Don't know where join begins")
            cols = len(outtex[bjoin].split('&'))
            text = [[] for _ in range(cols)]
            for rindex in range(bjoin, len(outtex)):
                for cindex, ctext in enumerate(outtex[rindex].split('&')):
                    text[cindex].append(ctext.strip(' \\'))
            text = ' & '.join(' '.join(col) for col in text) + r"\\"
            outtex[bjoin] = text
            for rindex in range(bjoin + 1, len(outtex)):
                outtex[rindex] = "%" + outtex[rindex]
            bjoin = index
        elif any(column.startswith("---") for column in line.split('|')):
            clinestr = []
            for cindex, column in enumerate(line.split('|')):
                if column.startswith('---'):
                    clinestr.append("\\cline{{{0}-{0}}}".format(cindex + 1))
            outtex[-1] = outtex[-1] + " ".join(clinestr)
        else:
            line = line.replace('|', '&') + r" \\"
            cnt = max(cnt, line.count('&'))
            outtex.append(line)
    if tabformat is None:
        outtex.insert(0, "\\begin{tabular}" + "{{{}}}".format('l' * (cnt + 1)))
    else:
        outtex.insert(0, "\\begin{tabular}" + "{{{}}}".format(tabformat))
    outtex.append("\\end{tabular}\n")
    args.outfile.write(u"\n".join(outtex))
    return (True, "")


def process_itemize(args, linelist, bindex, eindex, mode=None, options={}):
    if "bgcolor" not in options:
        options["bgcolor"] = "colorexample"
    outlist = []
    indent = -1
    level = -1
    for item in linelist[bindex:eindex]:
        if item.strip().startswith('-'):
            if item.index('-') > indent:
                indent = item.index('-')
                level += 1
                outlist.append("  " * level + "\\begin{compactitem}\\itshape")
            elif item.index('-') < indent:
                outlist.append("  " * level + "\\end{compactitem}")
                indent = item.index('-')
                level -= 1
            outlist.append("  " * level + "\\item " + item[(indent + 1):].strip())
        else:
            outlist.append(" " * 6 + "  " * level + item.strip())
    while level >= 0:
        outlist.append("  " * level + "\\end{compactitem}")
        level -= 1
    if mode is None:
        outlist.insert(0, r"\hskip1em\colorbox{" + options["bgcolor"]+ "}{\parbox{0.92\linewidth}{")
        outlist.append("}}")
        print('\n'.join(outlist), file=args.outfile)
    else:
        print('\n'.join(outlist), file=args.outfile)


def process_description(args, linelist, bindex, eindex, mode=None, options={}):
    linelist = [item[1:] for item in linelist[bindex:eindex]]
    linelist.append(u'')
    matchobj = re.match("([^\[]+)\s*(\[[^\]]+\])*", linelist[0])
    if matchobj.group(2):
        length = matchobj.group(2)[1:-1]
        linelist[0] = matchobj.group(1)
    else:
        length = "1cm"
    if linelist[1].startswith('%|'):
        print(r"\begin{minipage}[t]{" + length + r"}\textbf{" + linelist[0] + r"}\end{minipage}" +
              r"\begin{minipage}[t]{\dimexpr\textwidth-" + length + "-0.4cm}\n" +
              r"\vspace*{-\dimexpr\baselineskip+\heavyrulewidth+\abovetopsep\relax}",
              file=args.outfile)
        analyze(args, linelist[1:], mode=True)
        print(r"\end{minipage}", file=args.outfile)
    else:
        print(r"\begin{minipage}[t]{" + length + r"}\textbf{" + linelist[0] + r"}\end{minipage}" +
              r"\colorbox{colorexample}{\begin{minipage}[t]{\dimexpr\textwidth-" + length + "-0.4cm}",
              file=args.outfile)
        analyze(args, linelist[1:], mode=True)
        print(r"\end{minipage}}", file=args.outfile)


def process_none(args, linelist, bindex, eindex, mode=None, options={}):
    print(linelist[eindex], file=args.outfile)


def get_options(line):
    line = line.strip()[2:]
    # logging.info(dict([item.split(':') for item in [pair for pair in line.replace(' ', '').split(',')]]))
    return dict([item.split(':') for item in [pair for pair in line.replace(' ', '').split(',')]])


def analyze(args, linelist, mode=None):
    fn = process_none
    bindex, eindex = None, None
    options = {}
    for index, line in enumerate(linelist):
        if line.strip().startswith("- "):
            fn = process_itemize
        elif line.strip().startswith("%|"):
            fn = process_table
        elif line.strip().startswith(":"):
            fn = process_description
        elif line.strip().startswith("%@"):
            options = get_options(line)
        elif line.strip() == "":
            eindex = index
            fn(args, linelist, bindex, eindex, mode=mode, options=options)
            bindex, eindex = None, None
            options = {}
            fn = process_none
        if fn != process_none:
            if bindex is None:
                bindex = index
        else:
            fn(args, linelist, index, index, options)
    if bindex is not None:
        fn(args, linelist, bindex, eindex, mode, options)


def process(args):
    subdict = {
        u"\*\*([^*]+)\*\*": {"r": ur"\\textbf{\1}", "flags": 0},
        u"__([^_]+)__":     {"r": ur"\\uline{\1}", "flags": 0},
        u"-->":             {"r": ur"$\\rightarrow$ ", "flags": 0},
        u"\.att":           {"r": ur"\\danger{}", "flags": 0},
        u"\.rem":           {"r": ur"\\eye{}", "flags": 0},
        u"\.\.\.":          {"r": ur"$\\ldots$ ", "flags": 0},
        u"//([^/]+)//":     {"r": ur"\\textit{\1}", "flags": 0},
        u"\|\|([^|]+)\|\|": {"r": ur"\\fbox{\1}", "flags": 0},
        u"<([^|]+)>": {"r": ur"\\begin{small}\1\\end{small}", "flags": 0},
        u"^=([^=]+)=\s*(label{\w+})?\s*$":     {"r": ur"\\section{\1}", "flags": re.MULTILINE},
        u"^==([^=]+)==\s*(label{\w+})?\s*$":   {"r": ur"\\subsection{\1}", "flags": re.MULTILINE}
    }
    def replfn(r, matchobj):
        if r.find("section") != -1 and len(matchobj.groups()) > 1 and matchobj.group(2):
            #print( matchobj.expand(r) + "\\" + matchobj.group(2))
            return matchobj.expand(r) + "\\" + matchobj.group(2)
        return matchobj.expand(r)

    with codecs.open(args.infile, 'r', "utf-8") as fh:
        text = fh.read()
    for key, replacement in subdict.iteritems():
        rf = partial(replfn, replacement['r'])
        text = re.sub(key, rf, text, flags=replacement['flags'])
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

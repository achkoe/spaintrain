"""Preprocessor for tables"""
from __future__ import print_function
import argparse
import sys
import os
import re
import logging
import codecs

static_cnt = 0

logging.basicConfig(level=logging.INFO, format="%(lineno)d: %(msg)s")


def process(args, fh, linelist, btable, etable):
    global static_cnt
    outtex = []
    cnt, tabformat = 0, None
    bjoin = None
    for index, line in enumerate(linelist[btable:etable]):
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
    outtex.append("\\end{tabular}")
    with codecs.open(os.path.join(args.folder, "table{:03}.tex".format(static_cnt)), 'w', 'utf-8') as ft:
        ft.write(u"\n".join(outtex))
        print("%!include(tex): ''{}''".format(ft.name), file=fh)
    static_cnt += 1
    return (True, "")


def main(args):
    args.folder = os.path.abspath(args.folder)
    if not os.path.exists(args.folder):
        os.mkdir(args.folder)
    with codecs.open(args.infile, 'r', "utf-8") as fh:
        buf = fh.read()
        linelist = buf.splitlines()
    btable, etable = None, None
    with codecs.open(os.path.splitext(args.infile)[0] + '.t2tout', "w", 'utf-8') as fh:
        for index, line in enumerate(linelist):
            if line.startswith("%|===") and btable is None:
                btable = index
            elif (line == "" or line.startswith("%|===")) and btable is not None:
                etable = index + [1, 0][line == ""]
                ##
                for iindex in range(btable, etable):
                    linelist[iindex] = re.sub("//([^/]+)//", "\\\\textit{\\1}", linelist[iindex])
                    linelist[iindex] = re.sub("\*\*([^*]+)\*\*", "\\\\textbf{\\1}", linelist[iindex])
                ##
                (okay, msg) = process(args, fh, linelist, btable, etable)
                if not okay:
                    return False, msg
                btable = None
            elif btable is None:
                print(line, file=fh)
            elif line.startswith('%'):
                pass
            else:
                return (False, "invalid format in line {}: {}".format(index, repr(line)))
        msg = "Output written to {}".format(fh.name)
    return (True, msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("infile", help="input file")
    parser.add_argument("-f", "--folder", type=str, dest="folder", metavar="folder", action="store", default=".", help="folder for output, default %(default)s")
    args = parser.parse_args()
    print (args)
    (okay, msg) = main(args)
    print(msg)

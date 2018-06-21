# -*- coding: utf-8 -*-

def process_table(linelist):
    itemlist = []
    tablecols = -1
    # split lines containing & into list
    for line in linelist:
        if line.strip().startswith('\\'):
            itemlist.append(line)
        else:
            itemlist.append(line.strip(' \\').split('&'))
            if tablecols != -1 and len(itemlist[-1]) != tablecols:
                raise Exception("table cols")
            else:
                tablecols = len(itemlist[-1])
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


def prepocess(text):
    OUTTABLE, INTABLE = 0, 1
    mode = OUTTABLE
    textlist = []
    tablelist = []
    for line in text.splitlines():
        if line.strip().startswith(r"\begin{tabular}"):
            textlist.append(line)
            mode = INTABLE
        elif line.strip().startswith(r"\end{tabular}"):
            textlist.append(process_table(tablelist))
            textlist.append(line)
            mode = OUTTABLE
            tablelist = []
        elif mode == INTABLE:
            tablelist.append(line)
        else:
            textlist.append(line)
    return '\n'.join(textlist)


if __name__ == '__main__':
    infilename = "t.tex"
    outfilename = "p_t.tex"
    with open(infilename, 'r', encoding="utf-8") as fh:
        intext = fh.read()
    outtext = prepocess(intext)
    with open(outfilename, 'w', encoding="utf-8") as fh:
        fh.write(outtext)

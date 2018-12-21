from __future__ import print_function
import json
import codecs
import argparse
import tty
import sys
import termios


class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

def update_A_irregular(rlist, fromfilename):
    with codecs.open(fromfilename, "r", encoding="utf-8") as fh:
        ulist = json.load(fh)
    ukeylist = [item["A_infinitivo"] for item in ulist]
    rkeylist = [item["A_infinitivo"] for item in rlist]
    for rindex, rkey in enumerate(rkeylist):
        if rkey not in ukeylist:
            print("WARNING: {} not found in {}".format(rkey, fromfilename))
            continue
        uindex = ukeylist.index(rkey)
        rlist[rindex].update({"A_irregular": ulist[uindex]["A_irregular"]})


def set_priority(rlist):
    for ritem in rlist:
        ritem.update({"A_priority": 10000})


def edit_priority(rlist):
    clist = [item for item in rlist if item["A_priority"] == 10000]
    for index, item in enumerate(clist):
        print(u"{}/{} {} ".format(index, len(clist), item["A_infinitivo"]), end='')
        ch = None
        while ch not in "q 1 2 3 4 5 6 7 8 9".split():
            ch = getch()
        if ch in "1 2 3 4 5 6 7 8 9".split():
            print(ch)
            item["A_priority"] = int(ch)
        if ch == "q":
            break
    print("\nSaving y/n?")
    ch = None
    while ch not in "y n".split():
        ch = getch()
    return ch == "y"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="input file")
    parser.add_argument("--outfile", "-o", action="store", help="output file")
    parser.add_argument("--updateirregular", action="store_true", help="update irregular")
    parser.add_argument("--setpriority", action="store_true", help="set priority")
    parser.add_argument("--editpriority", action="store_true", help="edit priority")
    args = parser.parse_args()
    print(args)
    args.outfile = "__db__.json" if args.outfile is None else args.outfile

    with codecs.open(args.inputfile, "r", encoding="utf-8") as fh:
        rlist = json.load(fh)

    save = True
    if args.updateirregular:
        update_A_irregular(rlist, "_verben.json")
    if args.setpriority:
        set_priority(rlist)
    if args.editpriority:
        save = edit_priority(rlist)

    if save:
        print("Saving to {}".format(args.outfile))
        with codecs.open(args.outfile, "w", encoding="utf-8") as fh:
            json.dump(rlist, fh, sort_keys=True, indent=4, ensure_ascii=False)


from __future__ import print_function
import json
import codecs
import argparse


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="input file")
    parser.add_argument("--outfile", "-o", action="store", help="output file")
    args = parser.parse_args()
    print(args)
    args.outfile = "__db__.json" if args.outfile is None else args.outfile

    with codecs.open(args.inputfile, "r", encoding="utf-8") as fh:
        rlist = json.load(fh)

    update_A_irregular(rlist, "_verben.json")
    set_priority(rlist)

    with codecs.open(args.outfile, "w", encoding="utf-8") as fh:
        json.dump(rlist, fh, sort_keys=True, indent=4, ensure_ascii=False)


import json
import glob
import os.path
import argparse
from collections import OrderedDict


def main(filelist):
    result = OrderedDict()
    for filename in filelist:
        item = json.load(open(filename))
        key = os.path.splitext(os.path.basename(item["image"]))[0]
        result[key] = item
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile")
    args = parser.parse_args()
    print args
    filelist = glob.glob("*.json")
    result = main(sorted(filelist))
    with open(args.outfile, 'w') as fh:
        json.dump(result, fh, indent=4)
import argparse
import glob
import os.path
import json

template = {
    "image": "",
    "config": [
        {
            "color": 4294923520,
            "font": "Noto Sans [unknown],14,-1,5,50,0,0,0,0,0",
            "name": "Default Pen"
        },
        {
            "color": 4294907027,
            "font": "Noto Sans [unknown],14,-1,5,50,0,0,0,0,0",
            "name": "Correction Pen"
        },
        {
            "color": 4278233600,
            "font": "Helvetica,14,-1,5,50,0,0,0,0,0",
            "name": "Remark Pen"
        }
    ],
    "sessionlist": []
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs='?', default='.' + os.sep + "learn", help="folder to scan")
    parser.add_argument("--ext", default='png', help="image file extension")
    args = parser.parse_args()
    filelist = glob.glob(os.path.join(args.folder, "*." + args.ext))
    for filename in filelist:
        targetname = os.path.splitext(filename)[0] + ".json"
        if os.path.isfile(targetname):
            continue
        template["image"] = os.path.join("images", os.path.basename(filename))
        print "generated {}".format(targetname)
        with open(targetname, 'w') as fh:
            json.dump(template, fh, indent=4)

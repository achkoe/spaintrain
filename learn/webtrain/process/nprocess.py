import os
import json
import codecs
from collections import OrderedDict

OUTPUTFOLDER = "html"
INPUTFOLDER = "rawcontents"


def lesson2struct(lesson):
    with codecs.open(os.path.join(INPUTFOLDER, "lesson{}.txt".format(lesson)), encoding="utf-8") as fh:
        linelist = fh.read().splitlines()
    outdict = OrderedDict()
    header = None
    for line in linelist[1:]:
        line = line.strip()
        if line == u"":
            continue
        if line[0].isdigit():
            # headings starts always with number
            header = line
            outdict[header] = []
        elif line.startswith('.bcolumn'):
            if line[-1] == "s":
                outdict[header].append(u"""<div class="flex-container">""")
            outdict[header].append(u"""<div class="column">""")
        elif line.startswith('.ecolumn'):
            outdict[header].append(u"""</div>""")
            if line[-1] == "e":
                outdict[header].append(u"""</div>""")
        else:
            # process task
            outdict[header].append(line)
    return {"title": linelist[0], "content": outdict}


def process(lessonlist):
    outdict = OrderedDict()
    for lesson in lessonlist:
        print("process {}".format(lesson))
        struct = lesson2struct(lesson)
        outdict[struct["title"]] = struct["content"]
    with codecs.open("../js/lesson.js", "w") as fh:
        fh.write("ld={}".format(json.dumps(outdict, indent=4)))


if __name__ == '__main__':
    lessonlist = range(1, 71)
    process(lessonlist)

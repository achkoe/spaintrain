import json
import codecs

mergefile =  "/home/achim/spaintrain/book/presente.json"
sourcefile = "/home/achim/spaintrain/learn/verben.json"
outputfile = "/home/achim/spaintrain/learn/_verben.json"


mlist = json.load(open(mergefile))
slist = json.load(open(sourcefile))

infinitivlist = [d["i"] for d in slist]

for mdict in mlist:
    try:
        index = infinitivlist.index(mdict["i"])
        key = "presente"
        if key in slist[index]:
            print("{} already have key {}".format(mdict["i"], key))
        else:
            slist[index][key] = mdict[key]
    except ValueError:
        print("appending {}".format(mdict["i"]))
        slist.append(mdict)

with codecs.open(outputfile, "w", encoding="utf-8") as fh:
    json.dump(slist, fh, sort_keys=True, indent=4, ensure_ascii=False)

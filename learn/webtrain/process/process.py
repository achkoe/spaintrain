import os
import re
import codecs

OUTPUTFOLDER = "html"
INPUTFOLDER = "rawcontents"


def lesson2html(lesson):

    regexp = re.compile(r"\[([^\]]+)\]")
    with codecs.open(os.path.join(INPUTFOLDER, "lesson{}.txt".format(lesson)), encoding="utf-8") as fh:
        linelist = fh.read().splitlines()
    outlist = [u"""<div class="lesson" id="dl{0}"><h1 id="l{0}">{1}</h1>""".format(lesson, linelist[0])]
    inputlist = []
    taskindex = -1
    for line in linelist[1:]:
        line = line.strip()
        if line == u"":
            continue
        if line[0].isdigit():
            # headings starts always with number
            outlist.append(u"""\n<h2>{}</h2>""".format(line))
        else:
            # process task
            # get all occurences of [] in slist
            slist = regexp.findall(line)
            if len(slist) == 0:
                # it is a task without solution
                outlist.append(u"""<p class="taskns">{}</p>""".format(line))
            else:
                taskindex += 1
                inputlist = []
                solutionlist = []
                # replace all [] with get call
                line = regexp.sub("{}", line)
                outlist.append(u"""<p class="task">{}</p>""".format(line))
                for itemindex, item in enumerate(slist):
                    tid = u"{}_{}_{}".format(lesson, taskindex, itemindex)
                    # get the index of the form
                    if item.startswith(":"):
                        # we need a radio
                        itemlist = item.split("|")[1:]
                        # solution are prefixed with a '!'
                        radiolist = []
                        for subindex, subitem in enumerate(itemlist):
                            if subitem.startswith("!"):
                                # hide solution in output
                                itemlist[subindex] = subitem[1:]
                                # append solution in solutionlist
                                solutionlist.append(itemlist[subindex])
                            radiolist.append(u"""<input required="required" type="radio" id="{ttid}" name="{tid}"/>"""
                                u"""<label for="{ttid}">{value}</label>""".format(value=itemlist[subindex], ttid="{}_{}".format(tid, subindex), tid=tid))
                        inputlist.append(u"<span class='rbtask cbradio'>{}</span>".format("".join(radiolist)))
                    else:
                        # we need a textbox
                        inputlist.append(u"""<input required="required" type="text" id="{tid}" name="{tid}" size="{size}"/>""".format(tid=tid, size=len(item)))
                        if len(item.strip()):
                            solutionlist.append(item)
                outlist[-1] = outlist[-1].format(*inputlist)
                outlist.append(u"""<p class="solution"><span class="note cbradio">"""
                    u"""<input type="radio" id="s{0}_{1}_2" name="s{0}_{1}"/>"""
                    u"""<label for="s{0}_{1}_2">&#x2713;</label>"""
                    u"""<input type="radio" id="s{0}_{1}_1" name="s{0}_{1}"/>"""
                    u"""<label for="s{0}_{1}_1">&#x274D;</label>"""
                    u"""<input type="radio" id="s{0}_{1}_0" name="s{0}_{1}"/>"""
                    u"""<label for="s{0}_{1}_0">&#x2717;</label>"""
                    u"""</span><span class="sc">{2}</span></p>""".format(lesson, taskindex, ", ".join(solutionlist)))
    outlist.append(u"</div>")
    return u"\n".join(outlist)


def process(lessonlist):
    for lesson in lessonlist:
        print("process {}".format(lesson))
        htmltext = lesson2html(lesson)
        with codecs.open(os.path.join(OUTPUTFOLDER, "lesson{}.html".format(lesson)), "w", encoding="utf-8") as fh:
            fh.write(htmltext)


def joinall(lessonlist):
    filelist = [os.path.join(OUTPUTFOLDER, "lesson{}.html".format(lesson)) for lesson in lessonlist]
    htmllist = []
    for filename in filelist:
        with codecs.open(filename, encoding="utf-8") as fh:
            htmllist.append(fh.read())
    with codecs.open("template.html", encoding="utf-8") as fh:
        template = fh.read()
    with codecs.open(os.path.join("..", "webtrain.html"), "w", encoding="utf-8") as fh:
        fh.write(template.format(content="\n".join(htmllist)))


if __name__ == '__main__':
    lessonlist = [1, 2, 3, 4, 5, 6, 7, 12, 43]
    #lessonlist = [12]
    process(lessonlist)
    joinall(lessonlist)
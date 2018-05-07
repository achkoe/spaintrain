#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Transform vocabulary files to different output formats."""

from __future__ import print_function
import re
import datetime
import zlib
import collections
import glob
import os
import codecs
import argparse
try:
    import Levenshtein as ls
except:
    pass
mode_de, mode_es = 0, 1


class Item(object):
    """Class representing an item."""
    def __init__(self, filename=None, lineno=None):
        self.de = []
        self.es = []
        self.hashv = None
        self.group = 0
        self.theme = ''
        self.mode = mode_de
        self.filename = filename
        self.lineno = lineno

    def add(self, line):
        """Append line to self.de or self.es depending on self.mode."""
        if self.mode == mode_de:
            self.de.append(line)
        else:
            self.es.append(line)

    def __str__(self):
        return "{}:{}".format(self.de, self.es)


class BaseClass(object):

    """Base class for Vocabulary2XXX."""

    def getDateString(self):
        """Get formatted date."""
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def append_table(self, stringlist):
        """Table should be formatted like this:
        | Column title
        | col1 | col2
        | col1 | col2
        Title column is optional
        """
        output = ["<table  class='smarttable'>", "</table>"]
        columns = stringlist[1].count('|') - 1
        if stringlist[0].count('|') == 1:
            output.insert(-1, "<tr><th colspan='{}'>{}</th></tr>".format(columns + 1, stringlist[0][1:]))
            del stringlist[0]
        for string in stringlist:
            output.insert(-1, "<tr>{}</tr>"
                          .format("".join("<{tag}>{item}</{tag}>"
                                  .format(tag=['td', 'th'][item.startswith('-')], item=[item, item[1:]][item.startswith('-')])
                                          for item in [_.strip() for _ in string.split('|')[1:]])))
        return '"{}"'.format(''.join(output))


    def append_text(self, stringlist):
        """Append text function."""
        joinstr = ["<br/>", ""][stringlist[0].startswith('<')]
        return '"{}"'.format(joinstr.join(stringlist))


    def appendfunc(self, stringlist):
        return [self.append_text, self.append_table][stringlist[0].startswith('|')](stringlist)


    def readFiles(self, filenames):
        text = []
        for filename in filenames:
            print("Reading {}".format(filename))
            with open(filename) as fh:
                text.extend(fh.read().splitlines())
        return text


    def readTextVocabulary(self, filenames):
        print("Analyzing ...")
        itemlist = []
        themedict = {}
        sourcedict = {}
        totallines = 0
        for filename in filenames:
            item = Item(filename, 1)
            print("Reading {}".format(filename))
            with open(filename) as fh:
                text = fh.read().splitlines()
            totallines += len(text)
            for lineno, line in enumerate(text):
                if line.startswith("="):
                    # look if we have stgh. to process
                    self.processItem(itemlist, item)
                    item = Item(filename, lineno)
                    mo = re.search('\d', line)
                    item.group = mo.group(0) if mo else '0'
                    mo = re.search('[a-z]+', line)
                    item.theme = mo.group(0) if mo else ''
                    mo = re.search('[A-Z]+', line)
                    item.theme += mo.group(0) if mo else 'K'
                    item.mode = mode_de
                elif line.strip() is "":
                    item.mode = mode_es
                elif line.startswith(';'):
                    mo = re.match(';\s*(\w)\s*=\s*(.*)', line)
                    if mo:
                        themedict[mo.group(1)] = mo.group(2)
                elif line.startswith(':'):
                    mo = re.match(':\s*(\w)\s*=\s*(.*)', line)
                    if mo:
                        sourcedict[mo.group(1)] = mo.group(2)
                else:
                    item.add(line)
            # maybe we have to process last item
            self.processItem(itemlist, item)
        print("{} lines read".format(totallines))
        print("{} pairs read".format(len(itemlist)))
        hashv = [item.hashv for item in itemlist]
        c = collections.Counter(hashv)
        if any([v != 1 for v in c.values()]):
            print("PROBLEM: more than 2 items have the same adler32")
            for item in itemlist:
                hashv = item.hashv
                for search in itemlist:
                    if search == item:
                        continue
                    if search.hashv == item.hashv:
                        print(item)
        return itemlist, themedict, sourcedict


class Vocabulary2Train(BaseClass):
    filename = "de_es_vocabular_[0-9][0-9].txt"
    regexp = re.compile("_([a-zA-Z\s&;]+)_")

    def __init__(self, args):
        filenames = glob.glob(self.filename)
        filenames.sort()
        itemlist, themedict, sourcedict = self.readTextVocabulary(filenames)
        vocabulary, themestr, sourcestr = self.outputjs(itemlist, themedict, sourcedict)
        datestr = 'var lastmodified = "{}";\n'.format(self.getDateString())
        with open("vocabulary_de_es.js", "w") as fh:
            fh.write(datestr)
            fh.write(themestr)
            fh.write(sourcestr)
            fh.write(vocabulary)
            print("Generated file {0} successfully".format(fh.name))


    def outputjs(self, itemlist, themedict, sourcedict):
        vocabulary = "/*(vocabulary)s*/\n/* last modified {date}*/\nvar data = [{data}];".format(
            date=self.getDateString(),
            data=",\n".join("[{0.de}, {0.es}, {0.group}, '{0.theme}', '{0.hashv}']"
                            .format(item) for item in itemlist))
        themestr = 'var themestr = [{}];\n'.format(','.join('["{}", "{}"]'.format(k, v) for k, v in themedict.iteritems()))
        sourcestr = 'var sourcestr = [{}];\n'.format(','.join('["{}", "{}"]'.format(k, v) for k, v in sourcedict.iteritems()))
        return vocabulary, themestr, sourcestr


    def processItem(self, itemlist, item):
        """Process single item and append it to itemlist."""
        replacement = (('"', '\\"'), ('ä', '&auml;'), ('ö', '&ouml;'), ('ü', '&uuml;'), ('ß', '&szlig;'),
                       ('Ä', '&Auml;'), ('Ö', '&Ouml;'), ('Ü', '&Uuml;'), ('[', ''), (']', ''))
        if len(item.de) != 0 or len(item.es) != 0:
            item.de = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.de)).split('\n')
            item.es = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.es)).split('\n')
            #
            item.de = [self.regexp.sub(r"<b>\1</b>", e) for e in item.de]
            item.es = [self.regexp.sub(r"<b>\1</b>", e) for e in item.es]
            #
            item.de = self.appendfunc(item.de)
            item.es = self.appendfunc(item.es)
            item.hashv = hex(zlib.adler32(item.es + item.de) & 0xffffffff)[2:-1]
            itemlist.append(item)


class Vocabulary2Dict(BaseClass):
    filename = "de_es_vocabular_[0-9][0-9].txt"
    regexp = re.compile("_([^_]+)_")

    def __init__(self, args):
        filenames = glob.glob(self.filename)
        filenames.sort()
        itemlist, themedict, _ = self.readTextVocabulary(filenames)
        de, es = [], []
        for item in itemlist:
            de.extend(item.de)
            es.extend(item.es)
        de = zip(de, range(len(de)))
        de.sort(key=self.accessItem, cmp=lambda x, y: cmp(x.lower(), y.lower()))
        es = zip(es, range(len(es)))
        es.sort(key=lambda v: v[0])
        with open("dictionary_de_es.js", "w") as fh:
            print("/* {date} */\nvar de = [{de}];\nvar es = [{es}];"
                  .format(date=self.getDateString(),
                          de=',\n'.join('["{}", {}]'.format(_de, index) for _de, index in de),
                          es=',\n'.join('["{}", {}]'.format(_es, index) for _es, index in es)), file=fh)
            print("Generated file {0} successfully".format(fh.name))


    def processItem(self, itemlist, item):
        """Process a single item and append it to itemlist."""
        replacement = (('"', '\\"'), ('[', ''), (']', ''))
        if len(item.de) == 0 and len(item.es) == 0:
            return
        item.de = '|'.join(item.de)
        item.es = '|'.join(item.es)
        item.hashv = hex(zlib.adler32(item.es + item.de) & 0xffffffff)[2:-1]
        mde = re.findall('\[[^\]]*\]', item.de)
        mes = re.findall('\[[^\]]*\]', item.es)
        if len(mes) != len(mde) or len(mde) == 0 or len(mes) == 0:
            return
        item.de = mde
        item.es = mes
        item.de = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.de)).split('\n')
        item.es = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.es)).split('\n')

        item.de = [self.regexp.sub(r"\1", e) for e in item.de]
        item.es = [self.regexp.sub(r"\1", e) for e in item.es]

        itemlist.extend([item])


    def accessItem(self, item):
        if item[0].startswith('zu '):
            return item[0][3:]
        return item[0]


class Vocabulary2Table(BaseClass):
    def __init__(self, args):
        itemlist, themedict, sourcedict = self.readTextVocabulary([args.inputfile, ])
        if args.sort:
            itemlist.sort(cmp=self.cmpfun)
        with open(os.path.splitext(args.inputfile)[0] + ".table", 'w') as fh:
            for item in itemlist:
                print("%| {} | {} |".format(item.es, item.de), file=fh)
            print("Generated file {0} successfully".format(fh.name))

    def cmpfun(self, first, second):
        first_es = first.es[2:].strip() if first.es.startswith("la ") or first.es.startswith("el ") or first.es.startswith("de ") else first.es
        second_es = second.es[2:].strip() if second.es.startswith("la ") or second.es.startswith("el ") or second.es.startswith("de ") else second.es
        return cmp(first_es.lower(), second_es.lower())

    def processItem(self, itemlist, item):
        replacement = (('"', '\\"'), ('[', ''), (']', ''), ('|', '; '))
        if len(item.de) == 0 and len(item.es) == 0:
            return
        item.de = '|'.join(item.de)
        if len(item.es) > 4:
            print("WARNING: cutting {}".format(item.de[:min(len(item.de), 30)]))
            item.es = item.es[:1]
        item.es = '|'.join(item.es[:])
        item.hashv = hex(zlib.adler32(item.es + item.de) & 0xffffffff)[2:-1]
        item.de = reduce(lambda a, kv: a.replace(*kv), replacement, item.de)
        item.es = reduce(lambda a, kv: a.replace(*kv), replacement, item.es)
        itemlist.extend([item])


class Vocabulary2Latex(Vocabulary2Train):
    def __init__(self, args):
        if args.itemsperpage == 16:
            self.itemsperpage = 16
            self.itemsperline = 4
        if args.itemsperpage == 64:
            self.itemsperpage = 64
            self.itemsperline = 8
        if args.itemsperpage == 32:
            self.itemsperpage = 32
            self.itemsperline = 4
        filenames = glob.glob(self.filename)
        filenames.sort()
        itemlist, themedict, sourcedict = self.readTextVocabulary(filenames[:1])
        vocabulary, themestr, sourcestr = self.output(itemlist, themedict, sourcedict)
        with open("latex/vocabulary_de_es.tex", "w") as fh:
            fh.write(vocabulary)
            print("Generated file {0} successfully".format(fh.name))

    def output(self, itemlist, themedict, sourcedict):
        printthemedict = {'a': "Adj", 'b': "Adv", 'g': "Gr", 'k': "Kom", 'p': "Prä", 's': "Subst", 'u': "Verb", 'v': "Verb"}
        index = 0
        xpos, ypos = 0, 0
        vocabulary = []
        for item in itemlist:
            info = []
            for char in item.theme:
                if char in printthemedict:
                    info.append(printthemedict[char])
                elif char in sourcedict:
                    info.append(sourcedict[char][0])
            info = ', '.join(info)
            vocabulary.append("\\entry{{{}}}{{{}}}{{{}}}{{{}}}".format(xpos, ypos, item.de, info))
            vocabulary.append("\\entry{{{}}}{{{}}}{{{}}}{{{}}}".format(xpos + 1, ypos, item.es, info))
            index += 2
            xpos += 2
            if index != 0 and divmod(index, self.itemsperpage)[1] == 0:
                vocabulary.append("\\clearpage")
                xpos, ypos = 0, 0
            elif index != 0 and divmod(index, self.itemsperline)[1] == 0:
                #vocabulary.append("\\\\")
                xpos = 0
                ypos += 1
        return '\n'.join(vocabulary), "", ""


    def processItem(self, itemlist, item):
        """Process single item and append it to itemlist."""
        replacement = (('"', ''), ('ä', 'ä'), ('ö', 'ö'), ('ü', 'ü'), ('ß', 'ß'),
                       ('Ä', 'Ä'), ('Ö', 'Ö'), ('Ü', 'Ü'), ('[', ''), (']', ''), ('%', '\%'),
                       ('_', ''), ("ˈ", ''), ("ʧ", ""))
        if len(item.de) != 0 or len(item.es) != 0:
            item.de = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.de)).split('\n')
            item.es = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.es)).split('\n')
            #
            item.de = [self.regexp.sub(r"<b>\1</b>", e) for e in item.de]
            item.es = [self.regexp.sub(r"<b>\1</b>", e) for e in item.es]
            #
            item.de = self.appendfunc(item.de)
            item.es = self.appendfunc(item.es)
            item.hashv = hex(zlib.adler32(item.es + item.de) & 0xffffffff)[2:-1]
            itemlist.append(item)

    def append_text(self, stringlist):
        """Append text function."""
        joinstr = ["\\\\", ""][stringlist[0].startswith('<')]
        return '{}'.format(joinstr.join(stringlist))


class VocabularyCheck(BaseClass):
    filename = "de_es_vocabular_[0-9][0-9].txt"

    def __init__(self, args):
        filenames = glob.glob(self.filename)
        filenames.sort()
        itemlist, themedict, sourcedict = self.readTextVocabulary(filenames)
        for rindex, ref in enumerate(itemlist):
            result = []
            for index, item in enumerate(itemlist):
                if index == rindex:
                    continue
                if ref.es.startswith("<"):
                    continue
                d = ls.ratio(ref.es, item.es)
                if d > args.distance:
                    result.append((item.es, item.filename, item.lineno))
                    item.es = "<"
                    itemlist[index] = item
            if len(result) > 0:
                print("{0}: {1} ({2}:{3}: {4})".format(
                    ref.es,
                    ', '.join(r[0] for r in result),
                    ref.filename,
                    ref.lineno,
                    ', '.join("{}:{}".format(r[1], r[2]) for r in result)))

    def processItem(self, itemlist, item):
        replacement = (('"', '\\"'), ('[', ''), (']', ''),('los', ''), ('las', ''), ('el', ''), ('la', ''))
        if len(item.de) == 0 and len(item.es) == 0:
            return
        item.hashv = hex(zlib.adler32(''.join(item.es) + ''.join(item.de)) & 0xffffffff)[2:-1]
        item.de = item.de[0]
        item.es = item.es[0]
        item.de = reduce(lambda a, kv: a.replace(*kv), replacement, item.de).strip()
        item.es = reduce(lambda a, kv: a.replace(*kv), replacement, item.es).strip()
        itemlist.extend([item])


class Vocabulary2Anki(BaseClass):
    regexp = re.compile("_([a-zA-Z\s&;]+)_")

    def __init__(self, args):
        filenames = glob.glob(args.filepattern)
        filenames.sort()
        itemlist, themedict, sourcedict = self.readTextVocabulary(filenames)
        vocabulary, themestr, sourcestr = self.outputjs(itemlist, themedict, sourcedict)
        datestr = '# lastmodified = "{}";\n'.format(self.getDateString())
        with codecs.open("spain4anki.txt", "w") as fh:
            fh.write(datestr)
            fh.write(vocabulary)
            print("Generated file {0} successfully".format(fh.name))

    def outputjs(self, itemlist, themedict, sourcedict):
        vocabulary = "\n".join("{0.de} @ {0.es} @ {0.theme}".format(item) for item in itemlist)
        themestr = ''
        sourcestr = ''
        return vocabulary, themestr, sourcestr

    def append_text(self, stringlist):
        """Append text function."""
        return '{}'.format("<br>".join(stringlist))

    def processItem(self, itemlist, item):
        """Process single item and append it to itemlist."""
        def formatlist(item):
            inlist = False
            out = []
            for line in item:
                if line.strip().startswith('-'):
                    line = line.lstrip("- ")
                    if inlist:
                        out[-1] += "</li><li>" + line
                    else:
                        inlist = True
                        out.append("<ul><li>" + line)
                elif line.startswith(' ') and inlist:
                        out[-1] += line.strip(' ')
                else:
                    if inlist:
                        out[-1] += "</li></ul>"
                        inlist = False
                    out.append(line)
            return out

        replacement = (('"', '"'), ('[', ''), (']', ''))
        subdict = {
            "\*\*([^*]+)\*\*": {"r": r"<b>\1</b>", "flags": 0},
            "//([^/]+)//": {"r": r"<em>\1</em>", "flags": 0},
        }

        if len(item.de) != 0 or len(item.es) != 0:
            item.de = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.de)).split('\n')
            item.es = reduce(lambda a, kv: a.replace(*kv), replacement, '\n'.join(item.es)).split('\n')
            #
            for key, replacement in subdict.iteritems():
                item.de = [re.sub(key, replacement["r"], e, flags=replacement['flags']) for e in item.de]
                item.es = [re.sub(key, replacement["r"], e, flags=replacement['flags']) for e in item.es]

            item.es = formatlist(item.es)

            item.de = self.appendfunc(item.de)
            item.es = self.appendfunc(item.es)

            item.hashv = hex(zlib.adler32(item.es + item.de) & 0xffffffff)[2:-1]
            itemlist.append(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(help="sub-command help")
    parser_train = subparsers.add_parser('train', help="generate spaintrain files")
    parser_train.set_defaults(func=Vocabulary2Train)
    parser_dict = subparsers.add_parser('dict', help="generate spaindict files")
    parser_dict.set_defaults(func=Vocabulary2Dict)
    parser_latex = subparsers.add_parser('latex', help="generate latex files")
    parser_latex.set_defaults(func=Vocabulary2Latex)
    parser_latex.add_argument("-i", "--itemsperpage", type=int, choices=[16, 32, 64], default=16, help="number of items per page")
    parser_table = subparsers.add_parser('table', help="generate table files")
    parser_table.add_argument("-s", "--sort", action="store_true", help="sort output")
    parser_table.set_defaults(func=Vocabulary2Table)
    parser_table.add_argument('inputfile', help="name of input file to process")
    parser_check = subparsers.add_parser('check', help="check all inputs for doubles")
    parser_check.add_argument("distance", default=0.9, type=float, nargs='?')
    parser_check.set_defaults(func=VocabularyCheck)
    parser_anki = subparsers.add_parser('anki', help="generate anki files")
    parser_anki.set_defaults(func=Vocabulary2Anki)
    parser_anki.add_argument("--filepattern", "-f", action="store", metavar="fp", default="de_es_vocabular_g?.txt", help="input file pattern, default %(default)s")

    args = parser.parse_args()
    args.func(args)

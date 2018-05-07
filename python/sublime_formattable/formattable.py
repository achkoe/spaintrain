import sublime
import sublime_plugin
import sys


class FormatTableCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.is_scratch():
            return show_error("File is scratch.")
        sels = self.view.sel()
        if len(sels) <= 0:
            return show_error("No selection found.")
        text = self.view.substr(sels[0])
        if (len(text) == 0):
            return show_error("Empty selection.")
        status, retval = formattable(text)
        if status == 0:
            self.view.replace(edit, sels[0], retval)
        else:
            show_error(["Oops", "Invalid character at begin of line"][status])


def show_error(text):
    sublime.error_message(u'FormatTable\n\n%s' % text)


def formattable(text):
    """Format table.

    Table formats are
    %|
    |
    """
    # split teext and try to determine separation character and prefix character
    linelist = text.strip("\n\t ").splitlines()
    itemlist = []
    sep, prefix = '', ''
    length = 0
    for line in linelist:
        if line.strip().startswith("%|"):
            itemlist.append(line[1:].strip(" |").split('|'))
            sep, prefix = '|', '%'
        elif line.strip().startswith('|'):
            itemlist.append(line.strip(" |").split('|'))
            sep, prefix = '|', ''
        else:
            return 1, text
        length = max(length, len(itemlist[-1]))
        itemlist[-1] = [item.strip() for item in itemlist[-1]]
    lengthlist = [0 for i in range(length)]
    # calculate maximum with of each column
    for item in itemlist:
        if item[0].find("===") != -1 or item[0].find("---") != -1:
            continue
        currentlength = [len(column) for column in item]
        for index, length in enumerate(lengthlist):
            lengthlist[index] = max(length, currentlength[index])
    for row, item in enumerate(itemlist):
        if item[0].find("===") != -1:
            itemlist[row] = prefix + "{0}={1}={0}".format(sep, "===".join(["=" * length for length in lengthlist]))
            continue
        elif item[0].find("---") != -1:
            itemlist[row] = prefix + "{0}-{1}-{0}".format(sep, "---".join(["-" * length for length in lengthlist]))
            continue
        for column, content in enumerate(item):
            itemlist[row][column] = "{{:<{}}}".format(lengthlist[column]).format(content)
        itemlist[row] = prefix + "{0} {1} {0}".format(sep, " {} ".format(sep).join(itemlist[row]))

    return 0, '\n'.join(itemlist)


from __future__ import print_function
import subprocess
import re

filename = "pbook.tex"

template = r"""
\documentclass{article}
\usepackage{pdfpages}
\usepackage[paperwidth=297mm, paperheight=210mm]{geometry}
\pagestyle{plain}                                 % Don't use page numbers
\usepackage{textpos}
\setlength{\hoffset}{0pt}
\setlength{\voffset}{0pt}
\usepackage{xcolor}
\usepackage{everypage}
\def\PageTopMargin{1in}
\def\PageLeftMargin{1in}
\newcommand\atxy[3]{%
    \AddEverypageHook{\smash{\hspace*{\dimexpr-\PageLeftMargin-\hoffset+#1\relax}%
    \raisebox{\dimexpr\PageTopMargin+\voffset-#2\relax}{\textcolor[gray]{0.8}{#3}}}}}
\newlength{\ytick}
\setlength{\ytick}{3mm}
% top markers
\atxy{0.500\paperwidth}{\ytick}{\rule{1pt}{\ytick}}
% bottom markers
\atxy{0.500\paperwidth}{\paperheight}{\rule{1pt}{\ytick}}
\begin{document}
\setlength\voffset{+0.0in}                  % adj. vert. offset as needed
\setlength\hoffset{+0.0in}                  % adj. horiz. offset as needed
<>
\end{document}
""".replace('{', '{{').replace('}', '}}').replace('<', '{').replace('>', '}')

pdfinfo = subprocess.check_output(["pdfinfo", "book.pdf"])
matchobj = re.search("^Pages:\s*(\d+)", pdfinfo, re.MULTILINE)
numpages = int(matchobj.group(1))

fullpages, remainingpages = divmod(numpages, 4)

# p+0   p+2
# p+1   p+3
outlist = []
pagecnt = 1
while fullpages > 0:
    #print(pagecnt, fullpages)
    outlist.append("""
    \includepdf[pages={{{}, {}}}, nup=2x1, landscape=false]{{book.pdf}}
    \clearpage
    \includepdf[pages={{{}, {}}}, nup=2x1, landscape=false, angle=180]{{book.pdf}}
    \clearpage""".format(pagecnt, pagecnt + 2, pagecnt + 1, pagecnt + 3))
    pagecnt += 4
    fullpages -= 1

pagenum = ["{}", "{}", "{}", "{}"]
index = [0, 2, 1, 3]
cnt = 0
while pagecnt <= numpages:
    pagenum[index[cnt]] = str(pagecnt)
    pagecnt += 1
    cnt += 1

if pagenum[-2] == "{}":
    pass
#    outlist.append("""
#        \includepdf[pages={{{}, {}}}, nup=2x1, landscape=false]{{book.pdf}}
#        \clearpage
#        """.format(*pagenum))
else:  
    outlist.append("""
        \includepdf[pages={{{}, {}}}, nup=2x1, landscape=false]{{book.pdf}}
        \clearpage
        \includepdf[pages={{{}, {}}}, nup=2x1, landscape=false, angle=180]{{book.pdf}}
        """.format(*pagenum))

with open(filename, 'w') as fh:
    print(template.format('\n'.join(outlist)), file=fh)
print("File {} successfully generated".format(fh.name))
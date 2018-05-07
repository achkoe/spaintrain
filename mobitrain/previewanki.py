"""Convert anki export file to html."""

import os.path
HTML_TEMPLATE = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    .item{{
        margin:0;
        margin-bottom: 1em;
        border: 1px solid black;
    }}
    .de{{
        float:left;
        width:45%;
        overflow:hidden;
        background-color: #EE0;
        padding: 0 10pt;
    }}
    .es{{
        float:left;
        width:45%;
        overflow:hidden;
        background-color: #E66;
        padding: 0 10pt;
    }}
    .clear {{ clear: both;}}
    </style>
  </head>
  <body>
  {content}
  </body>
</html>
"""

ITEM_TEMPLATE = """
<div class="item">
<div class="de">
{de}
</div>
<div class="es">
{es}
</div>
<div class="clear"></div>
</div>

"""
INFILE = "spain4anki.txt"
OUTFILE = os.path.splitext(INFILE)[0] + ".html"


def process():
    contentlist = []
    with open(INFILE, "rb") as fh:
        linelist = fh.readlines()
    for line in linelist:
        if line.startswith('#'):
            continue
        de, es, _ = line.split('@')
        contentlist.append(ITEM_TEMPLATE.format(de=de, es=es))
    with open(OUTFILE, "wb") as fh:
        fh.write(HTML_TEMPLATE.format(title=INFILE, content="\n".join(contentlist)))



if __name__ == '__main__':
    process()

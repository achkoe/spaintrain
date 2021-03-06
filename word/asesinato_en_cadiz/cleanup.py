import re


def main(text):
    def fn_capital_after_fullstop(mo):
        return ". {}".format(mo.group(1).upper())

    def fn_capital_after_dash(mo):
        return "- {}{}".format(mo.group(1).upper(), mo.group(2))


    regexp_fs = re.compile(r"\.\s+([a-z])")
    regexp_cm = re.compile(r"\,\s+")
    regexp_qm = re.compile(r"\?\?\s*")
    regexp_ex = re.compile(r"!!\s*")
    regexp_ld = re.compile(r"…")
    regexp_sp = re.compile(r"[ ]+")
    regexp_nl = re.compile(r"\.(?!\n)")
    regexp_ds = re.compile(r"^-\s*([a-z])(.*)", re.M)

    text = regexp_ds.sub(fn_capital_after_dash, text)
    text = regexp_fs.sub(fn_capital_after_fullstop, text)
    text = regexp_cm.sub(", ", text)
    text = regexp_qm.sub(u"¿", text)
    text = regexp_ex.sub(u"¡", text)
    text = regexp_ld.sub(u"\\ldots", text)
    text = regexp_sp.sub(u" ", text)
    text = regexp_nl.sub(u".\n", text)

    return text


if __name__ == '__main__':
    inname = "contents.in.txt"
    outname = "contents.out.txt"
    with open(inname, encoding="utf-8") as fh:
        text = fh.read()
    with open(outname, "w", encoding="utf-8") as fh:
        fh.write(main(text))

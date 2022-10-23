import sqlite3
import json

from verbmanager import DBFILENAME


DBFILENAME = "_verben.db"


required_key_list = sorted([
    "german", "english", "infinitivo", "priority", "gerundio", "gerundioreflexiv", "participio", "anterior", "condicional", "condicionalperfecto",
    "futuro", "futuroperfecto", "imperativoafirmativo", "imperativoafirmativoreflexiv", "imperativonegativo", "imperfecto", "indefinido", "perfecto",
    "pluscuamperfecto", "presente", "subjuntivofuturo", "subjuntivofuturoperfecto", "subjuntivoimperfecto", "subjuntivoperfecto",
    "subjuntivopluscuamperfecto", "subjuntivopresente", ])

key_list = ["anterior", "condicional", "condicionalperfecto",
    "futuro", "futuroperfecto", "imperativoafirmativo", "imperativoafirmativoreflexiv", "imperativonegativo", "imperfecto", "indefinido", "perfecto",
    "pluscuamperfecto", "presente", "subjuntivofuturo", "subjuntivofuturoperfecto", "subjuntivoimperfecto", "subjuntivoperfecto",
    "subjuntivopluscuamperfecto", "subjuntivopresente"]

def run():
    import_list = json.load(open("importverblist.json"))
    for item in import_list:
        assert sorted(item.keys()) == required_key_list
    con = sqlite3.connect(DBFILENAME)
    cur = con.cursor()
    for item in import_list:
        cur.execute("INSERT INTO verben (german, english, infinitivo, priority, gerundio, gerundioreflexiv, participio) VALUES (?, ?, ?, ?, ?, ?, ?)", (item["german"], item["english"], item["infinitivo"], item["priority"], item["gerundio"], item["gerundioreflexiv"], item["participio"]))
        cur.execute("SELECT id FROM verben WHERE infinitivo==?", (item["infinitivo"], ))
        id_ = cur.fetchone()[0]
        print(id)
        for key in key_list:
            t = item[key]
            if len(t) < 6:
                t.insert(0, None)
            t.insert(0, id_)
            m = ",".join(["?"] * len(t))
            cur.execute("INSERT INTO {} VALUES ({})".format(key, m), t)
    con.commit()
    con.close()



if __name__ == "__main__":
    run()

#!/usr/bin/env python
"""Distribute spaintrain to various devices."""
import argparse
import netrc
import ftplib
import os

PROPERTIES = {
    "tablet": {
        "ipaddress": "192.168.188.48",
        "port": 50100,
        "uploadlist": [
            {
                "remotedir": "/spaintrain",
                "filelist": [
                    os.path.join(os.sep, "home", "achim", "Dokumente", "langtrain", "voctrain", "spaintrain", name) for name in 
                        ["index.html", "index.css", "spaintrain.js", "vocabulary_de_es.js", 
                         "dictionary_de_es.js", "spaindict.html", "dictionary_de_es.js", "spaindict.js", "spaindict.css"]
                    ],
            },
            {
                "remotedir": "/books",
                "filelist": ["/home/achim/Dokumente/langtrain/voctrain/spaintrain/book/tbook.pdf"],
            }
        ]
    },
    "handy": {
        "ipaddress": "192.168.188.21",
        "port": 50100,
        "uploadlist": [
            {
                "remotedir": "/spaintrain",
                "filelist": [
                    os.path.join(os.sep, "home", "achim", "Dokumente", "langtrain", "voctrain", "spaintrain", name) for name in 
                        ["index.html", "index.css", "spaintrain.js", "vocabulary_de_es.js", 
                         "dictionary_de_es.js", "spaindict.html", "dictionary_de_es.js", "spaindict.js", "spaindict.css"]
                ],
            },
        ]
    }
}


def distribute(key):
    host = PROPERTIES[key]["ipaddress"]
    port = PROPERTIES[key]["port"]
    login, account, password = netrc.netrc().authenticators(host)    
    con = ftplib.FTP()
    con.connect(host, port)
    con.login(login, password)
    print("Connected to {}".format(host))
    for upload in PROPERTIES[key]["uploadlist"]:
        print upload["remotedir"]
        con.cwd(upload["remotedir"])
        for name in upload["filelist"]:
            con.storbinary("STOR {}".format(os.path.basename(name)), open(name, "rb"))
        print con .retrlines('LIST')
    con.quit()


def main():
    choices = ["handy", "tablet"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device", choices=choices + [""], nargs="*", default="")   
    args = parser.parse_args()
    args.device = choices if type(args.device) == type('') else args.device
    for device in args.device:
        distribute(device)


if __name__ == '__main__':
    main()

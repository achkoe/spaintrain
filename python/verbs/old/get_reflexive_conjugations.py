import pathlib
import json
import requests
from bs4 import BeautifulSoup


URL = "https://conjugador.reverso.net/conjugacion-espanol-verbo-{infinitivo}.html"
inputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.json")
outputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.out.json")
print(inputfile)


def read_input():
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    return data


def get_conjugation(item):
    r = requests.get(URL.format(**item))
    soup = BeautifulSoup(r.content, "html.parser")
    for title in soup.find_all(class_="blue-box-wrap"):
        key = title.attrs["mobile-title"].strip()
        conjugations = [conjugation.text for conjugation in title.find_all("li")]
        item.update({key: conjugations})


def process_data(data):
    for item in data:
        if item["_complete"] == 0:
            print("processing {infinitivo}".format(**item))
            get_conjugation(item)
            item["_complete"] = 1


def write_output(data):
    with open(outputfile, "w") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    data = read_input()
    process_data(data)
    write_output(data)

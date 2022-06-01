import pathlib
import json
import requests
from bs4 import BeautifulSoup


URL = "https://www.gymglish.com/de/konjugation/spanisch/search?verb={infinitiv}"
inputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben.json")
outputfile = pathlib.Path(__file__).parent.joinpath("reflexive_verben_out.json")
print(inputfile)


def read_input():
    with open(inputfile, "r") as fh:
        data = json.load(fh)
    return data


def get_conjugation(item):
    r = requests.get(URL.format(**item))
    soup = BeautifulSoup(r.content, "html.parser")
    for conjugation_forms in soup.find_all(class_="conjucation-forms"):
        for search in conjugation_forms.previous_elements:
            if search.name == "h2":
                conjugation_mode = search.text.strip()
                break
        tense = conjugation_forms.parent.find("h3").text.strip()
        conjugations = [conjugation.text.strip().split(maxsplit=1)[-1].strip() for conjugation in conjugation_forms.find_all("li")]
        item.update({"{}_{}".format(conjugation_mode, tense): conjugations})
        #break


def process_data(data):
    for item in data:
        if item["_complete"] == 0:
            get_conjugation(item)


def write_output(data):
    with open(outputfile, "w") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    data = read_input()
    process_data(data)
    write_output(data)

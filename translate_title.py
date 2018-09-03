#!/usr/bin/env python

from json import dump, load
from os.path import isfile

class colors:
    BOLD = "\033[1m"
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def translate(translations, key, move):
    print()
    print("==============================================")
    print("ID:          ", key)
    print("Beschreibung:", move["description"])
    print("----------------------------------------------")
    print("Text:       '" +
          colors.BOLD +
          move["name"] +
          colors.END +
          "'")
    name = input("Übersetzung: ")
    print("==============================================")
    if name:
        translations[key] = name
        return True
    return False

data_file = open("data.json", "r")
data = load(data_file)

translations = {}
if isfile("title_translations.json"):
    in_file = open("title_translations.json", "r")
    translations = load(in_file)

moves = data["moves"]
for key, move in moves.items():
    if not key in translations:
        if not translate(translations, key, move):
            break

out_file = open("title_translations.json", "w")
dump(translations, out_file)

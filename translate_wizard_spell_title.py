#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
import sys

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

def save(obj, f):
    f = open(f, "w")
    dump(obj, f, sort_keys=True, indent=4)

def translate(translations, key, spell):
    print()
    print("==============================================")
    print("ID:          ", key)
    print("Beschreibung:", spell["description"])
    print("----------------------------------------------")
    print("--------- 'jump' zum Überspringen ------------")
    print("----------------------------------------------")
    print("Text:       '" +
          colors.BOLD +
          spell["name"] +
          colors.END +
          "'")
    name = input("Übersetzung: ")
    print("==============================================")
    if name.lower() == "jump":
        return True
    if name:
        translations["names"][key] = name
        return True
    return False

data_file = open("data.json", "r")
data = load(data_file)

translations = {}
if isfile("spell_translations.json"):
    in_file = open("spell_translations.json", "r")
    translations = load(in_file)

out_file = "spell_translations.json"

# Translate spell titles
spells = data["classes"]["wizard"]["spells"]
for spell in spells.values():
    if not spell["key"] in translations["names"]:
        success = translate(translations, spell["key"], spell)
        save(translations, out_file)
        if not success:
            sys.exit()

save(translations, out_file)

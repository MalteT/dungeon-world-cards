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
    print("TITLE:       ", move["name"])
    if "classes" in move:
        print("CLASSES:     ", ", ".join(move["classes"]))
    print("----------------------------------------------")
    print("Beschreibung:\n---\n", move["description"], "\n---\n", sep='')
    print("Übersetzung:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        lines.append(line)
    print("==============================================")
    if len(lines) > 0:
        translations[key] = "\n".join(lines)
        return True
    return False

moves_file = open("moves.json", "r")
moves = load(moves_file)

translations = {}
if isfile("description_translations.json"):
    in_file = open("description_translations.json", "r")
    translations = load(in_file)

for key, move in moves.items():
    if not key in translations:
        if not translate(translations, key, move):
            break

out_file = open("description_translations.json", "w")
dump(translations, out_file)

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
    dump(obj, f)

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

data_file = open("data.json", "r")
data = load(data_file)

translations = {}
if isfile("description_translations.json"):
    in_file = open("description_translations.json", "r")
    translations = load(in_file)

out_file = "description_translations.json"

# Translate basic moves
moves = data["basic_moves"]
for move in moves:
    if not move["key"] in translations:
        success = translate(translations, move["key"], move)
        save(translations, out_file)
        if not success:
            sys.exit()

# Translate special moves
moves = data["special_moves"]
for move in moves:
    if not move["key"] in translations:
        success = translate(translations, move["key"], move)
        save(translations, out_file)
        if not success:
            sys.exit()

save(translations, out_file)
# Reload moves to fix dublication bug
translations = {}
if isfile("description_translations.json"):
    in_file = open("description_translations.json", "r")
    translations = load(in_file)

# Translate all remaining moves
moves = data["moves"]
for key, move in moves.items():
    if not key in translations:
        success = translate(translations, key, move)
        save(translations, out_file)
        if not success:
            sys.exit()

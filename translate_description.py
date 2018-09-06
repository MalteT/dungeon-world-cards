#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
from subprocess import run
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
    temp_file = "/tmp/" + key
    temp = open(temp_file, "w")
    print("# Übersetzung oben eingeben.",
          "# Ohne Eingabe wird die Übersetzung abgebrochen.",
          "# ",
          "# ================================================================================",
          "# ID:          %s" % key,
          "# TITLE:       %s" % move["name"],
          "# CLASSES:     %s" % ", ".join(move["classes"]) if "classes" in move else "All classes",
          "# -- Zu Übersetzen ---------------------------------------------------------------",
          "# %s" % move["description"].replace("\n", "\n# "),
          "# --------------------------------------------------------------------------------",
          "# ================================================================================",
          sep="\n",
          file=temp)
    temp.flush()
    temp.close()
    proc = run(["$VISUAL %s" % temp_file], shell=True)
    if proc.returncode == 0:
        lines = []
        temp = open(temp_file)
        for line in temp.readlines():
            if not line.startswith("#"):
                line = line.strip()
                print(line)
                lines.append(line)
        temp.close()
        if len(lines) > 0 and lines[0] != "":
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

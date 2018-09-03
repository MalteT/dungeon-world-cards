#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
import re

MOVES_FILE = "moves.json"

def err(message):
    print(message)

def format_move_description(description):
    lines = description.split('\n')

    def prefix(line):
        if line.startswith("- "):
            return "bullet | " + line[2:]
        elif line.startswith("-> "):
            return "bullet | " + line[3:]
        elif line.startswith("Wirf+"):
            return "section | " + line
        else:
            return "text | " + line

    lines = map(prefix, lines)

    final = []
    for line in lines:
        if line.startswith("section | Wirf"):
            final.append("fill")
        # Replace ** with <b>
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
        # Bold 10+, 7-9, ...
        line = re.sub(r"Bei ([0-9]+[\+-][0-9]*)", r"Bei <b>\1</b>", line)
        # Italic dice and number
        line = re.sub(r"([\+-]?[0-9]+(w[0-9]+)?[\+-]?)", r"<i>\1</i>", line)
        final.append(line)

    return list(final)

def class_to_icon(classes):
    return {
        "bard": "class-bard",
        "wizard": "class-wizard",
        "paladin": "class-paladin",
        "cleric": "class-cleric",
        "druid": "class-druid",
        "fighter": "class-fighter",
        "ranger": "class-ranger",
        "thief": "class-rogue"
    }.get(classes, "artificial-intelligence")

def class_to_name(classes):
    return {
        "bard": "Barde",
        "wizard": "Zauberer",
        "paladin": "Paladin",
        "cleric": "Kleriker",
        "druid": "Druide",
        "fighter": "Krieger",
        "ranger": "Waldläufer",
        "thief": "Dieb"
    }.get(classes, "Alle")

def add_moves(cards, data):
    if not isfile(MOVES_FILE):
        err(MOVES_FILE, "not found!")

    moves = load(open(MOVES_FILE))

    # If translations exist, load them
    if isfile("title_translations.json"):
        title_translations = load(open("title_translations.json"))
    else:
        title_translations = {}
    if isfile("description_translations.json"):
        desc_translations = load(open("description_translations.json"))
    else:
        desc_translations = {}

    # Add all moves
    for key, move in moves.items():
        count = 1

        # If no class given, it's for all of them
        # and there should be more than just one
        if not "classes" in move:
            move["classes"] = [ "all" ]
            count = 5

        # If the title is translated, use translation
        if key in title_translations:
            move["name"] = title_translations[key]

        # If the description is translated, use translation
        if key in desc_translations:
            move["description"] = desc_translations[key]

        # Add a card for every class specified
        for name in move["classes"]:
            card = {
                "id": key,
                "title": move["name"],
                "count": count,
                "icon": class_to_icon(name),
                "color": "Teal",
                "contents": [
                    "subtitle | " + class_to_name(name),
                    "rule"
                ] + format_move_description(move["description"])
            }
            # Add description
            cards.append(card)


data_file = open("data.json", "r")
data = load(data_file)

cards = []
add_moves(cards, data)

card_file = open("cards.json", "w")
dump(cards, card_file)

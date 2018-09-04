#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
import re

MOVES_FILE = "moves.json"
DATA_FILE = "data.json"

CARDS_OUTPUT = "cards.json"

def err(message):
    print(message)

# Calculate the title size for a given title
def calculate_title_size(title):
    if len(title) > 25:
        return "10"
    if len(title) > 22:
        return "11"
    if len(title) > 20:
        return "12"
    return "13"

# Add move cards
def add_moves(cards):

    # Format move description according to some rules
    def format_move_description(description):
        lines = description.split('\n')
        def prefix(line):
            if line.startswith("- "):
                return "bullet | " + line[2:]
            elif line.startswith("-> "):
                return "bullet | " + line[3:]
            elif line.startswith("Wirf"):
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

    # Translate a class to an icon
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

    # Translate a class id to a name
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
        }.get(classes, "Alle Klassen")
    if not isfile(MOVES_FILE):
        err(MOVES_FILE, "not found!")

    moves = load(open(MOVES_FILE))

    # If translations exist, load them
    if isfile("title_translations.json"):
        title_translations = load(open("title_translations.json"))
        anz = len(title_translations)
        print("Übersetzungen (Titel): %d -> %.2f%% " % (anz , 100.0 * anz / len(moves)))
    else:
        title_translations = {}
    if isfile("description_translations.json"):
        desc_translations = load(open("description_translations.json"))
        anz = len(desc_translations)
        print("Übersetzungen (Beschreibung): %d -> %.2f%% " % (anz , 100.0 * anz / len(moves)))
    else:
        desc_translations = {}

    # Add all moves that have valid translations
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
        else:
            continue

        # If the description is translated, use translation
        if key in desc_translations:
            move["description"] = desc_translations[key]
        else:
            continue

        # Add a card for every class specified
        for name in move["classes"]:
            card = {
                "id": key,
                "title": move["name"],
                "title_size": calculate_title_size(move["name"]),
                "count": count,
                "icon": class_to_icon(name),
                "color": "DimGray",
                "contents": [
                    "subtitle | " + class_to_name(name),
                    "rule"
                ] + format_move_description(move["description"])
            }
            # Add description
            cards.append(card)

cards = []
add_moves(cards)

card_file = open(CARDS_OUTPUT, "w")
dump(cards, card_file)

#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
from sys import argv
import re

DATA_FILE = "data.json"
CARDS_OUTPUT = "cards.json"

color = "DimGray"

# Check existance of files
if not isfile(DATA_FILE):
    err(DATA_FILE, "not found!")

data_file = open(DATA_FILE)
data = load(data_file)
moves = data["moves"]

# If translations exist, load them
title_translations = {}
desc_translations = {}
if isfile("title_translations.json"):
    title_translations = load(open("title_translations.json"))
    anz = len(title_translations)
    print("Übersetzungen (Titel): %d -> %.2f%% " % (anz , 100.0 * anz / len(moves)))
if isfile("description_translations.json"):
    desc_translations = load(open("description_translations.json"))
    anz = len(desc_translations)
    print("Übersetzungen (Beschreibung): %d -> %.2f%% " % (anz , 100.0 * anz / len(moves)))

def err(message):
    print(message)

# Return a list of classes available
def get_classes():
    data_file = open(DATA_FILE)
    data = load(data_file)
    classes = data["classes"].keys()
    data_file.close()
    return list(classes)

# Extract and translate move identified by key
def key_to_move(key):
    move = moves[key]
    # If the title is translated, use translation
    if key in title_translations:
        move["name"] = title_translations[key]
    else:
        print("Missing title for %s" % key)
        return False
    # If the description is translated, use translation
    if key in desc_translations:
        move["description"] = desc_translations[key]
    else:
        print("Missing description for %s" % key)
        return False
    return move

# Calculate the title size for a given title
# TODO Could use some improvements
def calculate_title_size(title):
    if len(title) > 25:
        return "10"
    if len(title) > 22:
        return "11"
    if len(title) > 20:
        return "12"
    return "13"

# Format move description according to some rules
def format_move_description(description):
    lines = description.split('\n')
    def prefix(line):
        if line.startswith("- "):
            return "bullet | " + line[2:]
        elif line.startswith("-> "):
            return "bullet | " + line[3:]
        elif line.startswith("Wurf"):
            return "section | " + line
        elif line == "fill()":
            return "fill"
        elif line.startswith("boxes("):
            nr_boxes = re.sub(r"boxes\(([1-9])\)", r"\1", line)
            return "boxes | " + nr_boxes
        else:
            return "text | " + line
    lines = map(prefix, lines)
    final = []
    for line in lines:
        if line.startswith("section | Wurf"):
            final.append("fill")
        # Replace id(move_id) with the name of move_id
        line = re.sub(r"id\((.*?)\)",
                      lambda match: "<span style='text-decoration: underline'>%s</span>" % key_to_move(match.group(1))["name"],
                      line)
        # Replace ** with <b>
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
        # Make head :: tail into a property
        line = re.sub(r"text \| (.*?) :: (.*?)", r"property | \1 | \2", line)
        # Bold 10+, 7-9, ...
        line = re.sub(r"Bei ([0-9]+[\+-][0-9]*)", r"Bei <b>\1</b>", line)
        # Italic dice and number
        line = re.sub(r"([\+-]?[0-9]+(w[0-9]+)?[\+-]?)", r"<i>\1</i>", line)
        final.append(line)
    return list(final)

# Translate a class to an icon
def class_to_icon(cl):
    return {
        "bard": "class-bard",
        "wizard": "class-wizard",
        "paladin": "class-paladin",
        "cleric": "class-cleric",
        "druid": "class-druid",
        "fighter": "class-fighter",
        "ranger": "class-ranger",
        "thief": "class-rogue"
    }.get(cl, "artificial-intelligence")

# Translate a class id to a name
def class_to_name(cl):
    return {
        "bard": "Barde",
        "wizard": "Zauberer",
        "paladin": "Paladin",
        "cleric": "Kleriker",
        "druid": "Druide",
        "fighter": "Krieger",
        "ranger": "Waldläufer",
        "thief": "Dieb"
    }.get(cl, "Alle Klassen")

# Add race moves from the given class
def add_race_moves_from_class(cards, cl):
    content = data["classes"][cl]
    if "race_moves" in content:
        for move in content["race_moves"]:
            key = move["key"]
            move = key_to_move(key)
            if not move:
                continue
            card = {
                "id": key,
                "title": move["name"],
                "title_size": calculate_title_size(move["name"]),
                "count": 1,
                "icon": class_to_icon(cl),
                "color": color,
                "contents": [
                    "subtitle | " + class_to_name(cl) + " (Rasse)",
                    "rule"
                ] + format_move_description(move["description"])
            }
            cards.append(card)
# Add starting moves from the given class
def add_starting_moves_from_class(cards, cl):
    content = data["classes"][cl]
    if "starting_moves" in content:
        for move in content["starting_moves"]:
            key = move["key"]
            move = key_to_move(key)
            if not move:
                continue
            card = {
                "id": key,
                "title": move["name"],
                "title_size": calculate_title_size(move["name"]),
                "count": 1,
                "icon": class_to_icon(cl),
                "color": color,
                "contents": [
                    "subtitle | " + class_to_name(cl) + " (Level 0)",
                    "rule"
                ] + format_move_description(move["description"])
            }
            cards.append(card)

# Add advanced moves from the given class
def add_advanced_moves_from_class(cards, cl):
    content = data["classes"][cl]
    # Add advanced moves beginning at level 2
    if "advanced_moves_1" in content:
        for move in content["advanced_moves_1"]:
            key = move["key"]
            move = key_to_move(key)
            if not move:
                continue
            # Create card
            card = {
                "id": key,
                "title": move["name"],
                "title_size": calculate_title_size(move["name"]),
                "count": 1,
                "icon": class_to_icon(cl),
                "color": color,
                "contents": [
                    "subtitle | " + class_to_name(cl) + " (Level 2)",
                    "rule"
                ] + format_move_description(move["description"])
            }
            # Add requires/replaces information
            if "replaces" in move:
                repl_key = move["replaces"]
                repl_move = key_to_move(repl_key)
                if not repl_move:
                    repl_move = { "name": "To be translated" }
                card["contents"] += [
                    "fill",
                    "rule",
                    "property | Ersetzt | " + repl_move["name"]
                ]
            elif "requires" in move:
                requ_key = move["requires"]
                requ_move = key_to_move(requ_key)
                if not requ_move:
                    requ_move = { "name": "To be translated" }
                card["contents"] += [
                    "fill",
                    "rule",
                    "property | Benötigt | " + requ_move["name"]
                ]
            cards.append(card)
    # Add advanced moves beginning at level 6
    if "advanced_moves_2" in content:
        for move in content["advanced_moves_2"]:
            key = move["key"]
            move = key_to_move(key)
            if not move:
                continue
            # Create card
            card = {
                "id": key,
                "title": move["name"],
                "title_size": calculate_title_size(move["name"]),
                "count": 1,
                "icon": class_to_icon(cl),
                "color": color,
                "contents": [
                    "subtitle | " + class_to_name(cl) + " (Level 6)",
                    "rule"
                ] + format_move_description(move["description"])
            }
            # Add requires/replaces information
            if "replaces" in move:
                repl_key = move["replaces"]
                repl_move = key_to_move(repl_key)
                if not repl_move:
                    repl_move = { "name": "To be translated" }
                card["contents"] += [
                    "fill",
                    "rule",
                    "property | Ersetzt | " + repl_move["name"]
                ]
            elif "requires" in move:
                requ_key = move["requires"]
                requ_move = key_to_move(requ_key)
                if not requ_move:
                    requ_move = { "name": "To be translated" }
                card["contents"] += [
                    "fill",
                    "rule",
                    "property | Benötigt | " + requ_move["name"]
                ]
            cards.append(card)
# Add basic moves
def add_basic_moves(cards, cl):
    basic_moves = data["basic_moves"]
    for move in basic_moves:
        key = move["key"]
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
        card = {
            "id": move["key"],
            "title": move["name"],
            "title_size": calculate_title_size(move["name"]),
            "count": 1,
            "icon": "artificial-intelligence",
            "color": color,
            "contents": [
                "subtitle | Aktion",
                "rule"
            ] + format_move_description(move["description"])
        }
        cards.append(card)

# Add special moves
def add_special_moves(cards, cl):
    special_moves = data["special_moves"]
    for move in special_moves:
        key = move["key"]
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
        card = {
            "id": move["key"],
            "title": move["name"],
            "title_size": calculate_title_size(move["name"]),
            "count": 1,
            "icon": "artificial-intelligence",
            "color": color,
            "contents": [
                "subtitle | Spezial-Aktion",
                "rule"
            ] + format_move_description(move["description"])
        }
        cards.append(card)
# Format wizard spell level
def format_wizard_spell_level(lvl):
    if lvl == "cantrip":
        return "Streich"
    return "Level %d" % lvl
# Add wizard spells
def add_wizard_spells(cards):
    spells = data["classes"]["wizard"]["spells"]
    translations_file = open("spell_translations.json")
    translations = load(translations_file)
    for key, spell in spells.items():
        # Translation stuff
        if key in translations["names"]:
            spell["name"] = translations["names"][key]
            if key in translations["descriptions"]:
                spell["descriptions"] = translations["descriptions"][key]
        tags = []
        if "tags" in spell:
            for tag in spell["tags"]:
                if tag in translations["tags"]:
                    tag = translations["tags"][tag]
                tags.append("bullet | %s" % tag)
            if len(tags) > 0:
                tags = [
                    "fill",
                    "section | Tags"
                ] + tags
        # Card adding stuff
        card = {
            "id": key,
            "title": spell["name"],
            "title_size": calculate_title_size(spell["name"]),
            "count": 1,
            "icon": "spell-book",
            "color": "Indigo",
            "contents": [
                "subtitle | " + format_wizard_spell_level(spell["level"]),
                "rule",
                "text | " + spell["description"]
            ] + tags
        }
        cards.append(card)
# Add all moves relevant to a single class.
def add_moves_from_class(cards, cl):
    add_race_moves_from_class(cards, cl)
    add_starting_moves_from_class(cards, cl)
    add_advanced_moves_from_class(cards, cl)
    add_basic_moves(cards, cl)
    add_special_moves(cards, cl)
    if cl == "wizard":
        add_wizard_spells(cards)



if __name__ == "__main__":
    cards = []
    if len(argv) >= 2:
        # If classes given, only extract for them
        for cl in get_classes():
            if cl in argv:
                add_moves_from_class(cards, cl)
    else:
        for cl in get_classes():
            add_moves_from_class(cards, cl)

    card_file = open(CARDS_OUTPUT, "w")
    dump(cards, card_file, sort_keys=True, indent=4)

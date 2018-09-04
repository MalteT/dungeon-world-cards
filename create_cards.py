#!/usr/bin/env python3

from json import dump, load
from os.path import isfile
import re

DATA_FILE = "data.json"
MOVES_FILE = "moves.json"

CARDS_OUTPUT = "cards.json"

def err(message):
    print(message)

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

    # Extract and translate move identified by key
    def key_to_move(key, title_translations, desc_translations, move_data):
        move = move_data[key]
        # If the title is translated, use translation
        if key in title_translations:
            move["name"] = title_translations[key]
        else:
            return False
        # If the description is translated, use translation
        if key in desc_translations:
            move["description"] = desc_translations[key]
        else:
            return False
        return move

    # Check existance of files
    if not isfile(MOVES_FILE):
        err(MOVES_FILE, "not found!")
    if not isfile(DATA_FILE):
        err(DATA_FILE, "not found!")

    data = load(open(DATA_FILE))
    moves = load(open(MOVES_FILE))

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

    # Add moves of all classes that have valid translations
    class_moves = data["classes"]
    for name, content in class_moves.items():

        # Add race moves
        if "race_moves" in content:
            for move in content["race_moves"]:
                key = move["key"]
                move = key_to_move(key, title_translations, desc_translations, moves)
                if not move:
                    continue
                card = {
                    "id": key,
                    "title": move["name"],
                    "title_size": calculate_title_size(move["name"]),
                    "count": 1,
                    "icon": class_to_icon(name),
                    "color": "DimGray",
                    "contents": [
                        "subtitle | " + class_to_name(name) + " (Rasse)",
                        "rule"
                    ] + format_move_description(move["description"])
                }
                # Add description
                cards.append(card)

        # Add starting moves
        if "starting_moves" in content:
            for move in content["starting_moves"]:
                key = move["key"]
                move = key_to_move(key, title_translations, desc_translations, moves)
                if not move:
                    continue
                card = {
                    "id": key,
                    "title": move["name"],
                    "title_size": calculate_title_size(move["name"]),
                    "count": 1,
                    "icon": class_to_icon(name),
                    "color": "DimGray",
                    "contents": [
                        "subtitle | " + class_to_name(name) + " (Level 0)",
                        "rule"
                    ] + format_move_description(move["description"])
                }
                # Add description
                cards.append(card)

        # Add advanced moves beginning at level 2
        if "advanced_moves_1" in content:
            for move in content["advanced_moves_1"]:
                key = move["key"]
                move = key_to_move(key, title_translations, desc_translations, moves)
                if not move:
                    continue
                # Create card
                card = {
                    "id": key,
                    "title": move["name"],
                    "title_size": calculate_title_size(move["name"]),
                    "count": 1,
                    "icon": class_to_icon(name),
                    "color": "DimGray",
                    "contents": [
                        "subtitle | " + class_to_name(name) + " (Level 2)",
                        "rule"
                    ] + format_move_description(move["description"])
                }
                # Add requires/replaces information
                if "replaces" in move:
                    repl_key = move["replaces"]
                    repl_move = key_to_move(repl_key, title_translations, desc_translations, moves)
                    if not repl_move:
                        repl_move = { "name": "To be translated" }
                    card["contents"] += [
                        "fill",
                        "rule",
                        "property | Ersetzt | " + repl_move["name"]
                    ]
                elif "requires" in move:
                    requ_key = move["requires"]
                    requ_move = key_to_move(requ_key, title_translations, desc_translations, moves)
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
                move = key_to_move(key, title_translations, desc_translations, moves)
                if not move:
                    continue
                # Create card
                card = {
                    "id": key,
                    "title": move["name"],
                    "title_size": calculate_title_size(move["name"]),
                    "count": 1,
                    "icon": class_to_icon(name),
                    "color": "DimGray",
                    "contents": [
                        "subtitle | " + class_to_name(name) + " (Level 6)",
                        "rule"
                    ] + format_move_description(move["description"])
                }
                # Add requires/replaces information
                if "replaces" in move:
                    repl_key = move["replaces"]
                    repl_move = key_to_move(repl_key, title_translations, desc_translations, moves)
                    if not repl_move:
                        repl_move = { "name": "To be translated" }
                    card["contents"] += [
                        "fill",
                        "rule",
                        "property | Ersetzt | " + repl_move["name"]
                    ]
                elif "requires" in move:
                    requ_key = move["requires"]
                    requ_move = key_to_move(requ_key, title_translations, desc_translations, moves)
                    if not requ_move:
                        requ_move = { "name": "To be translated" }
                    card["contents"] += [
                        "fill",
                        "rule",
                        "property | Benötigt | " + requ_move["name"]
                    ]
                cards.append(card)

    # Add all basic moves
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
            "count": 5,
            "icon": "artificial-intelligence",
            "color": "DimGray",
            "contents": [
                "subtitle | Aktion",
                "rule"
            ] + format_move_description(move["description"])
        }
        cards.append(card)

    # Add all special moves
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
            "count": 5,
            "icon": "artificial-intelligence",
            "color": "DimGray",
            "contents": [
                "subtitle | Spezial-Aktion",
                "rule"
            ] + format_move_description(move["description"])
        }
        cards.append(card)

cards = []
add_moves(cards)

card_file = open(CARDS_OUTPUT, "w")
dump(cards, card_file)

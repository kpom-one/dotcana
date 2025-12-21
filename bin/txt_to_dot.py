#!/usr/bin/env python3
import json
import sys
import re


def load_cards(json_path="data/cards.json"):
    with open(json_path, "r") as f:
        data = json.load(f)
    # Build lookup by fullName
    return {card["fullName"]: card for card in data["cards"]}


def parse_deck(txt_path):
    """Parse deck file: 'COUNT CARD_NAME' per line"""
    cards = []
    with open(txt_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(\d+)\s+(.+)", line)
            if match:
                count = int(match.group(1))
                name = match.group(2).strip()
                cards.append((count, name))
    return cards


def generate_deck_dot(deck_num, deck_cards, card_db):
    lines = [f"digraph deck{deck_num} {{"]

    card_index = 1
    for count, name in deck_cards:
        card = card_db.get(name)
        if not card:
            print(f"Error: Card '{name}' not found in database", file=sys.stderr)
            sys.exit(1)

        for _ in range(count):
            node_id = f"D{deck_num}_{card_index:02d}"
            lines.append(
                f'    {node_id} [type="Card", card_id="{card["id"]}", exerted="0", damage="0", label="{name}"];'
            )
            card_index += 1

    lines.append("}")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <deck_number> <filename.txt>")
        print(f"Example: {sys.argv[0]} 1 data/deck1.txt")
        sys.exit(1)

    deck_num = sys.argv[1]
    txt_path = sys.argv[2]

    card_db = load_cards()
    deck_cards = parse_deck(txt_path)

    output = generate_deck_dot(deck_num, deck_cards, card_db)
    print(output)


if __name__ == "__main__":
    main()

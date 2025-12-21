# dotcana

Model Lorcana game state as directed graphs using DOT format.

## Setup

```bash
just setup
```

Installs: `networkx`, `pydot`

## Usage

```bash
# Create a matchup from two decks
just match data/decks/bs01.txt data/decks/rp01.txt

# Show game state and available actions
just show fe69

# Clear all output
just clear
```

## How It Works

- **Template** (`data/template.dot`) - Game board structure (zones, players)
- **Decks** (`data/decks/*.txt`) - Card lists, converted to DOT
- **Game state** (`output/<hash>/game.dot`) - Complete graph: structure + cards + legal actions
- **Rules engine** (`bin/rules-engine.py`) - Computes CAN_* edges (legal actions)

See `SCHEMA.md` for details.

## What Works

- ✓ Game initialization (template + decks → game.dot)
- ✓ Action computation (CAN_PASS only)
- ✓ State visualization via DOT

## What Doesn't

Everything else. Next: implement shuffle as first action.

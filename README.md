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

# Shuffle and draw starting hands (7 cards each)
just shuffle b013 "0123456.0123456.ab"

# Show game state and available actions
just show b013 0123456.0123456.ab

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
- ✓ Deterministic shuffle with hand-spec seeds
- ✓ Lazy card node creation (cards only in graph when drawn)
- ✓ Action computation (CAN_PASS, CAN_INK)
- ✓ Semantic action IDs (e=end, i=ink, p=play, etc.)
- ✓ Action directories pre-created for exploration
- ✓ State visualization via DOT

## What Doesn't

- Action application (applying actions to mutate state)
- Turn advancement
- Lore tracking
- Combat resolution
- Effect chains

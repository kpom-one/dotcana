# dotcana

Lorcana game state engine using directed graphs (DOT format). Browse game states as a filesystem tree, with on-demand state computation.

## Setup

```bash
just setup
```

Installs: `networkx`, `pydot`, `flask`

## Quick Start

```bash
# Set up a test game (creates deterministic game state)
just test

# Start the web viewer
just serve
# Visit http://localhost:5000

# Or explore via CLI
just play output/b013/0123456.0123456.ab/i49
```

## Commands

```bash
# Create a matchup from two decks
just match data/decks/bs01.txt data/decks/rp01.txt

# Shuffle and draw starting hands with seed
just shuffle b013 "0123456.0123456.ab"

# Navigate to a state and apply action if needed
just play output/b013/0123456.0123456.ab/i49

# Show available actions at a state
just show b013 0123456.0123456.ab

# Start web viewer (browse game tree)
just serve

# Set up deterministic test game
just test

# Clear all output
just clear
```

## How It Works

- **Game state as filesystem**: Each state is a directory with `game.dot`. Action directories (like `i49/`, `e35/`) represent possible moves.
- **On-demand computation**: Navigate to an action directory → state computed automatically
- **Semantic action IDs**: `e35` = end turn, `i49` = ink card, `p2c` = play card, etc. (hash-based for determinism)
- **Web viewer**: Browse the game tree visually, click through actions
- **DOT graphs**: Game state stored as NetworkX MultiDiGraph, serialized to DOT format

### Architecture

```
data/
  template.dot        # Game board structure (zones, players)
  decks/*.txt         # Card lists

output/
  <matchup-hash>/     # Deterministic hash of deck contents
    <seed>/           # Hand shuffle seed (format: deck1.deck2.mulligan)
      game.dot        # Current state
      i49/            # "Ink card" action directory
        game.dot      # State after inking
        e35/          # "End turn" action directory
          game.dot    # State after ending turn

lib/
  core/graph.py       # Graph utilities (load/save DOT, edge queries)
  lorcana/
    setup.py          # Game initialization, shuffle, action descriptions
    state.py          # LorcanaState class (load/save/mutate)
    compute.py        # Rules engine (compute legal actions)
    actions.py        # Action ID generation
    cards.py          # Card database (O(1) lookups)

bin/rules-engine.py   # CLI: init, shuffle, play, show
web/app.py            # Flask viewer: browse game tree
```

See `SCHEMA.md` for DOT graph structure details.

## What Works

- ✅ Game initialization (template + decks → game.dot)
- ✅ Deterministic shuffle with hand-spec seeds (`0123456.0123456.ab`)
- ✅ Lazy card node creation (cards only exist when drawn)
- ✅ Action computation (CAN_PASS, CAN_INK)
- ✅ Action execution (end turn, ink cards)
- ✅ Turn advancement with ink drop refresh
- ✅ Semantic action IDs with hash-based directory names
- ✅ Action directories pre-created for tab completion
- ✅ Web viewer for visual game tree browsing
- ✅ CLI exploration via `just play`
- ✅ Test harness via `just test`

## What Doesn't (Yet)

- ❌ Playing cards from hand (CAN_PLAY)
- ❌ Questing for lore (CAN_QUEST)
- ❌ Challenging characters (CAN_CHALLENGE)
- ❌ Card abilities and effects
- ❌ Singing songs
- ❌ Win condition detection

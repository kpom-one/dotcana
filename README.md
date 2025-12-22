# dotcana

Explore Lorcana games as a filesystem. Each directory is a game state, subdirectories are possible moves. Navigate with `cd`, replay with paths.

## Quick Start

```bash
# Install dependencies
just setup

# Create a test game
just test

# Explore the game tree
just play output/b013/b123456.0123456.ab/0/1/0/6

# Or use the web viewer
just serve
# Visit http://localhost:5000
```

## Understanding Paths

A path like `output/b013/b123456.0123456.ab/0/1/0/6` tells a story:

```
output/b013/b123456.0123456.ab/0/1/0/6
       │    └────seed─────┘  └─moves─┘
       └─matchup (which decks)
```

- **`b013`** - Matchup between two specific decks
- **`b123456.0123456.ab`** - Starting hands (deterministic shuffle)
- **`0/1/0/6`** - Sequence of moves taken

Each directory contains:
- **`game.dot`** - Complete game state at this point
- **`path.txt`** - History: how you got here
- **`actions.txt`** - Options: what you can do next

### Reading the Files

**path.txt** shows the game history:
```
0: ink:p1.jasmine_resourceful_infiltrator.a
1: play:p1.mulan_disguised_soldier.a
0: end
6: ink:p2.elsa_spirit_of_winter.c
```

**actions.txt** shows your options:
```
0: play:p2.diablo_obedient_raven.d
1: end
```

Pick an action number, `just play <whole_path>` with that directory → new game state computed.

## Commands

```bash
# Create a matchup from two decks
just match data/decks/deck1.txt data/decks/deck2.txt

# Shuffle and draw starting hands (with seed for reproducibility)
just shuffle b013 "b123456.0123456.ab"

# Navigate to a state (computes it if needed)
just play output/b013/b123456.0123456.ab/0/1

# Start web viewer
just serve

# Clear all games
just clear
```

## What Works

- ✅ Ink cards, play characters, quest for lore, end turn
- ✅ Deterministic shuffle with reproducible seeds
- ✅ Lazy state computation (only compute paths you explore)
- ✅ Sequential action IDs (0, 1, 2...) - no collisions
- ✅ Navigation files (path.txt, actions.txt)
- ✅ Web viewer for visual exploration
- ✅ Recursive path building (`just play long/path/to/state` works)

## What Doesn't (Yet)

- ❌ Challenge characters
- ❌ Card abilities and effects
- ❌ Singing songs
- ❌ Win condition detection

## Example: Replaying a Game

```bash
# Start fresh
just clear

# Set up a specific matchup
just match data/decks/bs01.txt data/decks/rp01.txt

# Shuffle with known seed (reproducible)
just shuffle b013 "b123456.0123456.ab"

# Replay a sequence of moves
just play output/b013/b123456.0123456.ab/0/1/0/1/1/0/6

# See where you ended up
cat output/b013/b123456.0123456.ab/0/1/0/1/1/0/6/path.txt
```

The same seed + same moves = same game state. Perfect for playtesting, bug reports, or AI training data.

---

## [Advanced] How It Works

**Game state as a graph**: Nodes are cards/players/zones. Edges are relationships (card IN hand, player's TURN).

**Filesystem as game tree**: Each state is a directory. Actions are subdirectories. The tree structure mirrors possible game paths.

**On-demand computation**: Empty directories don't exist. Navigate to `0/` → system computes what happens, creates `game.dot`.

**Sequential action IDs**: Actions sorted deterministically, numbered 0, 1, 2... No hash collisions, easy indexing.

**Navigation files**: Human-readable summaries (path.txt, actions.txt) alongside machine-readable graph (game.dot).

For deep technical details (graph schema, state representation, AI/ML use cases) → see [ARCHITECTURE.md](ARCHITECTURE.md)

For playtesting and manual data capture → see [TESTING.md](TESTING.md)

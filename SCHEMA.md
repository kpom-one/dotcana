# DOTCANA Schema v0.1

## Overview

Dotcana represents Lorcana game state as a directed graph using DOT format. The system is composed of decoupled CLI tools that communicate through the filesystem.

## Architecture

```
     ┌──────────┐
     │  start   │  Initialize game from template + decks
     └────┬─────┘
          │
          ▼
     ┌──────────┐      ┌──────────────┐
     │   play   │─────▶│ rules-engine │  Apply mutations, compute CAN_*
     └────┬─────┘      └──────────────┘
          │
          ▼
    ┌────────────┐
    │ visualizer │  Render game state (future)
    └────────────┘
```

All tools communicate through one shared contract: **the DOT file**.

## Directory Structure

```
dotcana/
├── data/
│   ├── template.dot                 # Universal board structure (zones, players, OWNS)
│   ├── cards.json                   # Card database (name → stats, abilities, etc.)
│   └── decks/
│       └── *.txt                    # Deck lists (count + card name per line)
├── output/
│   └── <hash>/                      # Matchup directory (hash of deck contents)
│       ├── deck1.txt                # P1's decklist (copied from data/decks/)
│       ├── deck2.txt                # P2's decklist (copied from data/decks/)
│       ├── game.dot                 # Initial state (before shuffle)
│       └── <seed>/                  # Hand-spec seed (xxxxxxx.xxxxxxx.xx)
│           ├── deck1.dek            # P1's shuffled deck (53 cards, flat file)
│           ├── deck2.dek            # P2's shuffled deck (53 cards, flat file)
│           ├── game.dot             # State after shuffle (14 cards in hands)
│           ├── e35/                 # Empty action directory (end turn)
│           ├── i49/                 # Empty action directory (ink card)
│           ├── i64/                 # Empty action directory (ink card)
│           └── ...                  # One directory per legal action
│               └── (populated when action applied)
│                   ├── game.dot     # State after action
│                   ├── deck1.dek
│                   ├── deck2.dek
│                   └── <action>/    # Next action directories...
```

### Path as Game Log

The directory path encodes the complete game history:

```
output/b013/0123456.0123456.ab/i49/e35/p2c/game.dot
       │    └────seed─────┘  └─action sequence─┘
       └─matchup hash
```

- **Branching**: Explore alternate lines from any state
- **Replay**: Walk the path
- **Analysis**: Diff any two game.dot files
- **Card tracking**: Query card across all paths
- **Tab completion**: Action directories pre-created, browsable with `ls`

### Action IDs

Semantic hash-based format: `[prefix][xx]`

**Prefixes:**
- `e` - End turn (pass)
- `i` - Ink card
- `p` - Play card
- `q` - Quest
- `c` - Challenge
- `a` - Activate ability

**Hash:** 2-char MD5 hex of `from_node:to_node`

**Examples:**
- `e35/` - End turn
- `i49/` - Ink p1.jasmine_resourceful_infiltrator.a
- `p2c/` - Play p1.tipo_growing_son.a
- `c7a/` - Challenge attacker → target

**Properties:**
- ✓ Self-documenting (`ls` shows action types)
- ✓ Deterministic (same edge always gets same ID)
- ✓ Collision-resistant (256 possibilities per prefix)
- ✓ Stable across runs (hash-based, not order-based)

---

## Node Types

| type         | attributes                              | notes                                          |
| ------------ | --------------------------------------- | ---------------------------------------------- |
| `Game`       | `turn`                                  | Global game state                              |
| `Player`     | `lore`, `ink_drops`                     | Score and ink limit per turn                   |
| `Zone`       | `kind`                                  | hand, deck, play, inkwell, discard, bag        |
| `Card`       | `card_id`, `exerted`, `damage`, `label` | Card instance in game                          |
| `Effect`     | TBD                                     | Temporary modifications (rules engine creates) |
| `TargetPool` | `pick`                                  | Multi-target selection (future)                |

### Zone Kinds

- `hand` - Cards in hand
- `deck` - Draw pile (order matters)
- `play` - Cards in play area
- `inkwell` - Inked cards (exerted = used this turn)
- `discard` - Discard pile
- `bag` - Out-of-game storage

### Derived State

Some values are computed, not stored:

- **Total ink**: Count of cards IN inkwell zone
- **Used ink**: Count of cards IN inkwell WHERE exerted="1"
- **Available ink**: Total - Used

---

## Edge Types

### Structural Edges

| edge           | from → to     | meaning          |
| -------------- | ------------- | ---------------- |
| `CURRENT_TURN` | Game → Player | Whose turn it is |
| `OWNS`         | Zone → Player | Zone ownership   |
| `IN`           | Card → Zone   | Card location    |

### Action Edges (CAN\_\*)

These represent legal actions. Computed by rules engine.

| edge            | from → to     | meaning                          |
| --------------- | ------------- | -------------------------------- |
| `CAN_PASS`      | Player → Game | End turn                         |
| `CAN_PLAY`      | Card → Zone   | Play card from hand to play zone |
| `CAN_INK`       | Card → Zone   | Ink card from hand to inkwell    |
| `CAN_QUEST`     | Card → Game   | Quest for lore                   |
| `CAN_CHALLENGE` | Card → Card   | Challenge opposing character     |
| `CAN_ACTIVATE`  | Card → Target | Use activated ability            |

### Effect Edges (Future)

| edge         | from → to       | meaning                  |
| ------------ | --------------- | ------------------------ |
| `CREATED_BY` | Effect → Card   | Source of the effect     |
| `MODIFIES`   | Effect → Target | What the effect modifies |

---

## File Formats

**Note:** Examples below use `-[LABEL]->` shorthand for readability. Actual DOT syntax is `-> [label="LABEL"]`.

### template.dot

Universal game structure. Same for every game.

```dot
digraph lorcana {
    // Game node
    game [type="Game", turn="0"];

    // Players
    p1 [type="Player", lore="0", ink_drops="1"];
    p2 [type="Player", lore="0", ink_drops="1"];

    game -[CURRENT_TURN]-> p1;

    // Zones
    "z.p1.hand"    [type="Zone", kind="hand"];
    "z.p1.deck"    [type="Zone", kind="deck"];
    "z.p1.play"    [type="Zone", kind="play"];
    "z.p1.ink"     [type="Zone", kind="inkwell"];
    "z.p1.discard" [type="Zone", kind="discard"];

    "z.p2.hand"    [type="Zone", kind="hand"];
    "z.p2.deck"    [type="Zone", kind="deck"];
    "z.p2.play"    [type="Zone", kind="play"];
    "z.p2.ink"     [type="Zone", kind="inkwell"];
    "z.p2.discard" [type="Zone", kind="discard"];

    // Ownership
    "z.p1.hand"    -[OWNS]-> p1;
    "z.p1.deck"    -[OWNS]-> p1;
    "z.p1.play"    -[OWNS]-> p1;
    "z.p1.ink"     -[OWNS]-> p1;
    "z.p1.discard" -[OWNS]-> p1;

    "z.p2.hand"    -[OWNS]-> p2;
    "z.p2.deck"    -[OWNS]-> p2;
    "z.p2.play"    -[OWNS]-> p2;
    "z.p2.ink"     -[OWNS]-> p2;
    "z.p2.discard" -[OWNS]-> p2;
}
```

### deck.dek

Shuffled deck as flat file (card IDs, not graph nodes). Cards only become nodes when drawn.

```
tinker_bell_giant_fairy.a
tinker_bell_giant_fairy.b
tipo_growing_son.a
tipo_growing_son.b
// ... 53 cards remaining (7 drawn to hand)
```

Format: `{normalized_card_name}.{a|b|c|d}` (copy suffix for 4-of cards)

### game.dot

Complete game state. Assembled from template + decks + runtime state.

```dot
digraph lorcana {
    // --- Structure (from template) ---
    game [type="Game", turn="3"];
    p1 [type="Player", lore="4", ink_drops="1"];
    p2 [type="Player", lore="2", ink_drops="1"];
    // ... zones, OWNS edges ...

    // --- Cards (lazy creation when drawn) ---
    "p1.tinker_bell_giant_fairy.a" [type="Card", card_id="2188", exerted="0", damage="0", label="Tinker Bell - Giant Fairy"];
    // ... only cards in zones (not deck) ...

    // --- Card locations (runtime) ---
    "p1.tinker_bell_giant_fairy.a" -[IN]-> "z.p1.hand";
    "p1.tipo_growing_son.a" -[IN]-> "z.p1.play";
    // ...

    // --- Actions (computed by rules engine) ---
    "p1.tinker_bell_giant_fairy.a" -[CAN_PLAY]-> "z.p1.play";
    "p1.tinker_bell_giant_fairy.a" -[CAN_INK]-> "z.p1.ink";
    "p1.tipo_growing_son.a" -[CAN_QUEST]-> game;
    "p1.tipo_growing_son.a" -[CAN_CHALLENGE]-> "p2.elsa_the_fifth_spirit.a";
    p1 -[CAN_PASS]-> game;
}
```

---

## CLI Tools

### match

Initialize a matchup from two deck files.

```bash
just match data/decks/deck1.txt data/decks/deck2.txt
# Creates 4-char hash from deck contents (not file paths)
# Creates output/<hash>/
# Copies deck1.txt, deck2.txt to matchup directory
# Loads template.dot and card database
# Outputs: output/<hash>/game.dot (initial state before shuffle)
```

### shuffle

Shuffle decks and draw starting hands using a hand-spec seed.

```bash
just shuffle <hash> <seed>
# Example: just shuffle b013 "0123456.0123456.ab"
# Seed format: xxxxxxx.xxxxxxx.xx
#   - First 7 chars: P1's hand (indices 0-9a-z into deck1.txt)
#   - Second 7 chars: P2's hand (indices 0-9a-z into deck2.txt)
#   - Last 2 chars: RNG suffix for shuffling remainder
# Creates: output/<hash>/<seed>/deck1.dek, deck2.dek, game.dot
# Cards in hands are created as nodes; remaining 53 in .dek files
```

### show

Display game state and available actions.

```bash
just show <hash> [<seed>]
# Examples:
#   just show b013                     # Before shuffle
#   just show b013 0123456.0123456.ab  # After shuffle
# Lists all CAN_* edges (legal actions)
```

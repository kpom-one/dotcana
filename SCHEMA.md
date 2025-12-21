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
├── template.dot                     # Universal board structure (zones, players, OWNS)
├── all_cards.json                   # Card database (name → stats, abilities, etc.)
├── SCHEMA.md                        # This file
│
├── matchup_<name>/
│   ├── deck1.dotfrag                # P1's card instances
│   ├── deck2.dotfrag                # P2's card instances
│   └── <seed>/
│       └── game.dot                 # Initial state (shuffled, hands drawn)
│           └── <action>/
│               └── game.dot         # State after action
│                   └── <action>/
│                       └── game.dot # And so on...
```

### Path as Game Log

The directory path encodes the complete game history:

```
matchup_x/99281/a0/b2/a1/c0/game.dot
         │      └─────────┘
         │           │
         seed    action sequence (game log)
```

- **Branching**: Explore alternate lines from any state
- **Replay**: Walk the path
- **Analysis**: Diff any two game.dot files
- **Card tracking**: Query card across all paths

### Action IDs

Two base36 characters (0-9, a-z): `a0/`, `b1/`, `zz/`

- 1296 unique IDs per game state (plenty for available actions)
- 3 characters per directory level
- Sufficient for 200-300 action games

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

### template.dot

Universal game structure. Same for every game.

```dot
digraph lorcana {
    // Game node
    GAME [type="Game", turn="0"];

    // Players
    P1 [type="Player", lore="0", ink_drops="1"];
    P2 [type="Player", lore="0", ink_drops="1"];

    GAME -[CURRENT_TURN]-> P1;

    // Zones
    Z_P1_HAND    [type="Zone", kind="hand"];
    Z_P1_DECK    [type="Zone", kind="deck"];
    Z_P1_PLAY    [type="Zone", kind="play"];
    Z_P1_INK     [type="Zone", kind="inkwell"];
    Z_P1_DISCARD [type="Zone", kind="discard"];

    Z_P2_HAND    [type="Zone", kind="hand"];
    Z_P2_DECK    [type="Zone", kind="deck"];
    Z_P2_PLAY    [type="Zone", kind="play"];
    Z_P2_INK     [type="Zone", kind="inkwell"];
    Z_P2_DISCARD [type="Zone", kind="discard"];

    // Ownership
    Z_P1_HAND    -[OWNS]-> P1;
    Z_P1_DECK    -[OWNS]-> P1;
    Z_P1_PLAY    -[OWNS]-> P1;
    Z_P1_INK     -[OWNS]-> P1;
    Z_P1_DISCARD -[OWNS]-> P1;

    Z_P2_HAND    -[OWNS]-> P2;
    Z_P2_DECK    -[OWNS]-> P2;
    Z_P2_PLAY    -[OWNS]-> P2;
    Z_P2_INK     -[OWNS]-> P2;
    Z_P2_DISCARD -[OWNS]-> P2;
}
```

### deck.dotfrag

Card instances for one player. Fragment (not complete graph).

```dot
// Player 1 deck - 60 cards
D1_01 [type="Card", card_id="2188", exerted="0", damage="0", label="Tinker Bell - Giant Fairy"];
D1_02 [type="Card", card_id="2188", exerted="0", damage="0", label="Tinker Bell - Giant Fairy"];
// ... 60 total
```

### game.dot

Complete game state. Assembled from template + decks + runtime state.

```dot
digraph lorcana {
    // --- Structure (from template) ---
    GAME [type="Game", turn="3"];
    P1 [type="Player", lore="4", ink_drops="1"];
    P2 [type="Player", lore="2", ink_drops="1"];
    // ... zones, OWNS edges ...

    // --- Cards (from dotfrags) ---
    D1_01 [type="Card", card_id="2188", exerted="0", damage="0", label="Tinker Bell - Giant Fairy"];
    // ... all 120 cards ...

    // --- Card locations (runtime) ---
    D1_01 -[IN]-> Z_P1_HAND;
    D1_02 -[IN]-> Z_P1_DECK;
    D1_03 -[IN]-> Z_P1_PLAY;
    // ...

    // --- Actions (computed by rules engine) ---
    D1_01 -[CAN_PLAY]-> Z_P1_PLAY;
    D1_01 -[CAN_INK]-> Z_P1_INK;
    D1_03 -[CAN_QUEST]-> GAME;
    D1_03 -[CAN_CHALLENGE]-> D2_07;
    P1 -[CAN_PASS]-> GAME;
}
```

---

## CLI Tools

### start

Initialize a game from template and decks.

```bash

just match decks/1.txt decks/2.txt
# create a 4 char matchup hash
# mkdir output/<hash>
# runs data/decks/txt_to_dotfrag.py
#   output -> output/<hash>/a.dotfrag output/<hash>/b.dotfrag


just shuffle <hash> <seed>
# mkdir output/<hash>/<seed>
# Call RulesEngine
#   output -> output/<hash>/<seed>/game.dot
#   this will have N actions

just play <hash> <seed> <action_list>
# TODO: Walk backwards to only play the necessary things
# current = output/<hash>/<seed>

# for action in action_list.split("/")
#     current += "/" + action

#     if exists(current + "/game.dot")
#       continue

#     if not dir_exists(current):
#        mkdir current

#     Call RulesEngine
#        output -> current + "/game.dot"

```

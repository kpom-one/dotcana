# Lorcana Keywords Reference

All 15 keyword abilities from the comprehensive rules.

---

## Simple Keywords (No Parameters)

### 1. Rush
**Rule:** This character can challenge the turn they're played
**Mechanic:** Ignores the "drying" restriction for challenging
**Implementation:** Boolean flag, check in `compute_can_challenge`

### 2. Evasive
**Rule:** Only characters with Evasive can challenge this character
**Mechanic:** Challenging restriction
**Implementation:** Boolean flag, check in `compute_can_challenge` target selection

### 3. Reckless
**Rule:** Can't quest. Must challenge each turn if able
**Mechanic:** Two static abilities (quest restriction + challenge requirement)
**Implementation:** Boolean flag, check in `compute_can_quest` and turn-end validation

### 4. Bodyguard
**Rule:** May enter play exerted. Opponent must challenge Bodyguard characters first if able
**Mechanic:** Replacement effect on play + challenging restriction
**Implementation:** Boolean flag, check in `execute_play` and `compute_can_challenge` target selection

### 5. Ward
**Rule:** Opponents can't choose this card when resolving an effect
**Mechanic:** Targeting restriction (doesn't prevent challenges)
**Implementation:** Boolean flag, check when effects target cards

### 6. Alert
**Rule:** Can challenge characters with Evasive
**Mechanic:** Ignores Evasive restriction
**Implementation:** Boolean flag, check in `compute_can_challenge`

---

## Stackable Keywords (Have +N Values)

### 7. Challenger +N
**Rule:** While challenging, this character gets +N Strength
**Mechanic:** Stat modifier during challenges only
**Implementation:** Integer value, add to strength in `execute_challenge`

### 8. Resist +N
**Rule:** Damage dealt to this card is reduced by N
**Mechanic:** Replacement effect for damage
**Implementation:** Integer value, apply in `damage_card()`

---

## Triggered Ability Keywords

### 9. Support
**Rule:** Whenever this character quests, you may add their Strength to another character's Strength this turn
**Mechanic:** Triggered ability on quest
**Implementation:** Triggered ability → Bag system required

### 10. Vanish
**Rule:** When an opponent chooses this character for an action, banish them
**Mechanic:** Triggered ability on targeting
**Implementation:** Triggered ability → Bag system required

---

## Alternate Cost Keywords

### 11. Shift [N]
**Rule:** You may pay [N] to play this on top of one of your characters named [Name]
**Mechanic:** Alternate play cost, creates card stack
**Implementation:** Alternate cost system + stack tracking (under/on top)

**Variants:**
- **[Classification] Shift** - Shift onto any character with specified classification (e.g., "Dreamborn Shift")
- **Universal Shift** - Shift onto any character

### 12. Singer [N]
**Rule:** This character counts as cost N to sing songs
**Mechanic:** Alternate cost for song actions
**Implementation:** Song system + alternate costs

### 13. Sing Together [N]
**Rule:** Exert characters with total cost N+ to sing this song for free
**Mechanic:** Multi-character alternate cost
**Implementation:** Song system + cost calculation

---

## Advanced Keywords (Complex Mechanics)

### 14. Boost [N] {I}
**Rule:** Once per turn, pay N ink to put top card of deck facedown under this card
**Mechanic:** Activated ability, creates stack
**Implementation:** Activated abilities + stack tracking + facedown cards

### 15. Universal Shift
**Rule:** Shift onto any character (not just same name)
**Mechanic:** See Shift variants above
**Implementation:** Same as Shift but no name restriction

---

## Implementation Complexity Tiers

**Tier 1 - Easy (Boolean Flags):**
- Rush, Evasive, Reckless, Bodyguard, Ward, Alert

**Tier 2 - Medium (Stat Modifiers):**
- Challenger +N, Resist +N

**Tier 3 - Hard (Triggered Abilities):**
- Support, Vanish
- **Requires:** Bag system, triggered ability infrastructure

**Tier 4 - Very Hard (Alternate Costs):**
- Shift, Singer, Sing Together, Boost
- **Requires:** Alternate cost system, song mechanics, stack tracking

---

## Dependencies

```
graph TD
    A[Boolean Keywords] --> B[Stat Keywords]
    B --> C[Triggered Keywords]
    C --> D[Alternate Cost Keywords]

    C -.requires.-> E[Bag System]
    D -.requires.-> F[Song System]
    D -.requires.-> G[Stack System]
```

**Recommendation:** Implement in tier order (1 → 2 → 3 → 4)

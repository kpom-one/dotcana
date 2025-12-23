# Lorcana Engine Implementation Roadmap

## Status: Architecture Validated ✅
Current foundation (graph + zones + state-based effects) supports full game rules without refactoring.

---

## Phase 1: Core Game Systems (Priority: Critical)

1. **The Bag** - Queue for triggered abilities ("When you play this card...", "Whenever this quests...")
2. **Static Abilities** - Continuous effects ("+2 Strength", "Can't be challenged", etc.)
3. **Turn Phases** - Beginning (Ready/Set/Draw), Main, End of Turn structure
4. **Keywords (Top 5)** - Rush, Evasive, Challenger, Bodyguard, Resist

**Result:** ~80% of cards become playable

---

## Phase 2: Feature Complete (Priority: High)

5. **Songs** - Exert characters to play songs for free (Singer keyword)
6. **Remaining Keywords** - Ward, Shift, Reckless, Support, etc. (10 more)
7. **Locations** - New card type with move mechanics and unique challenge rules
8. **Activated Abilities** - "{Exert}: Do something" effects on Items and Characters

**Result:** All card types and mechanics implemented

---

## Phase 3: Competitive Play (Priority: Medium)

9. **Advanced Keywords** - Alert, Boost, Vanish, Classification Shift variants
10. **Cost Modifiers** - Cards that reduce/increase costs of other cards
11. **Complex Interactions** - Edge cases, timing windows, priority resolution

**Result:** Tournament-ready rules engine

---

## Implementation Estimate
- **Lines of Code:** ~1500-2000 additional (current: ~1000)
- **Architecture Changes:** Minimal - mostly additive
- **Complexity:** Similar to Hearthstone, simpler than Magic: The Gathering

# Spellbook

Generates a spellbook in markdown format.

Run with:

```
python3 spellbook.py
```

optionally passing an output filename (defaults to `spellbook.md`).

## Generation

1. Pick a title
2. Pick three to ten ingredients (sorted into solid, liquid, weight, or intangible)
3. List directions
4. For each ingredient, select an amount (measurement/count based on type)
5. For each ingredient, there is a 5% chance of giving it a variant
6. For each ingredient, there is a 30% chance of giving it a method of preparation
7. For each ingredient, there is a 10% chance of prefacing it with "While [doing this action]..."
8. There is a 20% chance of ending with a final action (snapping fingers, dancing on toes)
9. There is a 10% chance of ending with a caution (do not attempt if/unless...)

Keep generating spells until you hit your wordcount

## Elements

### Titles

[Gerund] Spell
[Gerund] Enchantment
[Gerund] Curse
[Gerund] Cure
[Gerund] Rite
Cure for a [Major/Minor/Intermediate] [Ache/Wart/Disturbance] of the [Body Part]
Curse of [Major/Minor/Intermediate] [Ache/Wart/Disturbance] of the [Body Part]

Invocation of [Adjective]
Cure for [Adjective]
Curse of [Adjective]
Rite of [Noun form of Adjective]
+X Enchantment of [Adjective]
-X Curse of [Adjective]

...

### Ingredients

List of ingredients, with types (solid, liquid) and variants (cracked, cursed, pristine, cloudy, pure, chipped, viscous)

### Amounts

Amounts (3 measures, 12 ounces, 2 pinches)

### Actions

List of actions to take (while standing on/flexing one/two/three [foot/feet/leg/legs/hand/hands/arm/arms/tentacle/tentacles/pseudopod/pseudopodia/proboscis/proboscides)

### Cautions

do not do X when Y
[full moon, when wearing black hat, blond haired assistant]

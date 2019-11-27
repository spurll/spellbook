#!/usr/bin/python3

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-ShareAlike 4.0 International License.

import argparse
import yaml
import re
from os import path
from random import choice, randint

from maybe import flip, maybe, choice_without
from words import name, capitalize, uncapitalize, titlecase, oxford, wordcount
from words import indefinite, plural


CONFIG = 'config.yml'
BOOKS = 'books.yml'
SPELLS = 'spells.yml'
FIGURES = 'figures.yml'
LOCALES = 'locales.yml'
ACTIONS = 'actions.yml'
COMPONENTS = 'components.yml'
MATERIALS = 'materials.yml'

TARGET = 50000

resources = path.join(path.abspath(path.dirname(__file__)), 'resources')


def load_yaml(file):
    with open(file, 'r', encoding='utf8') as f:
        return yaml.load(f)


# Load configuration and dictionaries
config = load_yaml(path.join(resources, CONFIG))
books = load_yaml(path.join(resources, BOOKS))
spells = load_yaml(path.join(resources, SPELLS))
figures = load_yaml(path.join(resources, FIGURES))
locales = load_yaml(path.join(resources, LOCALES))
actions = load_yaml(path.join(resources, ACTIONS))
components = load_yaml(path.join(resources, COMPONENTS))
materials = load_yaml(path.join(resources, MATERIALS))

parts = [
    k for k, v in components['parts']['animal'].items()
    if v != 'intangible'
]

summons = [
    k for k, v in components['ingredients'].items()
    if v['type'] in ('animal', 'plant', 'fungus')
]

counts = ['¼', '½', '¾'] + list(range(1, 9))
plurals = [False] * 4 + [True] * 7


def generate(outfile):
    authors = [name() for _ in range(7)]
    author = authors[0]
    title = generate_title(author)
    prologue, epilogue = generate_frame()
    pages = [generate_cover(title, authors)]

    while wordcount(prologue, epilogue, *pages) < TARGET:
        pages.append(generate_page(authors))

    book = f'# {title}\n\n' + '\n\n---\n\n'.join((prologue, *pages, epilogue))

    print('Spellbook complete.\n')
    print(f'Title: {title}')
    print(f'Author: {author}')
    print(f'Length: {len(pages)} spells, {wordcount(book)} words\n')

    print(f'Writing output to {outfile}...')

    with open(outfile, 'w', encoding='utf8') as f:
        f.write(book)

    print('Done.')


def generate_title(author):
    book = choice(books['books'])

    if flip():
        book = f"{choice(books['attributes'])} {book}"

    subjects = [s for c in spells['spells'].values() for s in c]
    subject = choice(subjects)

    if flip():
        subject = ' and '.join((
            plural(subject),
            choice_without(subjects, subject.lower())
        ))

    subject = plural(subject)

    if flip():
        subject = f"{choice(spells['attributes'])} {subject}"

    if flip():
        return titlecase(f"{author}'s {book} {subject}")

    if flip():
        return titlecase(f"{book} {name()}'s {subject}")

    return titlecase(f'{book} {subject}')


def generate_frame():
    gender = choice(list(figures['genders'].values()))
    figure = gender['noun']
    pronouns = gender['pronouns']
    attribute = choice(figures['attributes'])
    locale = choice(locales['locales'])

    # Prologue
    prologue = ' '.join((
        indefinite(attribute).capitalize(),
        figure,
        choice(['crept into', 'strode into', 'stole into', 'entered']),
        indefinite(choice(locales['attributes'])),
        f'{locale}, '
    ))

    companion = choice(figures['companions']['types']) if flip() else None

    if companion:
        prologue += ' '.join((
            'accompanied by',
            indefinite(choice(figures['companions']['attributes'])),
            f'{companion}. '
        ))
    else:
        prologue += f'{choice(figures["dress"])}. '

    prologue += (
        f'{pronouns[0].capitalize()} stopped as {pronouns[2]} eyes lit upon '
        f'the object of {pronouns[2]} quest. '
    )

    if flip():
        prologue += (
            f'The {figure} suddenly surged forward and grasped the tome '
            'eagerly. '
        )
    else:
        prologue += (
            f'The {figure} began to move again, approaching the tome warily. '
        )

    prologue += (
        f'{pronouns[0].capitalize()} lifted it from its resting place, then '
        'opened its cover and began to read.'
    )

    # Epilogue
    epilogue = ' '.join((
        f'The {attribute} {figure} closed the book.',
        f'Rising to {pronouns[2]} feet,',
        f'{pronouns[0]} beckoned to {pronouns[2]} {companion} and set out'
        if companion else f'{pronouns[0]} left the {locale}',
        f'in search of components.'
    ))

    return prologue, epilogue


def generate_cover(title, authors):
    cover = f'## {title}\n\n### {authors[0]}'

    if maybe(0.2):
        cover += f'\n\n{choice(books["editions"]).capitalize()} Edition'

    for role in books['roles']:
        if maybe(0.2):
            cover += f'\n\n{role.capitalize()} by {name()}'

    contributors = oxford(authors[2:])
    cover += f'\n\nWith thanks to {contributors} for their contributions.'

    return cover


def generate_page(authors):
    # Generate spell title
    spell = choice(list(spells['spells'].keys()))
    title = choice(spells['spells'][spell])

    afflicted = choice(parts) if spell in ('blight', 'cure') else None
    target = plural(choice(summons))

    if flip():
        title = f'{choice(spells["attributes"])} {title}'

    if spell == 'cure':
        title += ' for '
    else:
        title += ' of '

    if spell == 'summoning':
        title += target
    elif spell in ('blight', 'cure'):
        title += f'{choice(spells["maladies"])} {afflicted}'
    else:
        title += choice(spells['subjects'])

    if maybe(0.2):
        title = f"{choice(authors).split()[0]}'s {title}"

    title = titlecase(title)

    # Generate list of ingredients
    items, ingredients = generate_ingredients()
    ingredients = f'\n* ' + '\n* '.join(ingredients)

    # Generate directions
    directions = generate_directions(items, spell, afflicted, authors, target)

    page = '\n\n'.join((
        f'## {title}',
        f'### Ingredients\n{ingredients}',
        f'### Directions\n\n{directions}',
    ))

    return page


def generate_ingredients():
    items, ingredients = [], []

    for _ in range(randint(3, 10)):
        item, ingredient = pick_ingredient()
        items.append(item)
        ingredients.append(ingredient)

    return items, ingredients


def pick_ingredient():
    # This is horrifyingly inefficient
    item = choice(list(components['ingredients'].items()))
    item[1]['name'] = item[0]
    item = item[1]

    part = (
        choice(list(components['parts'][item['type']].items()))
        if item['parts'] else None
    )

    # Item types: animal, plant, fungus, solid, liquid, intangible
    # Part types: solid, liquid, intangible
    type = part[1] if part else item['type']

    attributes = components['attributes']['general']

    if type != 'intangible':
        count, pluralize = choice(list(zip(counts, plurals)))
    else:
        count, pluralize = None, False

    if type in ('solid', 'liquid'):
        # Note no +=! For lists, += modifies the original list!
        attributes = attributes + components['attributes'][type]
        attribute = choice(attributes) if maybe(0.25) else None
        measure = choice(components['measures'][type])

        ingredient = f'{part[0]} of {item["name"]}' if part else item['name']

        item = {'item': ingredient, 'type': type}

        ingredient = ' '.join((
            str(count),
            plural(measure) if pluralize else measure,
            f'{attribute} {ingredient}' if attribute else ingredient,
        ))

        if maybe(0.2):
            ingredient += f', {choice(components["preparations"][type])}'

    else:
        ingredient = item['name']

        if part:
            ingredient = f'{part[0]} of {ingredient}'
        elif type == 'animal' and flip():
            ingredient = f'live {ingredient}'

        if pluralize:
            ingredient = plural(ingredient)

        item = {'item': ingredient, 'type': type}

        if maybe(0.25):
            ingredient = f'{choice(attributes)} {ingredient}'

        if count:
            ingredient = f'{count} {ingredient}'

    return item, ingredient


def generate_directions(items, spell, afflicted, authors, target):
    liquid = [i['item'] for i in items if i['type'] == 'liquid']
    solid = [i['item'] for i in items if i['type'] == 'solid']
    other = [i['item'] for i in items if i['type'] not in ('solid', 'liquid')]

    directions = initial(type, liquid) + '\n\n'

    if liquid and solid and flip():
        # Group liquids and solids, then add anything else
        directions += grouped_directions(liquid, solid, other)
    else:
        # Add each ingredient individually
        directions += individual_directions(items)

    if flip():
        directions += '\n\n' + final(spell, afflicted, liquid, authors, target)

    return directions


def grouped_directions(liquid, solid, other):
    directions = choice([
        f'Combine {oxford(liquid)}.',
        f'Add {oxford(liquid)}, stirring gently.',
        f'Beat together {oxford(liquid)} until frothy.',
        f'Pour {oxford(liquid)} into prepared vessel.',
    ])

    if maybe(0.33):
        directions += ' Bring to a boil, stirring ' + choice([
            'vigorously.', 'continuously.', 'occasionally.',
            'intermittently.', 'once.'
        ])
    elif flip():
        directions += (
            ' Lower the temperature until the mixture begins to congeal.'
        )

    next_direction = choice([
        f'Stir in {oxford(solid)}, individually.',
        f'Blend in {oxford(solid)}, stirring until fully dissolved.',
        f'Add {oxford(solid)}.' + (' Do not overmix.' if flip() else ''),
        f'Beat in {oxford(solid)} until only a few chunks remain.',
    ])

    directions += '\n\n' + optional_action(next_direction)

    if other:
        next_direction = ' '.join([
            choice([
                f'Add {i}.',
                f'Carefully add {i}.',
                f'Cautiously add {i}.',
                f'Blend in {i}.',
                f'Fold in {i}.',
                f'Combine with {i}.',
                f'Add {i} and mix thoroughly.',
            ]) for i in other
        ])

        directions += '\n\n' + optional_action(next_direction)

    return directions


def individual_directions(items):
    directions = choice([
        f'Start with {items[0]["item"]}.',
        f'To begin, add {items[0]["item"]}.',
        f'First, add {items[0]["item"]}.',
        f'Add {items[0]["item"]} to the prepared vessel.',
    ])

    for i in items[1:]:
        if i['type'] == 'liquid':
            next_direction = choice([
                f'Add {i["item"]}.',
                f'Pour in {i["item"]}.',
                f'Mix in {i["item"]}.',
            ]) + (
                f' Stir {choice(["vigorously", "gently", "once"])}.'
            if flip() else '')

        elif i['type'] == 'solid':
            next_direction = choice([
                f'Add {i["item"]}.',
                f'Mix in {i["item"]}.',
                f'Fold in {i["item"]}.',
            ])

        else:
            next_direction = choice([
                f'Add {i["item"]}.',
                f'Carefully add {i["item"]}.',
                f'Cautiously add {i["item"]}.',
                f'Blend in {i["item"]}.',
                f'Fold in {i["item"]}.',
                f'Combine with {i["item"]}.',
                f'Add {i["item"]} and mix thoroughly.',
            ])

        directions += '\n\n' if maybe(0.2) else ' '
        directions += optional_action(next_direction, 0.2)

    return directions


def optional_action(direction, chance=0.5):
    return action() + uncapitalize(direction) if maybe(chance) else direction


def action():
    limb = choice(actions['limbs'])
    limbs = choice([
        f'one {limb}',
        f'two {plural(limb)}',
        f'three {plural(limb)}',
    ])

    options = [f'While {a}, ' for a in actions['actions']['general']]

    options += [f'While {a} {limbs}, ' for a in actions['actions']['limb']]

    # Add additional actions that too complicated to put in the YAML file
    # without causing a headache
    options += [
        f'Raise {limbs} and gesticulate wildly, then ',

        f'While waving {indefinite(limb)} slowly over the mixture, ',

        f'Snap your fingers {choice(["once", "twice", "thrice"])}, then ',

        f'Gesture vaguely to the {choice(["north", "south", "east", "west"])},'
        ' then ',

        f'While working your fingers in a {"counter" if flip() else ""}'
        'clockwise spiral, ',

        f'Wriggle your {choice(["fingers", "toes"])}, then ',
    ]

    return choice(options)


def initial(type, liquid):
    stone = choice(materials['stone'])
    metal = choice(materials['metal'])
    fabric = choice(materials['fabric'])
    hard = choice(materials['hardwood'])
    soft = choice(materials['softwood'])
    
    if flip():
        wood, backup = hard, choice_without(materials['hardwood'], hard)
    else:
        wood, backup = soft, choice_without(materials['softwood'], soft)

    options = [
        'Prepare a ' + choice(['broad ', 'narrow ', 'shallow ', 'deep ']) +
        choice([
            f'{stone} mortar and pestle.',
            f'{metal} mortar and pestle.',
            f'{wood} mortar and pestle.',
            f'wooden mortar and pestle ({wood} preferred, though {backup} will'
            ' do).',
        ]),

        f'Heat a cauldron over a well-banked fire of {wood}' +
        (f' and {backup}.' if flip() else '.')
        if liquid else None,

        f'Place {indefinite(metal)} boiler over a brazier and etch with runes '
        'while it heats.'
        if liquid else None,

        'Array components on {indefinite(fabric)} sheet according to gestalt '
        'principles.'
        if not liquid else None,

        f'Ready {indefinite(fabric)} sack for mixing.'
        if not liquid else None,

        'Ready a vessel composed of a ' + choice(['non-', '']) +
        'ferromagnetic metal (if unsure of its composition, test with a '
        'lodestone).'
        if flip() else None,

        f'Ready {indefinite(choice([stone, metal, wood]))} vessel and ' +
        choice([
            'chill until frost is just visible.',
            'heat until the bottom begins to scorch.',
        ]),
    ]

    direction = choice([o for o in options if o])

    if flip():
        options = [
            'On a ' + choice(['misty', 'cloudy', 'rainy', 'dry', 'humid']) +
            choice([' morning', ' day', ' afternoon', ' evening', ' night']),

            'Facing ' + choice(['north', 'south', 'east', 'west']),

            'Under a ' +
            choice(['waxing', 'waning', 'gibbous', 'crescent', 'full', 'new'])
            + ' moon',

            'With a ' + choice(['rising ', 'setting ']) + choice([
                'sun', 'moon', 'Mercury', 'Mars', 'Venus',
            ]) + ' in the sky',

            'Under the sign of ' + choice([
                'Capricorn', 'Gemini', 'Pisces', 'Virgo', 'Cancer', 'Leo',
                'Aquarius', 'Taurus', 'Libra', 'Scorpius', 'Aries',
                'Sagittarius', 'Ophiuchus', 'Cassiopeia', 'Orion'
            ]),

            'After aligning yourself ' + choice(['parallel', 'perpendicular'])
            + ' to the ' + choice(['governing', 'major', 'minor']) + ' leyline'
        ]

        direction = f'{choice(options)}, {uncapitalize(direction)}'

    return direction


def final(type, afflicted, liquid, authors, target):
    # Even though it's inefficient, build every possible set of directions,
    # then choose one, because otherwise the code becomes very bad
    options = [
        'Heat until all of the liquid has boiled away and the black fumes have'
        ' blotted out the great and minor lights of the sky.',

        'Take a handful and scatter it in a loose circle.',

        'Take a fistful and scatter it to the wind.',

        'Take a pinch between thumb and forefinger and inhale deeply.',

        'Paint face, arms, and chest with the compound. The spell will take '
        'hold within seconds.',

        'Hum softly as you scatter the contents.',

        'Move one forefinger through the mixture, making the approved sigils '
        'and signs, then discard.',

        f"Chant your preferred invocations over the compound ({authors[1]}'s" + 
        (' Poem of Power' if flip() else ' Song of Sanctity') +
        ' recommended), then reserve for future use.',

        'The mixture should be shaken, then imbibed while making the '
        'appropriate runic gestures with the left hand.',

        f'Speak the seven forbidden words, then submerge one arm in the '
        'compound up to the elbow and withdraw.'
        if type not in ('curse', 'blight', 'cure') and liquid else None,

        'Bring to a rolling boil and have the subject inhale the vapours for '
        f'{srange()} hours, or until the illness passes.'
         if type == 'cure' and liquid else None,

        f'Bring to a rolling boil and steep a length of bandage for {srange()}'
        ' hours.' + ('Still hot, ' if flip() else 'Let cool, then ') +
        f'apply the bandages to {afflicted}, wrapping ' +
        ('tightly.' if flip() else 'loosely.')
        if type == 'cure' and liquid else None,

        f"Make a poultice using {authors[2]}'s standard method. Apply to "
        f'{afflicted} immediately.'
        if type == 'cure' and liquid else None,

        f'With {"gloved" if flip() else "bare"} hands, fold a small measure of'
        ' the curative into an equal amount of wax or tallow, the massage into'
        f" the subject's {afflicted}."
        if type == 'cure' else None,

        f'With {"gloved" if flip() else "bare"} hands, apply the curative to '
        f'the {afflicted} directly, then bandage.'
        if type == 'cure' else None,

        'Sprinkle a loose handful of the compound over the subject' +
        (f"'s {afflicted}," if type in ('cure', 'curse') else ',') +
        (
            ' mouthing the standard invocations.' if flip() else
            ' forming the standard signs with the left hand.'
        ) if type not in ('general', 'summoning') else None,

        f'Ensure that the subject ingests the compound within {srange()} '
        'hours for maximum effectiveness.'
        if type not in ('general', 'summoning') else None,

        'Apply directly to the forehead.'
        if type not in ('general', 'summoning') else None,

        f"Following {authors[3]}'s three maxims, create a wax simulacrum of the"
        ' target. Submerge in the brew, and boil until all liquid has '
        'evaporated.'
        if type in ('curse', 'blight') and liquid else None,

        f"Following {authors[4]}'s four precepts, create a cloth manikin of the"
        ' target. Coat liberally with the compound, then burn. Scatter the '
        'ashes.'
        if type in ('curse', 'blight') else None,

        "Take a single strand of the target's hair, break it in two, and add "
        'it to the concoction, mixing thoroughly.'
        if type in ('curse', 'blight') else None,

        'Dig a hole six feet deep and bury. Excavate after the spring thaw.'
        if type == 'general' else None,
    ]

    direction = choice([o for o in options if o])

    if type == 'summoning':
        direction += (
            f' {srange()} {target} should begin to appear within ' +
            ('seconds.' if flip() else 'minutes.' if flip() else 'hours.')
        )

    return direction


def srange():
    start = randint(1, 5)
    return f'{start} to {start + randint(start + 1, start + 3)}'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'outfile',
        help='The output file. Defaults to spellbook.md.',
        nargs='?',
        default='spellbook.md'
    )

    args = parser.parse_args()

    generate(args.outfile)


if __name__ == '__main__':
    main()

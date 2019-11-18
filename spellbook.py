#!/usr/bin/python3

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-ShareAlike 4.0 International License.

import argparse
import yaml
import re
from os import path
from random import choice, randint

from words import name, titlecase, wordcount, indefinite, plural
from maybe import flip, maybe, choice_without


CONFIG = 'config.yml'
BOOKS = 'books.yml'
SPELLS = 'spells.yml'
FIGURES = 'figures.yml'
LOCALES = 'locales.yml'
ACTIONS = 'actions.yml'
COMPONENTS = 'components.yml'

#TARGET = 50000
TARGET = 500

basedir = path.abspath(path.dirname(__file__))


def load_yaml(file):
    with open(file, 'r', encoding='utf8') as f:
        return yaml.load(f)


# Load configuration and dictionaries
config = load_yaml(path.join(basedir, CONFIG))
books = load_yaml(path.join(basedir, BOOKS))
spells = load_yaml(path.join(basedir, SPELLS))
figures = load_yaml(path.join(basedir, FIGURES))
locales = load_yaml(path.join(basedir, LOCALES))
actions = load_yaml(path.join(basedir, ACTIONS))
components = load_yaml(path.join(basedir, COMPONENTS))

parts = [p for p in components['parts']['animal']]

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
        'stole into',
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

    authors = ', '.join(authors[1:-2]) + f', and {authors[-1]}'
    cover += f'\n\nWith thanks to {authors} for their contributions.'

    return cover


def generate_page(authors):
    # Generate spell title
    type = choice(list(spells['spells'].keys()))
    title = choice(spells['spells'][type])

    afflicted = choice(parts) if type in ('blight', 'cure') else None

    if flip():
        title = f'{choice(spells["attributes"])} {title}'

    if type == 'cure':
        title += ' for '
    else:
        title += ' of '

    if type == 'summoning':
        title += plural(choice(summons))
    elif type in ('blight', 'cure'):
        title += f'{choice(spells["maladies"])} {afflicted}'
    else:
        title += choice(spells['subjects'])

    if maybe(0.2):
        title = f"{choice(authors).split()[0]}'s {title}"

    title = titlecase(title)

    # Generate list of ingredients
    items = []
    ingredients = ''
    directions = ''

    for _ in range(randint(3, 10)):
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

            current = f'{part[0]} of {item["name"]}' if part else item['name']

            items.append({'ingredient': current, 'type': type})

            current = ' '.join((
                str(count),
                plural(measure) if pluralize else measure,
                f'{attribute} {current}' if attribute else current,
            ))

            if maybe(0.2):
                current += f', {choice(components["preparations"][type])}'

        else:
            current = item['name']

            if part:
                current = f'{part[0]} of {current}'
            elif type == 'animal' and flip():
                current = f'live {current}'

            if pluralize:
                current = plural(current)

            items.append({'ingredient': current, 'type': type})

            if maybe(0.25):
                current = f'{choice(attributes)} {current}'

            if count:
                current = f'{count} {current}'

        ingredients += f'* {current}\n'

    for i in items:
        pass

    # If contains liquid, "pour in... stirring constantly/occasionally"
    # flip() heat cauldron over
    # dig a hole six foot by three

    # Generate directions
    # TODO: Add directions (e.g., on a misty morning, facing west, facing a rising Mercury, under the sign of Sagitarius)

    # TODO: Add cautions

    # Even though it's inefficient, build every possible set of directions,
    # then choose one, because otherwise the code becomes very bad
    liquid = any(i['type'] == 'liquid' for i in items)
    time = randint(1, 5)
    time = f'{time} to {time + randint(time + 1, time + 3)} hours'

    options = [
        'Heat until all of the liquid has boiled away and the black fumes have'
        ' blotted out the great and minor lights of the sky.',

        'Bring to a rolling boil and have the subject inhale the vapours for '
        f'{time}, or until the illness passes.'
         if type == 'cure' and liquid else None,

        'Bring to a rolling boil and steep a length of bandage for {time}. ' +
        ('Still hot, ' if flip() else 'Let cool, then ') +
        f'apply the bandages to {afflicted}, wrapping ' +
        ('tightly.' if flip() else 'loosely.')
        if type == 'cure' and liquid else None,

        f"Make a poultice using {authors[1]}'s standard method. Apply to "
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
            'mouthing the standard invocations.' if flip() else
            'forming the standard signs with the left hand.'
        ) if type not in ('general', 'summoning'),

        f'Ensure that the subject ingests the compound within {time}, to '
        'ensure maximum effectiveness.'
        if type not in ('general', 'summoning'),

        'Apply directly to the forehead.'
        if type not in ('general', 'summoning'),

        # TODO Make a momment if curse
        # TODO add a strand of hair if curse
        # TODO: If a summoning, how long until "X" starts to appear?
        # TODO: Add more summoning options
        # TODO: Add more general options
    ]

    directions += '\n\n' + choice([o for o in options if o])

    spell = '\n\n'.join((
        f'## {title}',
        f'### Ingredients\n\n{ingredients}',
        f'### Directions\n\n{directions}',
    ))

    return spell


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

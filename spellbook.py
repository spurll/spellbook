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

    if flip():
        title = f'{choice(spells["attributes"])} {title}'

    if type == 'cure':
        title += ' for '
    else:
        title += ' of '

    if type == 'summoning':
        title += plural(choice(summons))
    elif type in ('blight', 'cure'):
        title += f'{choice(spells["maladies"])} {choice(parts)}'
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
        item = 

        prep = (
            choice(components['preparations'][type])
            if type in ('solid', 'liquid') else ''
        )

        count, plural = (
            choice(zip(counts, plurals))
            if type != 'intangible' else (None, False)
        )

        items.append()

        # TODO: Include occasional attributes
        # TODO: If discrete, pluralize component if necessary
        # TODO: If not discrete, pluralize the measurement if necessary
        # TODO: If an animal with no parts, add live or dead

    # If contains liquid, "pour in... stirring constantly/occasionally"

    # Generate directions
    # TODO: Add directions (e.g., on a misty morning, facing west, facing a rising Mercury, under the sign of Sagitarius)

    # TODO: Add cautions


    # TODO: If a cure, direct how to apply to affected area (e.g., "make a poultice using authors[1]'s standard method and apply to {area} immediately")
    # TODO: If a curse, direct how to use (e.g., make a mommet, feed directly, etc.)
    # TODO: If a summoning, how long until "X" starts to appear?

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

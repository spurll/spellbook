#!/usr/bin/python3

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-ShareAlike 4.0 International License.

import argparse
import yaml
import re
from os import path
from random import choice

from words import name, titlecase, wordcount, indefinite, plural
from maybe import flip, choice_without


CONFIG = 'config.yml'
BOOKS = 'books.yml'
SPELLS = 'spells.yml'
FIGURES = 'figures.yml'
LOCALES = 'locales.yml'
ACTIONS = 'actions.yml'
COMPONENTS = 'components.yml'

# No need to include "y" as it only rarely functions as an initial vowel
VOWELS = 'AEIOUaeiou'
TARGET = 50000

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



# TODO: Add cautions

# TODO: Occasionally add people's names to spells

# TODO: Add title of the book, titles between sections, page numbers




def generate(outfile):
    author = name()
    title = generate_title(author)
    prologue, epilogue = generate_frame()
    pages = [generate_cover(title, author)]

    print(prologue)
    print(pages)
    print(epilogue)
    return;

    while wordcount(prologue, epilogue, *pages) < TARGET:
        pages.append(generate_page())

    book = f'# {title}\n\n' + '\n\n---\n\n'.join((prologue, *pages, epilogue))

    print('Spellbook complete.')
    print(f'Length: {pages.length} spells, {wordcount(book)} words\n')

    print(f'Writing output to {outfile}...')

    with open(outfile, 'w', encoding='utf8') as f:
        f.write('\n\n'.join((prologue)))

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


def generate_cover(title, author):
    return f'## {title}\n\n### by {author}'

# WITH ILLUSTRATIONS BY XXX



def generate_page():
    pass


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

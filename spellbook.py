#!/usr/bin/python3

# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-ShareAlike 4.0 International License.

import argparse
import yaml
import re
from os import path
from random import choice

CONFIG = 'config.yml'
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
figures = load_yaml(path.join(basedir, FIGURES))
locales = load_yaml(path.join(basedir, LOCALES))
spells = load_yaml(path.join(basedir, SPELLS))
actions = load_yaml(path.join(basedir, ACTIONS))
components = load_yaml(path.join(basedir, COMPONENTS))



# TODO: Add cautions




def generate(outfile):
    prologue, epilogue = generate_frame()



    print(prologue)
    print('')
    print(epilogue)
    return;

    pages = [generate_cover()]

    while wordcount(prologue, epilogue, *pages) < TARGET:
        pages.append(generate_page())

    # TODO: Add title of the book, titles between sections, page numbers
    book = '\n\n'.join((prologue, epilogue, *pages))

    print('Spellbook complete.')
    print(f'Length: {pages.length} spells, {wordcount(book)} words\n')

    print(f'Writing output to {outfile}...')

    with open(outfile, 'w', encoding='utf8') as f:
        f.write('\n\n'.join((prologue)))

    print('Done.')


def generate_frame():
    person = choice(list(figures['genders'].values()))
    pronouns = person['pronouns']
    attribute = choice(figures['attributes'])

    description = f'{indefinite(attribute)} {person["noun"]}'

    locale = f'{choice(locales["attributes"])} {(choice(locales["locales"]))}'

    prologue = f'{description.capitalize()} stole into {indefinite(locale)}, '

    if choice((True, False)):
        prologue += f'{choice(figures["dress"])}. '
    else:
        companion = ' '.join((
            choice(figures['companions']['attributes']),
            choice(figures['companions']['types'])
        ))
        prologue += f'accompanied by {indefinite(companion)}. '

    prologue += (
        f'{pronouns[0].capitalize()} stopped as {pronouns[2]} eyes lit upon '
        f'the object of {pronouns[2]} quest. '
    )

    if choice((True, False)):
        prologue += (
            f'The {person["noun"]} suddenly surged forward and grasped the '
            'tome eagerly. '
        )
    else:
        prologue += (
            f'The {person["noun"]} began to move again, approaching the '
            'tome warily. '
        )

    prologue += (
        f'{pronouns[0].capitalize()} lifted it from its resting place, then '
        'opened its cover and began to read.'
    )

    epilogue = ''

    return prologue, epilogue


def generate_cover():
    pass


def generate_page():
    pass


def wordcount(*args):
    """Double-counts hyphenated words, but oh well."""
    return sum((len(re.findall(r'\b\w', str)) for str in args))


def indefinite(noun):
    """Returns the given noun prefaced with 'a' or 'an', as appropriate."""
    return f'an {noun}' if noun[0] in VOWELS else f'a {noun}'


def plural(noun):
    """Returns the plural of a given noun (a hopeless task in English)."""
    if noun == 'ox':
        return f'{noun}en'

    if noun.endswith('foot'):
        return f'{noun[:-4]}feet'
    if noun.endswith('child'):
        return f'{noun}ren'
    if noun.endswith('man'):
        return f'{noun[:-3]}men'
    if noun.endsiwth(('moose', 'caribou', 'sheep', 'fish')):
        return noun

    if noun.endswith('ium'):
        return f'{noun[:-3]}ia'
    if noun.endswith(('pus', 'pod')):
        return f'{noun[:-3]}podes'
    if noun.endswith('scis'):
        return f'{noun[:-4]}scides'
    if noun.endswith('us') and not noun.endswith('lotus'):
        return f'{noun[:-2]}i'
    if noun.endswith('i'):
        return noun

    if noun.endswith('y'):
        return f'{noun[:-1]}ies'
    if noun.endswith(('s', 'x', 'ch', 'sh')):
        return f'{noun}es'

    return f'{noun}s'


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

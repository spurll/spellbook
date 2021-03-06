import re
from random import choice, randint
from maybe import flip, maybe, choice_without


CONSONANTS = list('bcdfghjklmnprstvwy')
VOWELS = list('aeiou')

COMBINATIONS = ['sh', 'ch', 'th', 'gh', 'st']
INITIAL_COMBINATIONS = ['br', 'dr', 'pr', 'tr', 'bl', 'pl']
TERMINAL_COMBINATIONS = ['nt', 'pt', 'll', 'ss', 'ck', 'sk']

INITIAL = CONSONANTS + COMBINATIONS + INITIAL_COMBINATIONS
TERMINAL = CONSONANTS + COMBINATIONS + TERMINAL_COMBINATIONS

LOWER_TITLE = [
    'a', 'an', 'the', 'and', 'as', 'at', 'atop', 'but', 'by', 'for', 'from',
    'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'per', 'to', 'up',
    'via', 'with'
]


def word(syllables=None):
    syllables = syllables or randint(1, 3)
    return ''.join(
        syllable(s == 0, s == syllables - 1) for s in range(syllables)
    )


def syllable(first=True, last=True):
    """
    Usually start with a consonant (or consonant combination), add vowel,
    optionally add another vowel, and optionally end with a consonant.
    """
    initial = (
        choice(INITIAL if first else INITIAL + TERMINAL)
        if not first or maybe(0.75) else ''
    )
    vowel = choice(VOWELS)
    extension = (
        choice_without(VOWELS, vowel if vowel not in 'eo' else None)
        if maybe(0.25) else ''
    )
    terminal = choice(TERMINAL) if last and maybe(0.75) else ''

    return initial + vowel + extension + terminal


def name():
    first = word().capitalize()

    if flip():
        return first

    return f'{first} {"of " if maybe(0.25) else ""}{word().capitalize()}'


def capitalize(str):
    """
    Capitalizes the first letter without changing the case of any other
    letters.
    """
    return str[0].upper() + str[1:] if str else str


def uncapitalize(str):
    """
    Lowercases the first letter without changing the case of any other
    letters.
    """
    return str[0].lower() + str[1:] if str else str


def oxford(strings):
    """Joins strings using the serial comma standard."""
    if len(strings) < 2:
        return ''.join(strings)
    if len(strings) == 2:
        return ' and '.join(strings)
    return ', '.join(strings[:-1]) + f', and {strings[-1]}'


def titlecase(str):
    """
    Capitalizes each word, except those in a proscribed list (e.g., articles,
    short prepositions, etc.). Note: all whitespace is replaced by single space
    characters.
    """
    return ' '.join(
        w.capitalize() if i == 0 or w not in LOWER_TITLE else w
        for i, w in enumerate(str.split())
    )


def wordcount(*args):
    # Ensure that hyphenated words aren't counted as two by replacing hyphens
    args = [str.replace('-', '_') for str in args]
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
    if noun.endswith(('moose', 'caribou', 'sheep', 'fish')):
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

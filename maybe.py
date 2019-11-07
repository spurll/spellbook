from random import getrandbits, random, choice


def flip():
    return bool(getrandbits(1))


def maybe(chance):
    return random() < chance


def choice_without(iterable, avoid):
    return choice([i for i in iterable if i != avoid])

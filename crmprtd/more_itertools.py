"""
Some additional iteration tools
"""
from itertools import islice, cycle


def take(n, iterable):
    """Yield the first n values of an iterable"""
    return islice(iterable, n)


def cycles(cycle_length, n):
    """Yield the first n values of a cycling (repeating) range of length cycle_length"""
    return take(n, cycle(range(cycle_length)))

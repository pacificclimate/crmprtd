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


def tap(f, iterable):
    """Return a generator that calls function f on each item, then yields the item."""
    for item in iterable:
        f(item)
        yield item


def log_progress(when=(10,), message="progress: {count}", log=None):
    """
    Return a function that logs a message periodically. This function is typically used
    to log progress updates during a long iteration, when such updates would be too
    bulky or intrusive if logged on every iteration.

    The function returned accepts an optional keyword argument, `item`, that can be
    used to pass in other information, e.g., the current iteration item. This is its
    typical usage, but it could be used differently.

    The function maintains a count of calls to it.

    A message is logged according to the argument `when`, which is either a single
    integer or an iterable of integers. (A single integer is converted to a length-1
    tuple.) A message is logged when the call count is equal to any of the integers in
    `when` or when it is a multiple of the last integer in `when`. This enables
    messages to be logged more frequently in the early parts of an iteration and less
    frequently in the later parts.

    The message is defined by argument `message`, which is a template string that is
    formatted with arguments `count` (function call count) and `item` (function
    argument) when a message is logged.

    The logger is given by the argument `log`, which is typically a Python logger
    function.

    Interesting that the explanation is 3x as long as the code.
    """
    count = 0
    when = tuple(when)
    front, last = when[0 : len(when) - 1], when[len(when) - 1]
    log(f"log_progress: when={when}, front={front}, last={last}")

    def f(item=None):
        if log is None:
            return
        nonlocal count
        count += 1
        if count in front or count % last == 0:
            log(message.format(count=count, item=item))

    return f

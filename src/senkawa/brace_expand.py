import contextlib
import itertools
import re
import string
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import cast

from pyparsing import ParseException

from . import expressions
from .errors import UnbalancedBracesError

alphabet = string.ascii_uppercase + string.ascii_lowercase
escape_re = re.compile(r"\\(.)")


@dataclass
class State:
    start = 0
    pos = 0
    depth = 0
    items: list[Iterable[str]] = field(default_factory=list)


def make_int_range(left: str, right: str, *, step: str | None = None):
    if any(s.startswith(("0", "-0")) for s in (left, right) if s not in ("0", "-0")):
        padding = max(len(left), len(right))
    else:
        padding = 0

    int_step = (int(step) or 1) if step else 1
    start = int(left)
    end = int(right)
    r = (
        range(start, end + 1, int_step)
        if start < end
        else range(start, end - 1, -int_step)
    )
    fmt = f"%0{padding}d"
    return (fmt % i for i in r)


def make_char_range(left: str, right: str, step: str | None = None):
    int_step = (int(step) or 1) if step else 1
    start = alphabet.index(left)
    end = alphabet.index(right)
    if start < end:
        return alphabet[start : end + 1 : int_step]

    end = end or -len(alphabet)
    return alphabet[start : end - 1 : -int_step]


def parse_expression(expr: str, *, escape: bool):
    with contextlib.suppress(ParseException):
        parsed = expressions.int_range.parse_string(expr)
        return make_int_range(
            str(parsed.left),
            str(parsed.right),
            step=cast(str | None, parsed.get("step")),
        )

    with contextlib.suppress(ParseException):
        parsed = expressions.char_range.parse_string(expr)
        return make_char_range(
            str(parsed.left),
            str(parsed.right),
            step=cast(str | None, parsed.get("step")),
        )

    return parse_sequence(expr, escape=escape)


def parse_sequence(seq: str, *, escape: bool = True):
    state = State()
    while state.pos < len(seq):
        char = seq[state.pos]

        if escape and char == "\\":
            state.pos += 2
            continue

        match (char, state.depth):
            case ("{", _):
                state.depth += 1
            case ("}", _):
                state.depth -= 1
            case (",", 0):
                state.items.append(
                    parse_pattern(seq[state.start : state.pos], escape=escape)
                )
                state.start = state.pos + 1  # skip the comma

        state.pos += 1

    if state.depth != 0:
        raise UnbalancedBracesError(f"Unbalanced braces: {seq}")

    if not state.items:
        return None

    # part after the last comma (may be the empty string)
    state.items.append(parse_pattern(seq[state.start :], escape=escape))
    return itertools.chain.from_iterable(state.items)


def parse_pattern(pattern: str, *, escape: bool) -> Iterator[str]:
    state = State()
    while state.pos < len(pattern):
        char = pattern[state.pos]

        if escape and char == "\\":
            state.pos += 2
            continue

        match char:
            case "{":
                if state.depth == 0 and state.pos > state.start:
                    # print 'literal:', pattern[start:pos]
                    state.items.append([pattern[state.start : state.pos]])
                    state.start = state.pos

                state.depth += 1
            case "}":
                state.depth -= 1
                if state.depth == 0:
                    expr = pattern[state.start + 1 : state.pos]
                    item = parse_expression(expr, escape=escape)
                    if item is None:  # not a range or sequence
                        state.items.extend(
                            [["{"], parse_pattern(expr, escape=escape), ["}"]]
                        )
                    else:
                        state.items.append(item)

                    state.start = state.pos + 1  # skip the closing brace

        state.pos += 1

    if state.depth != 0:  # unbalanced braces
        raise UnbalancedBracesError(f"Unbalanced braces: {pattern}")

    if state.start < state.pos:
        state.items.append([pattern[state.start :]])

    return ("".join(item) for item in itertools.product(*state.items))


def brace_expand(pattern: str, *, escape: bool = True) -> Iterator[str]:
    """Brace the pattern and return an iterator of expanded strings.

    Args:
        pattern (str): A brace expansion pattern.
        escape (bool, optional): Whether to allow escaping special characters for brace expansion by a backslash or not. Defaults to True.

    Yields:
        Iterator[str]: An iterator over strings resulting from brace expansion.

    Examples:
    >>> from senkawa import brace_expand

    # Integer range
    >>> list(brace_expand('item{1..3}'))
    ['item1', 'item2', 'item3']

    # Character range
    >>> list(brace_expand('{a..c}'))
    ['a', 'b', 'c']

    # Sequence
    >>> list(brace_expand('index.html{,.backup}'))
    ['index.html', 'index.html.backup']

    # Nested patterns
    >>> list(brace_expand('python{2.{5..7},3.{2,3}}'))
    ['python2.5', 'python2.6', 'python2.7', 'python3.2', 'python3.3']

    # Prefixing an integer with zero causes all numbers to be padded to
    # the same width.
    >>> list(brace_expand('{07..10}'))
    ['07', '08', '09', '10']

    # An optional increment can be specified for ranges.
    >>> list(brace_expand('{a..g..2}'))
    ['a', 'c', 'e', 'g']

    # Ranges can go in both directions.
    >>> list(brace_expand('{4..1}'))
    ['4', '3', '2', '1']

    # Numbers can be negative
    >>> list(brace_expand('{2..-1}'))
    ['2', '1', '0', '-1']

    # Unbalanced braces raise an exception.
    >>> list(brace_expand('{1{2,3}'))
    Traceback (most recent call last):
        ...
    senkawa.errors.UnbalancedBracesError: Unbalanced braces: {1{2,3}

    # By default, the backslash is the escape character.
    >>> list(brace_expand(r'{1\\{2,3}'))
    ['1{2', '3']

    # Setting 'escape' to False disables backslash escaping.
    >>> list(brace_expand(r'\\{1,2}', escape=False))
    ['\\\\1', '\\\\2']
    """  # noqa: E501
    return (
        escape_re.sub(r"\1", s) if escape else s
        for s in parse_pattern(pattern, escape=escape)
    )

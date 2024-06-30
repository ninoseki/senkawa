# senkawa

Glob with Bash-style brace expansion.

!!! note

    This package is highly influenced by [trendels/braceexpand](https://github.com/trendels/braceexpand).

## Installation

```bash
pip install senkawa
```

## Usage

```py
>>> import senkawa
# With glob
>>> list(senkawa.glob("*.{md,toml}"))
["README.md", "pyproject.toml"]

>>> list(senkawa.glob("tests/fixtures/{1..3}.txt"))
["tests/fixtures/1.txt", "tests/fixtures/2.txt", "tests/fixtures/3.txt"]

# brace-expand only
# Integer range
>>> list(senkawa.brace_expand('item{1..3}'))
['item1', 'item2', 'item3']

# Character range
>>> list(senkawa.brace_expand('{a..c}'))
['a', 'b', 'c']

# Sequence
>>> list(senkawa.brace_expand('index.html{,.backup}'))
['index.html', 'index.html.backup']

# Nested patterns
>>> list(senkawa.brace_expand('python{2.{5..7},3.{2,3}}'))
['python2.5', 'python2.6', 'python2.7', 'python3.2', 'python3.3']

# Prefixing an integer with zero causes all numbers to be padded to
# the same width.
>>> list(senkawa.brace_expand('{07..10}'))
['07', '08', '09', '10']

# An optional increment can be specified for ranges.
>>> list(senkawa.brace_expand('{a..g..2}'))
['a', 'c', 'e', 'g']

# Ranges can go in both directions.
>>> list(senkawa.brace_expand('{4..1}'))
['4', '3', '2', '1']

# Numbers can be negative
>>> list(senkawa.brace_expand('{2..-1}'))
['2', '1', '0', '-1']

# Unbalanced braces raise an exception.
>>> list(senkawa.brace_expand('{1{2,3}'))
Traceback (most recent call last):
    ...
senkawa.UnbalancedBracesError: Unbalanced braces: '{1{2,3}'

# By default, the backslash is the escape character.
>>> list(senakwa.brace_expand(r'{1\{2,3}'))
['1{2', '3']

# Setting 'escape' to False disables backslash escaping.
>>> list(senkawa.brace_expand(r'\{1,2}', escape=False))
['\\1', '\\2']

```

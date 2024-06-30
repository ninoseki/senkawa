import pytest
from senkawa import UnbalancedBracesError, brace_expand, glob


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("{1,2}", ["1", "2"]),
        ("{1}", ["{1}"]),
        ("{1,2{}}", ["1", "2{}"]),
        ("}{", ["}{"]),
        ("a{b,c}d{e,f}", ["abde", "abdf", "acde", "acdf"]),
        ("a{b,c{d,e,}}", ["ab", "acd", "ace", "ac"]),
        ("a{b,{c,{d,e}}}", ["ab", "ac", "ad", "ae"]),
        ("{{a,b},{c,d}}", ["a", "b", "c", "d"]),
        ("{7..10}", ["7", "8", "9", "10"]),
        ("{10..7}", ["10", "9", "8", "7"]),
        ("{1..5..2}", ["1", "3", "5"]),
        ("{5..1..2}", ["5", "3", "1"]),
        ("{1..3..0}", ["1", "2", "3"]),
        ("{1..3..-0}", ["1", "2", "3"]),
        ("{a..b..0}", ["a", "b"]),
        ("{a..b..-0}", ["a", "b"]),
        ("{07..10}", ["07", "08", "09", "10"]),
        ("{7..010}", ["007", "008", "009", "010"]),
        ("{1..-2}", ["1", "0", "-1", "-2"]),
        ("{01..-2}", ["01", "00", "-1", "-2"]),
        ("{1..-02}", ["001", "000", "-01", "-02"]),
        ("{-01..3..2}", ["-01", "001", "003"]),
        ("{a..e}", ["a", "b", "c", "d", "e"]),
        ("{a..e..2}", ["a", "c", "e"]),
        ("{e..a}", ["e", "d", "c", "b", "a"]),
        ("{e..a..2}", ["e", "c", "a"]),
        ("{1..a}", ["{1..a}"]),
        ("{a..1}", ["{a..1}"]),
        ("{1..1}", ["1"]),
        ("{a..a}", ["a"]),
        ("{,}", ["", ""]),
        ("{Z..a}", ["Z", "a"]),
        ("{a..Z}", ["a", "Z"]),
        ("{A..z}", list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")),
        ("{z..A}", list("zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA")),
        ("{a.{b,c}}", ["{a.b}", "{a.c}"]),
        ("{a.{1..2}}", ["{a.1}", "{a.2}"]),
        ("{{{,}}}", ["{{}}", "{{}}"]),
    ],
)
def test_brace_expand(pattern: str, expected: list[str]):
    assert list(brace_expand(pattern)) == expected


@pytest.mark.parametrize(
    "pattern",
    [
        "{{1,2}",
        "{1,2}}",
        "{1},2}",
        "{1,{2}",
        "{}1,2}",
        "{1,2{}",
        "}{1,2}",
        "{1,2}{",
    ],
)
def test_brace_expand_with_unlabeled_braces(pattern: str):
    with pytest.raises(UnbalancedBracesError):
        brace_expand(pattern)


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("\\{1,2\\}", ["{1,2}"]),
        ("{1\\,2}", ["{1,2}"]),
        ("\\}{1,2}", ["}1", "}2"]),
        ("\\{{1,2}", ["{1", "{2"]),
        ("{1,2}\\}", ["1}", "2}"]),
        ("{1,2}\\{", ["1{", "2{"]),
        ("{\\,1,2}", [",1", "2"]),
        ("{1\\,,2}", ["1,", "2"]),
        ("{1,\\,2}", ["1", ",2"]),
        ("{1,2\\,}", ["1", "2,"]),
        ("\\\\{1,2}", ["\\1", "\\2"]),
        ("\\{1..2\\}", ["{1..2}"]),
    ],
)
def test_brace_expand_with_escape(pattern: str, expected: list[str]):
    assert list(brace_expand(pattern, escape=True)) == expected


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("\\{1,2}", ["\\1", "\\2"]),
        ("{1,2\\}", ["1", "2\\"]),
        ("{1\\,2}", ["1\\", "2"]),
        ("{\\,1,2}", ["\\", "1", "2"]),
        ("{1\\,,2}", ["1\\", "", "2"]),
        ("{1,\\,2}", ["1", "\\", "2"]),
        ("{1,2\\,}", ["1", "2\\", ""]),
        ("\\{1..2\\}", ["\\{1..2\\}"]),
    ],
)
def test_brace_expand_without_escape(pattern: str, expected: list[str]):
    assert list(brace_expand(pattern, escape=False)) == expected


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        (
            "{00..10}",
            ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"],
        ),
        (
            "{10..00}",
            ["10", "09", "08", "07", "06", "05", "04", "03", "02", "01", "00"],
        ),
        (
            "{0..010}",
            [
                "000",
                "001",
                "002",
                "003",
                "004",
                "005",
                "006",
                "007",
                "008",
                "009",
                "010",
            ],
        ),
        (
            "{0..10}",
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        ),
        (
            "{10..0}",
            ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"],
        ),
        (
            "{-0..1}",
            ["0", "1"],
        ),
        (
            "{1..-0}",
            ["1", "0"],
        ),
        (
            "{0..-0}",
            ["0"],
        ),
    ],
)
def test_brace_expand_with_padding(pattern: str, expected: list[str]):
    assert list(brace_expand(pattern)) == expected


def test_glob_with_sequence():
    assert set(glob("*.{md,toml}")) == {"pyproject.toml", "README.md"}


def test_glob_with_range():
    assert set(glob("tests/fixtures/{1..3}.txt")) == {
        "tests/fixtures/1.txt",
        "tests/fixtures/2.txt",
        "tests/fixtures/3.txt",
    }

import pytest

from straight_line_programs import (
    BinaryRule,
    ISLP,
    IterationComponent,
    IterationRule,
    RLSLP,
    RunLengthRule,
    SLP,
    TerminalRule,
)


def test_slp_char_at_and_substring():
    rules = {
        "A1": TerminalRule("a"),
        "A2": TerminalRule("b"),
        "A3": BinaryRule("A1", "A2"),
        "S": BinaryRule("A3", "A3"),
    }
    slp = SLP(rules, start="S")
    assert slp.char_at(0) == "a"
    assert slp.char_at(3) == "b"
    assert slp.substring(1, 3) == "ba"
    assert slp.substring(1, 2, include_end=True) == "ba"
    with pytest.raises(IndexError):
        slp.char_at(-1)
    with pytest.raises(IndexError):
        slp.substring(2, 1)
    with pytest.raises(IndexError):
        slp.substring(1, 5)


def test_rlslp_char_at_and_substring():
    rules = {
        "A": TerminalRule("ab"),
        "S": RunLengthRule("A", 5),
    }
    rlslp = RLSLP(rules, start="S")
    assert rlslp.char_at(6) == "a"
    assert rlslp.substring(2, 8) == "ababab"


def test_islp_char_at_and_substring():
    rules = {
        "A": TerminalRule("a"),
        "B": TerminalRule("b"),
        "S": IterationRule(
            k1=1,
            k2=4,
            components=(
                IterationComponent("A", 1),
                IterationComponent("B", 0),
            ),
        ),
    }
    islp = ISLP(rules, start="S")
    assert islp.char_at(1) == "b"
    assert islp.char_at(13) == "b"
    assert islp.substring(2, 9) == "aabaaab"

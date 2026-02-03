import pytest

from straight_line_programs import (
    BinaryRule,
    ExpansionTooLargeError,
    GrammarValidationError,
    ISLP,
    IterationComponent,
    IterationRule,
    RLSLP,
    RunLengthRule,
    SLP,
    TerminalRule,
)
from straight_line_programs.base import BaseGrammar


def test_validation_start_symbol_missing():
    with pytest.raises(GrammarValidationError):
        SLP({"A": TerminalRule("a")}, start="S")


def test_validation_undefined_nonterminal():
    with pytest.raises(GrammarValidationError):
        SLP({"S": BinaryRule("A", "B")}, start="S")


def test_validation_cycle_detection():
    rules = {
        "A": BinaryRule("B", "B"),
        "B": BinaryRule("A", "A"),
    }
    with pytest.raises(GrammarValidationError):
        SLP(rules, start="A")


def test_validation_invalid_rule_type():
    rules = {
        "A": TerminalRule("a"),
        "S": RunLengthRule("A", 2),
    }
    with pytest.raises(GrammarValidationError):
        SLP(rules, start="S")


def test_expression_max_length_guard():
    slp = SLP({"S": TerminalRule("abcd")}, start="S")
    with pytest.raises(ExpansionTooLargeError):
        slp.expression(max_length=3)


def test_nonterminals_and_empty_slice():
    slp = SLP({"A": TerminalRule("a"), "S": BinaryRule("A", "A")}, start="S")
    assert set(slp.nonterminals()) == {"A", "S"}
    assert slp.substring(1, 1) == ""


def test_include_end_bounds_error():
    slp = SLP({"S": TerminalRule("abc")}, start="S")
    with pytest.raises(IndexError):
        slp.substring(0, 3, include_end=True)


def test_repetition_helpers_bounds():
    def get_len(_symbol: str) -> int:
        return 2

    def get_char(_symbol: str, index: int) -> str:
        return "ab"[index]

    def get_substring(_symbol: str, start: int, end: int) -> str:
        return "ab"[start:end]

    assert BaseGrammar._substring_in_repetition("A", 3, 2, 2, get_substring, get_len) == ""
    with pytest.raises(IndexError):
        BaseGrammar._char_in_repetition("A", 3, 6, get_char, get_len)
    with pytest.raises(IndexError):
        BaseGrammar._substring_in_repetition("A", 3, 0, 7, get_substring, get_len)


def test_slp_expression_nested_multichar_terminal():
    slp = SLP({"S": TerminalRule("ab")}, start="S")
    assert slp.expression_nested() == "\"ab\""


def test_rlslp_binary_branches_and_invalid_rules():
    rules = {
        "A": TerminalRule("ab"),
        "B": TerminalRule("cd"),
        "C": BinaryRule("A", "B"),
        "S": BinaryRule("C", "A"),
    }
    rlslp = RLSLP(rules, start="S")
    assert rlslp.size() == 1 + 1 + 2 + 2
    assert rlslp.expression() == "abcdab"
    assert rlslp.char_at(0) == "a"
    assert rlslp.char_at(3) == "d"
    assert rlslp.substring(0, 2) == "ab"
    assert rlslp.substring(4, 6) == "ab"
    assert rlslp.substring(2, 5) == "cda"
    with pytest.raises(GrammarValidationError):
        RLSLP({"S": TerminalRule("")}, start="S")
    with pytest.raises(GrammarValidationError):
        RLSLP({"A": TerminalRule("a"), "S": RunLengthRule("A", 1)}, start="S")


def test_islp_binary_and_iteration_edges():
    rules = {
        "A": TerminalRule("a"),
        "B": TerminalRule("b"),
        "C": BinaryRule("A", "B"),
        "S": BinaryRule("C", "A"),
    }
    islp = ISLP(rules, start="S")
    assert islp.length() == 3
    assert islp.size() == 1 + 1 + 2 + 2
    assert islp.expression() == "aba"
    assert islp.char_at(0) == "a"
    assert islp.char_at(2) == "a"
    assert islp.substring(0, 1) == "a"
    assert islp.substring(1, 3) == "ba"


def test_islp_iteration_validation_and_slicing_branches():
    rules = {
        "A": TerminalRule("a"),
        "B": TerminalRule("b"),
        "S": IterationRule(
            k1=1,
            k2=3,
            components=(IterationComponent("A", 1), IterationComponent("B", 0)),
        ),
    }
    islp = ISLP(rules, start="S")
    assert islp.substring(0, 1) == "a"
    assert islp.substring(2, 3) == "a"
    assert islp.substring(0, 9) == "abaabaaab"
    with pytest.raises(GrammarValidationError):
        ISLP(
            {"A": TerminalRule("a"), "S": IterationRule(0, 1, (IterationComponent("A", 0),))},
            start="S",
        )
    with pytest.raises(GrammarValidationError):
        ISLP(
            {"A": TerminalRule("a"), "S": IterationRule(1, 1, (IterationComponent("A", -1),))},
            start="S",
        )
    with pytest.raises(IndexError):
        islp._rule_char_at(rules["S"], 9, islp._char_at_symbol, islp._lengths.__getitem__)

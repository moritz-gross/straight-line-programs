"""Straight-Line Programs (SLPs)."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple, Union

from .base import BaseGrammar
from .errors import GrammarValidationError
from .rules import BinaryRule, TerminalRule

SLPRule = Union[TerminalRule, BinaryRule]


class SLP(BaseGrammar):
    """Straight-Line Program (SLP).

    An SLP is a context-free grammar that generates exactly one string using
    only terminal and binary concatenation rules.

    Args:
        rules: Mapping from nonterminal names to terminal or binary rules.
        start: Start symbol for the grammar.
    """

    rule_types: Tuple[type, ...] = (TerminalRule, BinaryRule)

    def __init__(self, rules: Dict[str, SLPRule], start: str) -> None:
        super().__init__(rules, start)

    def _referenced_nonterminals(self, rule: SLPRule) -> Iterable[str]:
        """Return referenced nonterminals for an SLP rule."""
        if isinstance(rule, BinaryRule):
            return (rule.left, rule.right)
        return ()

    def _rule_size(self, rule: SLPRule) -> int:
        """Return the size contribution of an SLP rule."""
        if isinstance(rule, TerminalRule):
            return 1
        if isinstance(rule, BinaryRule):
            return 2
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_length(self, rule: SLPRule, get_len) -> int:
        """Compute |exp(A)| for an SLP rule."""
        if isinstance(rule, TerminalRule):
            if not rule.terminal:
                raise GrammarValidationError("Terminal string must be non-empty.")
            return len(rule.terminal)
        if isinstance(rule, BinaryRule):
            return get_len(rule.left) + get_len(rule.right)
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_expand(self, rule: SLPRule, expand_symbol) -> str:
        """Expand an SLP rule to its explicit string."""
        if isinstance(rule, TerminalRule):
            return rule.terminal
        if isinstance(rule, BinaryRule):
            return expand_symbol(rule.left) + expand_symbol(rule.right)
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_char_at(self, rule: SLPRule, index: int, get_char, get_len) -> str:
        """Return the character at index for an SLP rule."""
        if isinstance(rule, TerminalRule):
            return rule.terminal[index]
        if isinstance(rule, BinaryRule):
            left_len = get_len(rule.left)
            if index < left_len:
                return get_char(rule.left, index)
            return get_char(rule.right, index - left_len)
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_substring(self, rule: SLPRule, start: int, end: int, get_substring, get_len) -> str:
        """Return the substring for an SLP rule (end-exclusive)."""
        if isinstance(rule, TerminalRule):
            return rule.terminal[start:end]
        if isinstance(rule, BinaryRule):
            left_len = get_len(rule.left)
            if end <= left_len:
                return get_substring(rule.left, start, end)
            if start >= left_len:
                return get_substring(rule.right, start - left_len, end - left_len)
            left_part = get_substring(rule.left, start, left_len)
            right_part = get_substring(rule.right, 0, end - left_len)
            return left_part + right_part
        raise GrammarValidationError("Unsupported rule type.")

    def length(self, symbol: str | None = None) -> int:
        """Return the length of the expansion of a symbol (defaults to start).

        Length is computed recursively from the rules:
        - Terminal rule A -> a: |exp(A)| = |a|
        - Binary rule A -> B C: |exp(A)| = |exp(B)| + |exp(C)|

        Source: Navarro et al., "Generalized Straight-Line Programs"
        https://arxiv.org/abs/2404.07057
        """

        return super().length(symbol)

    def expression_nested(self, symbol: str | None = None) -> str:
        """Return a nested, parenthesized expression of how the string is built."""

        sym = symbol or self.start
        return self._nested_symbol(sym)

    def _nested_symbol(self, symbol: str) -> str:
        rule = self.rules[symbol]
        if isinstance(rule, TerminalRule):
            return self._format_terminal(rule.terminal)
        if isinstance(rule, BinaryRule):
            left = self._nested_symbol(rule.left)
            right = self._nested_symbol(rule.right)
            return f"({left} {right})"
        raise GrammarValidationError("Unsupported rule type.")

    @staticmethod
    def _format_terminal(terminal: str) -> str:
        if len(terminal) == 1:
            return terminal
        return f"\"{terminal}\""

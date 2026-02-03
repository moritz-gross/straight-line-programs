"""Run-Length Straight-Line Programs (RLSLPs)."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple, Union

from .base import BaseGrammar
from .errors import GrammarValidationError
from .rules import BinaryRule, RunLengthRule, TerminalRule

RLSLPRule = Union[TerminalRule, BinaryRule, RunLengthRule]


class RLSLP(BaseGrammar):
    """Run-Length Straight-Line Program (RLSLP).

    An RLSLP extends an SLP with run-length rules A -> B^t.

    Args:
        rules: Mapping from nonterminal names to terminal, binary, or run-length rules.
        start: Start symbol for the grammar.
    """

    rule_types: Tuple[type, ...] = (TerminalRule, BinaryRule, RunLengthRule)

    def __init__(self, rules: Dict[str, RLSLPRule], start: str) -> None:
        super().__init__(rules, start)

    def _referenced_nonterminals(self, rule: RLSLPRule) -> Iterable[str]:
        """Return referenced nonterminals for an RLSLP rule."""
        if isinstance(rule, BinaryRule):
            return rule.left, rule.right
        if isinstance(rule, RunLengthRule):
            return (rule.base,)
        return ()

    def _rule_size(self, rule: RLSLPRule) -> int:
        """Return the size contribution of an RLSLP rule."""
        if isinstance(rule, TerminalRule):
            return 1
        if isinstance(rule, BinaryRule):
            return 2
        if isinstance(rule, RunLengthRule):
            return 2
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_length(self, rule: RLSLPRule, get_len) -> int:
        """Compute |exp(A)| for an RLSLP rule."""
        if isinstance(rule, TerminalRule):
            if not rule.terminal:
                raise GrammarValidationError("Terminal string must be non-empty.")
            return len(rule.terminal)
        if isinstance(rule, BinaryRule):
            return get_len(rule.left) + get_len(rule.right)
        if isinstance(rule, RunLengthRule):
            if rule.count < 2:
                raise GrammarValidationError("Run-length count must be >= 2.")
            return get_len(rule.base) * rule.count
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_expand(self, rule: RLSLPRule, expand_symbol) -> str:
        """Expand an RLSLP rule to its explicit string."""
        if isinstance(rule, TerminalRule):
            return rule.terminal
        if isinstance(rule, BinaryRule):
            return expand_symbol(rule.left) + expand_symbol(rule.right)
        if isinstance(rule, RunLengthRule):
            return expand_symbol(rule.base) * rule.count
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_char_at(self, rule: RLSLPRule, index: int, get_char, get_len) -> str:
        """Return the character at index for an RLSLP rule."""
        if isinstance(rule, TerminalRule):
            return rule.terminal[index]
        if isinstance(rule, BinaryRule):
            left_len = get_len(rule.left)
            if index < left_len:
                return get_char(rule.left, index)
            return get_char(rule.right, index - left_len)
        if isinstance(rule, RunLengthRule):
            return self._char_in_repetition(rule.base, rule.count, index, get_char, get_len)
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_substring(
        self, rule: RLSLPRule, start: int, end: int, get_substring, get_len
    ) -> str:
        """Return the substring for an RLSLP rule (end-exclusive)."""
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
        if isinstance(rule, RunLengthRule):
            return self._substring_in_repetition(
                rule.base, rule.count, start, end, get_substring, get_len
            )
        raise GrammarValidationError("Unsupported rule type.")

    def length(self, symbol: str | None = None) -> int:
        """Return the length of the expansion of a symbol (defaults to start).

        Length is computed recursively from the rules:
        - Terminal rule A -> a: |exp(A)| = |a|
        - Binary rule A -> B C: |exp(A)| = |exp(B)| + |exp(C)|
        - Run-length rule A -> B^t: |exp(A)| = t * |exp(B)|

        Source: Navarro et al., "Balancing Run-Length Straight-Line Programs"
        https://arxiv.org/abs/2206.13027
        """

        return super().length(symbol)

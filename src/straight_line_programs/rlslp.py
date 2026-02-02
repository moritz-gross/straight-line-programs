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

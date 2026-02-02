"""Iterated Straight-Line Programs (ISLPs)."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple, Union

from .base import BaseGrammar
from .errors import GrammarValidationError
from .rules import BinaryRule, IterationRule, TerminalRule

ISLPRule = Union[TerminalRule, BinaryRule, IterationRule]


class ISLP(BaseGrammar):
    """Iterated Straight-Line Program (ISLP).

    An ISLP extends an SLP with iteration rules based on polynomial exponents.

    Args:
        rules: Mapping from nonterminal names to terminal, binary, or iteration rules.
        start: Start symbol for the grammar.
    """

    rule_types: Tuple[type, ...] = (TerminalRule, BinaryRule, IterationRule)

    def __init__(self, rules: Dict[str, ISLPRule], start: str) -> None:
        super().__init__(rules, start)

    def _referenced_nonterminals(self, rule: ISLPRule) -> Iterable[str]:
        """Return referenced nonterminals for an ISLP rule."""
        if isinstance(rule, BinaryRule):
            return (rule.left, rule.right)
        if isinstance(rule, IterationRule):
            return tuple(component.symbol for component in rule.components)
        return ()

    def _rule_size(self, rule: ISLPRule) -> int:
        """Return the size contribution of an ISLP rule."""
        if isinstance(rule, TerminalRule):
            return 1
        if isinstance(rule, BinaryRule):
            return 2
        if isinstance(rule, IterationRule):
            t = len(rule.components)
            return 2 * t + 2
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_length(self, rule: ISLPRule, get_len) -> int:
        """Compute |exp(A)| for an ISLP rule."""
        if isinstance(rule, TerminalRule):
            if not rule.terminal:
                raise GrammarValidationError("Terminal string must be non-empty.")
            return len(rule.terminal)
        if isinstance(rule, BinaryRule):
            return get_len(rule.left) + get_len(rule.right)
        if isinstance(rule, IterationRule):
            if rule.k1 < 1 or rule.k2 < 1 or rule.k1 > rule.k2:
                raise GrammarValidationError("Iteration bounds must satisfy 1 <= k1 <= k2.")
            for component in rule.components:
                if component.exponent < 0:
                    raise GrammarValidationError("Iteration exponents must be >= 0.")
            total = 0
            lengths = [get_len(component.symbol) for component in rule.components]
            exponents = [component.exponent for component in rule.components]
            for i in range(rule.k1, rule.k2 + 1):
                for length, exponent in zip(lengths, exponents):
                    total += length * (i ** exponent)
            return total
        raise GrammarValidationError("Unsupported rule type.")

    def _rule_expand(self, rule: ISLPRule, expand_symbol) -> str:
        """Expand an ISLP rule to its explicit string."""
        if isinstance(rule, TerminalRule):
            return rule.terminal
        if isinstance(rule, BinaryRule):
            return expand_symbol(rule.left) + expand_symbol(rule.right)
        if isinstance(rule, IterationRule):
            if rule.k1 < 1 or rule.k2 < 1 or rule.k1 > rule.k2:
                raise GrammarValidationError("Iteration bounds must satisfy 1 <= k1 <= k2.")
            for component in rule.components:
                if component.exponent < 0:
                    raise GrammarValidationError("Iteration exponents must be >= 0.")
            parts = []
            expanded = [expand_symbol(component.symbol) for component in rule.components]
            exponents = [component.exponent for component in rule.components]
            for i in range(rule.k1, rule.k2 + 1):
                for segment, exponent in zip(expanded, exponents):
                    parts.append(segment * (i ** exponent))
            return "".join(parts)
        raise GrammarValidationError("Unsupported rule type.")

    def length(self, symbol: str | None = None) -> int:
        """Return the length of the expansion of a symbol (defaults to start).

        Length is computed recursively from the rules:
        - Terminal rule A -> a: |exp(A)| = |a|
        - Binary rule A -> B C: |exp(A)| = |exp(B)| + |exp(C)|
        - Iteration rule A -> prod_{i=k1}^{k2} B_1^{i^{c_1}} ... B_t^{i^{c_t}}:
          |exp(A)| = sum_{i=k1}^{k2} sum_{r=1}^t |exp(B_r)| * i^{c_r}

        Source: Navarro and Urbina, "Iterated Straight-Line Programs"
        https://arxiv.org/abs/2402.09232
        """

        return super().length(symbol)

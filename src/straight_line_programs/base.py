"""Common grammar logic for SLP variants."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Set, Tuple

from .errors import ExpansionTooLargeError, GrammarValidationError


class BaseGrammar:
    """Base class for straight-line program variants.

    Concrete subclasses define:
    - Which rule types are allowed.
    - How rule size and rule length are computed.
    - How rules expand into explicit strings.
    """

    rule_types: Tuple[type, ...] = ()

    def __init__(self, rules: Dict[str, object], start: str) -> None:
        """Create a grammar with a rule map and a start symbol.

        Args:
            rules: Mapping from nonterminal names to rule objects.
            start: Start symbol for the grammar.
        """
        self.rules = dict(rules)
        self.start = start
        self._lengths: Dict[str, int] = {}
        self.validate()

    def validate(self) -> None:
        """Validate the grammar structure and precompute lengths.

        Checks:
        - Start symbol is defined.
        - Rule types are valid for the subclass.
        - All referenced nonterminals exist.
        - Grammar is acyclic.
        """
        if self.start not in self.rules:
            raise GrammarValidationError("Start symbol must be defined in rules.")
        for symbol, rule in self.rules.items():
            if not isinstance(rule, self.rule_types):
                raise GrammarValidationError(
                    f"Invalid rule type for {symbol}: {type(rule).__name__}"
                )
            for ref in self._referenced_nonterminals(rule):
                if ref not in self.rules:
                    raise GrammarValidationError(
                        f"Undefined nonterminal '{ref}' referenced by {symbol}."
                    )
        for symbol in self.rules:
            self._compute_length(symbol, set())

    def _compute_length(self, symbol: str, visiting: Set[str]) -> int:
        """Compute |exp(symbol)| with cycle detection and memoization."""
        if symbol in self._lengths:
            return self._lengths[symbol]
        if symbol in visiting:
            raise GrammarValidationError("Grammar contains a cycle.")
        visiting.add(symbol)
        rule = self.rules[symbol]
        length = self._rule_length(rule, lambda s: self._compute_length(s, visiting))
        self._lengths[symbol] = length
        visiting.remove(symbol)
        return length

    def length(self, symbol: Optional[str] = None) -> int:
        """Return the length of the expansion of a symbol (defaults to start)."""

        sym = symbol or self.start
        return self._compute_length(sym, set())

    def expression(self, symbol: Optional[str] = None, max_length: Optional[int] = 100000) -> str:
        """Expand a symbol to its explicit string.

        Args:
            symbol: Nonterminal to expand. Defaults to the start symbol.
            max_length: Optional guard to prevent huge expansions.
        """

        sym = symbol or self.start
        length = self.length(sym)
        if max_length is not None and length > max_length:
            raise ExpansionTooLargeError(
                f"Expansion length {length} exceeds max_length={max_length}."
            )
        return self._expand_symbol(sym)

    def char_at(self, index: int, symbol: Optional[str] = None) -> str:
        """Return the character at position index (0-based).

        Args:
            index: 0-based position in the expansion.
            symbol: Nonterminal to index. Defaults to the start symbol.
        """

        sym = symbol or self.start
        length = self.length(sym)
        if index < 0 or index >= length:
            raise IndexError(f"Index {index} out of range for length {length}.")
        return self._char_at_symbol(sym, index)

    def substring(
        self,
        start: int,
        end: int,
        symbol: Optional[str] = None,
        include_end: bool = False,
    ) -> str:
        """Return the substring from start to end.

        Default is end-exclusive: [start, end). Set include_end=True for [start, end].

        Args:
            start: 0-based starting index (inclusive).
            end: 0-based ending index (exclusive by default).
            symbol: Nonterminal to slice. Defaults to the start symbol.
            include_end: Treat end as inclusive if True.
        """

        sym = symbol or self.start
        length = self.length(sym)
        if include_end:
            if start < 0 or end < start or end >= length:
                raise IndexError(
                    f"Substring bounds must satisfy 0 <= start <= end < {length}."
                )
            end_exclusive = end + 1
        else:
            if start < 0 or end < start or end > length:
                raise IndexError(
                    f"Substring bounds must satisfy 0 <= start <= end <= {length}."
                )
            end_exclusive = end
        if start == end_exclusive:
            return ""
        return self._substring_symbol(sym, start, end_exclusive)

    def _expand_symbol(self, symbol: str) -> str:
        """Recursively expand a symbol using the subclass rule semantics."""
        rule = self.rules[symbol]
        return self._rule_expand(rule, self._expand_symbol)

    def _char_at_symbol(self, symbol: str, index: int) -> str:
        """Return the character at index within a symbol expansion."""
        rule = self.rules[symbol]
        return self._rule_char_at(rule, index, self._char_at_symbol, self._lengths.__getitem__)

    def _substring_symbol(self, symbol: str, start: int, end: int) -> str:
        """Return the substring within a symbol expansion (end-exclusive)."""
        rule = self.rules[symbol]
        return self._rule_substring(
            rule, start, end, self._substring_symbol, self._lengths.__getitem__
        )

    @staticmethod
    def _char_in_repetition(symbol: str, repeat_count: int, index: int, get_char, get_len) -> str:
        """Index into a repeated symbol block."""
        base_len = get_len(symbol)
        total_len = base_len * repeat_count
        if index < 0 or index >= total_len:
            raise IndexError(
                f"Index {index} out of range for repeated length {total_len}."
            )
        local_index = index % base_len
        return get_char(symbol, local_index)

    @staticmethod
    def _substring_in_repetition(
        symbol: str, repeat_count: int, start: int, end: int, get_substring, get_len
    ) -> str:
        """Slice within a repeated symbol block (end-exclusive)."""
        base_len = get_len(symbol)
        total_len = base_len * repeat_count
        if start < 0 or end < start or end > total_len:
            raise IndexError(
                f"Substring bounds must satisfy 0 <= start <= end <= {total_len}."
            )
        if start == end:
            return ""
        first_rep = start // base_len
        last_rep = (end - 1) // base_len
        parts = []
        for rep in range(first_rep, last_rep + 1):
            local_start = 0
            local_end = base_len
            if rep == first_rep:
                local_start = start - rep * base_len
            if rep == last_rep:
                local_end = end - rep * base_len
            parts.append(get_substring(symbol, local_start, local_end))
        return "".join(parts)

    def size(self) -> int:
        """Return the grammar size as defined in the paper for this variant."""

        return sum(self._rule_size(rule) for rule in self.rules.values())

    def nonterminals(self) -> Tuple[str, ...]:
        """Return all nonterminal names in this grammar."""
        return tuple(self.rules.keys())

    def _referenced_nonterminals(self, rule: object) -> Iterable[str]:
        """Return nonterminals referenced by the given rule."""
        raise NotImplementedError

    def _rule_size(self, rule: object) -> int:
        """Return the contribution of a rule to grammar size."""
        raise NotImplementedError

    def _rule_length(self, rule: object, get_len) -> int:
        """Return |exp(A)| for a rule A using get_len for nonterminals."""
        raise NotImplementedError

    def _rule_expand(self, rule: object, expand_symbol) -> str:
        """Expand a rule to a concrete string."""
        raise NotImplementedError

    def _rule_char_at(self, rule: object, index: int, get_char, get_len) -> str:
        """Return the character at index for a rule."""
        raise NotImplementedError

    def _rule_substring(self, rule: object, start: int, end: int, get_substring, get_len) -> str:
        """Return the substring for a rule."""
        raise NotImplementedError

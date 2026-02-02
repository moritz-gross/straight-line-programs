"""Custom exceptions for straight_line_programs."""


class GrammarValidationError(ValueError):
    """Raised when a grammar is ill-formed.

    Examples:
    - Cycles in rule dependencies.
    - Undefined nonterminals.
    - Invalid rule types for a grammar variant.
    """


class ExpansionTooLargeError(ValueError):
    """Raised when an expansion exceeds the requested max_length."""

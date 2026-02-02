"""Rule definitions for SLP variants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class TerminalRule:
    """Terminal rule A -> a.

    Args:
        terminal: The literal terminal string produced by the rule.
    """

    terminal: str


@dataclass(frozen=True)
class BinaryRule:
    """Binary concatenation rule A -> B C.

    Args:
        left: Left nonterminal B.
        right: Right nonterminal C.
    """

    left: str
    right: str


@dataclass(frozen=True)
class RunLengthRule:
    """Run-length rule A -> B^t.

    Args:
        base: The repeated nonterminal B.
        count: The repetition count t.

    Note: theory often assumes t >= 3. We allow t >= 2 for small examples.
    """

    base: str
    count: int


@dataclass(frozen=True)
class IterationComponent:
    """One block B_r^{i^{c_r}} inside an ISLP iteration rule.

    Args:
        symbol: The nonterminal B_r being repeated.
        exponent: The exponent c_r (so the repetition count is i^{c_r}).
    """

    symbol: str
    exponent: int


@dataclass(frozen=True)
class IterationRule:
    """Iteration rule A -> prod_{i=k1}^{k2} B_1^{i^{c_1}} ... B_t^{i^{c_t}}.

    Args:
        k1: Lower bound of the iteration index i.
        k2: Upper bound of the iteration index i (inclusive).
        components: Sequence of iteration components B_r^{i^{c_r}}.
    """

    k1: int
    k2: int
    components: Tuple[IterationComponent, ...]

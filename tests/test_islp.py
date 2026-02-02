from straight_line_programs import (
    ISLP,
    IterationComponent,
    IterationRule,
    TerminalRule,
)


def test_islp_string_family():
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
    assert islp.length() == 14
    assert islp.expression() == "abaabaaabaaaab"


def test_islp_rule_size():
    rule = IterationRule(
        k1=1,
        k2=3,
        components=(IterationComponent("A", 1), IterationComponent("B", 0)),
    )
    islp = ISLP({"A": TerminalRule("a"), "B": TerminalRule("b"), "S": rule}, start="S")
    assert islp.size() == 1 + 1 + 6

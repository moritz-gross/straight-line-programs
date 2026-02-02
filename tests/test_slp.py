from straight_line_programs import BinaryRule, SLP, TerminalRule


def test_slp_abab():
    rules = {
        "A1": TerminalRule("a"),
        "A2": TerminalRule("b"),
        "A3": BinaryRule("A1", "A2"),
        "S": BinaryRule("A3", "A3"),
    }
    slp = SLP(rules, start="S")
    assert slp.expression() == "abab"
    assert slp.length() == 4
    assert slp.size() == 6
    assert slp.expression_nested() == "((a b) (a b))"

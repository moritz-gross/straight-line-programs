from straight_line_programs import BinaryRule, RLSLP, RunLengthRule, TerminalRule


def test_rlslp_run_length():
    rules = {
        "A": TerminalRule("ab"),
        "S": RunLengthRule("A", 5),
    }
    rlslp = RLSLP(rules, start="S")
    assert rlslp.length() == 10
    assert rlslp.expression() == "ababababab"
    assert rlslp.size() == 3


def test_rlslp_ab_power_100_length_only():
    rules = {
        "A1": TerminalRule("a"),
        "A2": TerminalRule("b"),
        "A3": BinaryRule("A1", "A2"),
        "S": RunLengthRule("A3", 100),
    }
    rlslp = RLSLP(rules, start="S")
    assert rlslp.length() == 200

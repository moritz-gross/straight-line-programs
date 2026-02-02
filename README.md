# straight-line-programs

  Small teaching-oriented Python library for Straight-Line Programs (SLPs) and variants (RLSLP, ISLP).
  Built to mirror the definitions and notation used in [Generalized Straight-Line Programs](https://arxiv.org/pdf/2404.07057) by Navarro et al.

  ## Install

  From GitHub:

  ```bash
  uv add git+https://github.com/moritz-gross/straight-line-programs.git
  # or
  pip install git+https://github.com/moritz-gross/straight-line-programs.git
  ```

  ## Quick usage
  ```
  from straight_line_programs import (
      SLP, RLSLP, ISLP,
      TerminalRule, BinaryRule, RunLengthRule,
      IterationRule, IterationComponent,
  )

  slp = SLP(
      rules={
          "A1": TerminalRule("a"),
          "A2": TerminalRule("b"),
          "A3": BinaryRule("A1", "A2"),
          "S": BinaryRule("A3", "A3"),
      },
      start="S",
  )

  slp.expression()         # "abab"
  slp.expression_nested()  # "((a b) (a b))"
  slp.length()             # 4
  ```

  ## Features

  - SLP / RLSLP / ISLP rule types
  - Length computation without full expansion
  - Safe full expansion (guarded by max length)
  - Nested expression display (expression_nested())

  ## Development
  ```bash
  uv run pytest
  ```
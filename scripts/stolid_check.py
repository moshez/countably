"""Run stolid as a standalone lint pass on the given paths."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from stolid.checker import Checker


def main(roots: list[str]) -> int:
    total = 0
    for root in roots:
        for path in Path(root).rglob("*.py"):
            source = path.read_text()
            tree = ast.parse(source)
            lines = source.splitlines()
            checker = Checker(tree=tree, lines=lines, filename=str(path))
            for line, col, msg, _ in checker.run():
                print(f"{path}:{line}:{col + 1}: {msg}")
                total += 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

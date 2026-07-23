#!/usr/bin/env python3
"""Reassemble and run the one-time documentation bootstrap."""
from pathlib import Path

parts_dir = Path(__file__).parent / "bootstrap_parts"
parts = sorted(parts_dir.glob("part_*.txt"))
if not parts:
    raise SystemExit("No bootstrap parts were found.")
source = "".join(path.read_text(encoding="utf-8") for path in parts)
namespace = {"__name__": "__main__", "__file__": str(Path(__file__))}
exec(compile(source, str(Path(__file__)), "exec"), namespace)

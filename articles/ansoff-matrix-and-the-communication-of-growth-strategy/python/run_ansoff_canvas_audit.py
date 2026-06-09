#!/usr/bin/env python3
"""Convenience runner for local Ansoff Matrix Catalyst Canvas audits."""

from __future__ import annotations

from pathlib import Path
import sys

ARTICLE_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ARTICLE_ROOT / "python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from ansoff_canvas.cli import main  # noqa: E402

raise SystemExit(main(["--article-root", str(ARTICLE_ROOT)]))

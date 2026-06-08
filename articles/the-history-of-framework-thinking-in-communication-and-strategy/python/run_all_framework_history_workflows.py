#!/usr/bin/env python3
"""Run all Python workflows for The History of Framework Thinking in Communication and Strategy."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

scripts = [
    ROOT / "python" / "catalyst_canvas_framework_history_engine.py",
]

for script in scripts:
    print(f"Running {script.name}")
    subprocess.run([sys.executable, str(script)], check=True)

print("All Python framework-history workflows complete.")

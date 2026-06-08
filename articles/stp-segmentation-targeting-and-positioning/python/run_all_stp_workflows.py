#!/usr/bin/env python3
"""Run all Python STP workflows in sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

scripts = [
    "stp_audience_positioning_audit.py",
    "segment_priority_model.py",
    "positioning_gap_checker.py",
    "ethical_targeting_review.py",
]

for script in scripts:
    print(f"Running {script}...")
    subprocess.run([sys.executable, str(HERE / script)], check=True)

print("All STP Python workflows completed.")

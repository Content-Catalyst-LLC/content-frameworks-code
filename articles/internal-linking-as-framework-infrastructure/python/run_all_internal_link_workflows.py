#!/usr/bin/env python3
"""Run all Python workflows for the internal-linking article."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for script in [ROOT / "python" / "catalyst_canvas_internal_link_audit.py"]:
    print(f"Running {script.name}")
    subprocess.run([sys.executable, str(script)], check=True)
print("All Python internal-link workflows complete.")

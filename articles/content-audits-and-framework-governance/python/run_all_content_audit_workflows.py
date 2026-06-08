#!/usr/bin/env python3
"""Run all Python workflows for Content Audits and Framework Governance."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

scripts = [
    ROOT / "python" / "catalyst_canvas_content_audit_engine.py",
]

for script in scripts:
    print(f"Running {script.name}")
    subprocess.run([sys.executable, str(script)], check=True)

print("All Python content-audit workflows complete.")

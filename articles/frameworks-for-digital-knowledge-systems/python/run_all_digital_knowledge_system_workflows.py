#!/usr/bin/env python3
"""Run all Python workflows for Frameworks for Digital Knowledge Systems."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

scripts = [
    ROOT / "python" / "catalyst_canvas_digital_knowledge_system_engine.py",
]

for script in scripts:
    print(f"Running {script.name}")
    subprocess.run([sys.executable, str(script)], check=True)

print("All Python digital-knowledge-system workflows complete.")

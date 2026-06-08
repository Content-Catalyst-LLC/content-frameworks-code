#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "python" / "content_frameworks_audit.py",
    ROOT / "python" / "internal_link_diagnostics.py"
]

for script in SCRIPTS:
    print(f"Running {script.name}")
    subprocess.run([sys.executable, str(script)], check=True)

print("All Python workflows complete.")

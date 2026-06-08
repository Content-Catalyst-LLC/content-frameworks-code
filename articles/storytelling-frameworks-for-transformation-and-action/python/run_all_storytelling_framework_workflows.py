#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "python" / "storytelling_framework_audit_engine.py")], check=True)
print("All Python storytelling-framework workflows complete.")

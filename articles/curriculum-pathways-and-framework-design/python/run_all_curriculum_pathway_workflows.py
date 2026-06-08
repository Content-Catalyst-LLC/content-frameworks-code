#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "python" / "curriculum_pathway_audit_engine.py")], check=True)
print("All Python curriculum-pathway workflows complete.")

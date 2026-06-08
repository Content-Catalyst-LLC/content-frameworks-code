#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "python" / "evidence_architecture_audit_engine.py")], check=True)
print("All Python evidence-architecture workflows complete.")

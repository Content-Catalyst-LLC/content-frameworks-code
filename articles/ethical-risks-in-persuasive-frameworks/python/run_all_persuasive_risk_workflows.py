#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "python" / "persuasive_framework_risk_audit_engine.py")], check=True)
print("All Python persuasive-risk workflows complete.")

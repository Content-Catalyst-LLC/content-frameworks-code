#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "python" / "communication_model_audit_engine.py")], check=True)
print("All Python communication-model workflows complete.")

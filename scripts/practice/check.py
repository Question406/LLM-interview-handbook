from pathlib import Path
import subprocess
import sys
from setup import python_path

if not python_path().exists():
    raise SystemExit("Run npm run practice:setup first.")
raise SystemExit(subprocess.call([str(python_path()), str(Path(__file__).resolve().parents[2] / "tests/practice_runner_test.py")]))

"""Install the local practice environment outside the Dropbox source tree."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[2]
ENV = Path(tempfile.gettempdir()) / ("interview-handbook-python-" + hashlib.sha256(str(ROOT).encode()).hexdigest()[:10])


def python_path():
    return Path(os.environ.get("PRACTICE_PYTHON", str(ENV / "bin/python")))


if __name__ == "__main__":
    if not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise SystemExit("Use Python 3.11–3.13 to create the practice environment.")
    if not python_path().exists():
        venv.create(ENV, with_pip=True)
    subprocess.run([str(python_path()), "-m", "pip", "install", "--disable-pip-version-check", "-r",
                    str(Path(__file__).with_name("requirements.txt")), "-c",
                    str(Path(__file__).with_name("requirements.lock"))], check=True)
    # Font discovery is expensive on macOS. Build the cache once during setup,
    # not inside each short-lived execution process.
    environment = {**os.environ, "MPLBACKEND": "Agg", "MPLCONFIGDIR": str(python_path().parent.parent / "practice-matplotlib")}
    subprocess.run([str(python_path()), "-c", "import matplotlib.pyplot as plt; import io; plt.plot([0,1]); plt.savefig(io.BytesIO(),format='png'); plt.close('all')"], env=environment, check=True)
    print("Practice Python:", python_path())

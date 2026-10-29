#!/usr/bin/env python3
"""Run the exact displayed code/tests for the 2026-10-28 additions.

Use a Python environment with NumPy and PyTorch. No model downloads required.
"""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content/sources/frontier-coding-2026-10-28/cards.json"


def main():
    records = json.loads(MANIFEST.read_text())
    with tempfile.TemporaryDirectory(prefix="frontier-coding-check-") as folder:
        for item in records:
            source = (ROOT / item["file"]).read_text()
            blocks = re.findall(r"^```python\n(.*?)^```", source, re.M | re.S)
            assert len(blocks) == 2, item["id"]
            code = "\n\n".join(blocks)
            compile(code, item["id"], "exec")
            path = Path(folder) / (item["id"] + ".py")
            path.write_text(code)
            result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise RuntimeError(f"{item['id']}:\n{result.stdout}\n{result.stderr}")
            print(item["id"], result.stdout.strip(), flush=True)
    print(f"All {len(records)} new coding programs passed.")


if __name__ == "__main__":
    main()

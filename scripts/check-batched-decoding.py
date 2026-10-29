#!/usr/bin/env python3
"""Execute the exact Python implementations and tests published in batch cards.

Run with a Python environment containing PyTorch. No model downloads are needed.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "content/handbooks/apple-interview/questions/decoding"
IDS = (
    "apple-batched-token-selection",
    "apple-batched-generation",
    "apple-batched-beam-search",
)


def main():
    with tempfile.TemporaryDirectory(prefix="batch-decoding-check-") as directory:
        for question_id in IDS:
            source = (CARDS / f"{question_id}.md").read_text()
            blocks = re.findall(r"^```python\n(.*?)^```", source, re.M | re.S)
            if len(blocks) < 2:
                raise RuntimeError(f"{question_id}: missing implementation/tests")
            program = "\n\n".join(blocks)
            compile(program, question_id, "exec")
            target = Path(directory) / f"{question_id}.py"
            target.write_text(program)
            result = subprocess.run(
                [sys.executable, str(target)], capture_output=True, text=True,
                timeout=60, cwd=ROOT,
            )
            if result.returncode:
                raise RuntimeError(f"{question_id}:\n{result.stdout}\n{result.stderr}")
            print(f"{question_id}: {result.stdout.strip()}")
    print("All 3 published batch decoding implementations passed.")


if __name__ == "__main__":
    main()

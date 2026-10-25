#!/usr/bin/env python3
"""Check coding-test guidance; optionally execute the displayed simple examples.

Usage: python3 scripts/check-simple-tests.py [--execute]
Numerical examples require NumPy and PyTorch in the selected Python environment.
Existing complete practice suites retain their dedicated check-* scripts.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^(?:#{2,3} 简单测试怎么写|<h2>简单测试怎么写</h2>)", re.M)
CODE = re.compile(
    r"^```(python|javascript)\n(.*?)^```|<pre[^>]*>(.*?)</pre>", re.M | re.S
)


def code_blocks(text):
    result = []
    for match in CODE.finditer(text):
        language, fenced, raw = match.groups()
        if raw is not None:
            # Legacy code is escaped HTML, occasionally with highlighting spans.
            result.append(("python", unescape(re.sub(r"<[^>]+>", "", raw))))
        else:
            result.append((language, fenced))
    return result


def is_coding(path, text, blocks):
    frontmatter = text.split("---", 2)[1]
    code = "\n".join(block for _, block in blocks)
    has_tests = bool(re.search(r"\bassert\b|\btest_|assert\.", code))
    has_tests = has_tests or bool(HEADING.search(text))
    implementation = bool(re.search(r"^\s*(?:async )?(def |class |function )", code, re.M))
    return has_tests or implementation and (
        path.parts[-4].startswith("leetcode")
        or path.parent.name in ("coding", "rl-coding", "alibaba-oa")
        or "ml-101" in path.parts
        or re.search(r"^  - (?:Coding|AI Coding)\s*$", frontmatter, re.M)
    )


def execute(entry):
    path, program = entry
    with tempfile.TemporaryDirectory(prefix="handbook-simple-") as directory:
        script = Path(directory) / "solution.py"
        script.write_text(program)
        try:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=ROOT,
                capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            return f"{path}: timed out after 60 seconds"
        if result.returncode:
            return f"{path}:\n{result.stdout}\n{result.stderr}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    count = 0
    programs = []
    for path in sorted((ROOT / "content/handbooks").glob("*/questions/**/*.md")):
        text = path.read_text()
        blocks = code_blocks(text)
        if not blocks or not is_coding(path, text, blocks):
            continue
        headings = list(HEADING.finditer(text))
        assert len(headings) == 1, f"{path}: expected one simple-test section"
        count += 1
        start = headings[0].end()
        tail = text[start:]
        end = re.search(r"^#{2,3} |<h2>", tail, re.M)
        section = tail[:end.start()] if end else tail
        examples = code_blocks(section)
        if not examples:
            assert "测试" in section and ("assert" in section or "场景" in section), path
            continue
        assert all(language == "python" for language, _ in examples), path
        example = "\n\n".join(block for _, block in examples)
        tree = ast.parse(example, filename=str(path))
        assert any(
            isinstance(node, ast.Assert) or isinstance(node, ast.Call)
            and "assert" in ast.unparse(node.func)
            for node in ast.walk(tree)
        ), path
        # Only the primary implementation is needed for LeetCode; later blocks
        # discuss follow-ups. Other new examples may need multiple definitions.
        preceding = code_blocks(text[:headings[0].start()])
        if any(part.startswith("leetcode-") for part in path.parts):
            preceding = preceding[:1]
        if path.stem == "code-attention":
            preceding = preceding[:1]
        if path.stem == "code-ppo-grpo-gspo":
            # The last Python block configures an external trainer; this small
            # loss example only needs the preceding standalone torch functions.
            preceding = preceding[:-1]
        if path.stem in ("code-fw-miles", "code-fw-verl"):
            # These are framework fragments. Their examples supply inputs and
            # repeat the short formula, so they run as standalone programs.
            preceding = []
        source = "\n\n".join(block for _, block in preceding)
        module = ast.parse(source, filename=str(path))
        module.body = [node for node in module.body if not (
            isinstance(node, ast.If) and "__main__" in ast.unparse(node.test)
        )]
        imports = ""
        if path.stem in ("code-rmsnorm", "code-gae", "code-rope"):
            imports = "import torch\nimport torch.nn as nn\n"
        program = imports + ast.unparse(module) + "\n\n" + example
        programs.append((path.relative_to(ROOT), program))
    print(f"Guidance coverage: {count} coding cards; {len(programs)} displayed simple examples.")
    if args.execute:
        with ThreadPoolExecutor(max_workers=4) as pool:
            failures = [failure for failure in pool.map(execute, programs) if failure]
        if failures:
            print("\n\n".join(failures), file=sys.stderr)
            raise SystemExit(1)
        print(f"PASS: all {len(programs)} displayed simple examples executed.")


if __name__ == "__main__":
    main()

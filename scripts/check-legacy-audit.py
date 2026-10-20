#!/usr/bin/env python3
"""Validate displayed code, contracts, coverage and optional runtime execution."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile


def practice_section(text):
    """Return the '## 完整编程练习' section: from that heading up to the next level-2 heading."""
    body = text.split('---', 2)[2]
    start = body.index('## 完整编程练习')
    rest = body[start:]
    following = re.search(r'^## ', rest[2:], re.M)
    return rest if following is None else rest[:following.start() + 2]


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'content/sources/legacy-coding-audit-2026-10-18'
entries = json.loads((ARCHIVE / 'manifest.json').read_text())
entries += json.loads((ROOT / 'content/sources/legacy-coding-repair-2026-10-18/manifest.json').read_text())
assert len({entry['id'] for entry in entries}) == len(entries)
expected = {entry['id'] for entry in entries}
# The audit is an archived 420-card snapshot, not a ban on future authored cards.
inventory = json.loads((ARCHIVE / 'inventory.json').read_text())
old = [ROOT / entry['file'] for entry in inventory]

actual = set()
programs = {}
for path in old:
    text = path.read_text()
    if '## 完整编程练习' not in text:
        continue
    identifier = re.search(r'^id: (.*)$', text, re.M)[1]
    actual.add(identifier)
    assert '  - 完整编程练习' in text.split('---', 2)[1], identifier
    practice = practice_section(text)
    for heading in ('题面、接口与约束', '输入输出示例', '解题思路与正确性',
                    '完整参考实现', '可执行测试', '复杂度与追问'):
        assert '### ' + heading in practice, (identifier, heading)
    blocks = re.findall(r'^```python\n(.*?)^```', practice, re.M | re.S)
    assert len(blocks) == 2, identifier
    program = '\n\n'.join(blocks).strip() + '\n'
    ast.parse(program)
    digest = hashlib.sha256(program.encode()).hexdigest()
    entry = next(item for item in entries if item['id'] == identifier)
    if entry.get('displayedSha256'):
        assert digest == entry['displayedSha256'], identifier
        assert program == (ROOT / entry['solution']).read_text(), identifier
    programs.setdefault(digest, (identifier, program))
assert expected == actual, {'missing': sorted(expected-actual), 'unexpected': sorted(actual-expected)}
if '--execute' in sys.argv:
    for identifier, program in programs.values():
        with tempfile.TemporaryDirectory(prefix='handbook-audit-') as directory:
            path = Path(directory) / 'exercise.py'
            path.write_text(program)
            result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=60)
            assert result.returncode == 0, (identifier, result.stdout, result.stderr)
        print('PASS', identifier, flush=True)
print(f'{len(old)} old cards inventoried; {len(actual)} complete exercises; '
      f'{len(programs)} unique displayed programs verified.'
      + (' Executed all.' if '--execute' in sys.argv else ' Use --execute for runtime checks.'))

#!/usr/bin/env python3
"""Run the actual implementations and tests displayed in repaired legacy cards."""
from pathlib import Path
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
ARCHIVE = ROOT / 'content/sources/legacy-coding-repair-2026-10-18'
entries = json.loads((ARCHIVE / 'manifest.json').read_text())
assert len({entry['id'] for entry in entries}) == len(entries)
seen = set()
for entry in entries:
    text = (ROOT / entry['file']).read_text()
    assert '  - 完整编程练习' in text.split('---', 2)[1], entry['id']
    practice = practice_section(text)
    assert practice.strip().startswith('## 完整编程练习'), entry['id']
    for heading in ('题面、接口与约束', '输入输出示例', '解题思路与正确性',
                    '完整参考实现', '可执行测试', '复杂度与追问'):
        assert '### ' + heading in practice, (entry['id'], heading)
    blocks = re.findall(r'^```python\n(.*?)^```', practice, re.M | re.S)
    assert len(blocks) == 2, entry['id']
    program = '\n\n'.join(blocks)
    digest = hashlib.sha256(program.encode()).hexdigest()
    if digest not in seen:
        with tempfile.TemporaryDirectory(prefix='legacy-coding-') as directory:
            path = Path(directory) / 'exercise.py'
            path.write_text(program)
            result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=60)
            assert result.returncode == 0, (entry['id'], result.stdout, result.stderr)
        seen.add(digest)
    print('PASS', entry['id'])
print(f'{len(entries)} original cards, {len(seen)} unique displayed implementations passed.')

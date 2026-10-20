#!/usr/bin/env python3
"""Execute and compare the exact KV prefix implementations printed in the handbook."""
from pathlib import Path
from html.parser import HTMLParser
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'content/sources/kv-prefix-implementation-2026-10-18'
manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
assert len(manifest) == 8 and len({item['id'] for item in manifest}) == 8


class RenderedCode(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pre = False
        self.code = False
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.pre = True
        # Only Python blocks are practice code; ```text example blocks render as language-plaintext.
        if tag == 'code' and self.pre and 'language-python' in (dict(attrs).get('class') or ''):
            self.code = True
            self.blocks.append('')

    def handle_endtag(self, tag):
        if tag == 'code':
            self.code = False
        if tag == 'pre':
            self.pre = False

    def handle_data(self, data):
        if self.code:
            self.blocks[-1] += data


for item in manifest:
    text = (ROOT / item['file']).read_text()
    assert 'realInterview: false' in text
    assert '  - 完整编程练习' in text
    for heading in ('题面、接口与约束', '输入输出示例', '解题思路与正确性',
                    '完整参考实现', '可执行测试', '复杂度与追问'):
        assert '### ' + heading in text, (item['id'], heading)
    blocks = re.findall(r'^```python\n(.*?)^```', text, re.M | re.S)
    assert len(blocks) == 2, item['id']
    reference = (ROOT / item['solution']).read_text()
    implementation, tests = reference.split('# === TESTS ===', 1)
    assert blocks[0].strip() == implementation.strip(), item['id']
    assert blocks[1].strip() == tests.strip(), item['id']
    if '--rendered' in sys.argv:
        rendered = ROOT / 'public/content/us-tech-interview/systems' / (item['id'] + '.json')
        parser = RenderedCode()
        parser.feed(json.loads(rendered.read_text()))
        assert [code.strip() for code in parser.blocks] == [code.strip() for code in blocks], item['id']
    digest = hashlib.sha256(reference.encode()).hexdigest()
    assert digest == item['sha256'], item['id']
    program = '\n\n'.join(blocks)
    ast.parse(program)
    with tempfile.TemporaryDirectory(prefix='kv-prefix-practice-') as directory:
        target = Path(directory) / 'exercise.py'
        target.write_text(program)
        result = subprocess.run([sys.executable, str(target)], cwd=ROOT,
                                capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, (item['id'], result.stdout, result.stderr)
    print('PASS', item['id'], flush=True)
    item['tested'] = True
(ARCHIVE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('All 8 standalone displayed exercises passed.')

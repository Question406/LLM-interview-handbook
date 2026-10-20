#!/usr/bin/env python3
"""Validate every reconstructed practice and execute each unique reference module."""
from pathlib import Path
import collections
import ast
import textwrap
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
AR=ROOT/'content/sources/1point3acres-frontier-2026-10-18'
records=json.loads((AR/'curated.json').read_text())['records']
manifest=json.loads((AR/'practice/manifest.json').read_text())
assert len({x['id'] for x in manifest})==len(manifest), 'duplicate audit ids'
assert {x['id'] for x in manifest}=={x['id'] for x in records}, 'audit coverage mismatch'
by_id={r['id']:r for r in records}
modules={}
for entry in manifest:
    body=(ROOT/by_id[entry['id']]['file']).read_text()
    if entry.get('solution'):
        assert '## 完整编程练习' in body and '### 输入输出示例' in body and '### 可执行测试' in body,entry['id']
        assert '\x00' not in body,entry['id']
        blocks=re.findall(r'^```(?:python|javascript)\n(.*?)^```',body,re.M|re.S)
        assert len(blocks)==2,entry['id']
        reference=(ROOT/entry['solution']).read_text()
        assert reference.startswith(blocks[0].rstrip()+'\n'), 'Displayed code differs: '+entry['id']
        if entry.get('language','python')=='python':
            ast.parse(blocks[0]+'\n'+blocks[1])
            assert textwrap.indent(blocks[1].strip()+'\n','    ') in reference, 'Displayed tests differ: '+entry['id']
        else:
            assert blocks[1].strip() in reference, 'Displayed JS tests differ: '+entry['id']
        modules[entry['solution']]=entry.get('language','python')
    else:
        assert '## 完整非编程练习' in body,entry['id']
        assert entry.get('reviewed') is True,entry['id']
for relative,language in sorted(modules.items()):
    path=ROOT/relative
    command=['node',str(path)] if language=='javascript' else [sys.executable,str(path)]
    completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
    if completed.returncode:
        print(relative,completed.stdout,completed.stderr,sep='\n',file=sys.stderr)
        raise SystemExit(completed.returncode)
    print('PASS',path.name,flush=True)
for entry in manifest:
    if entry.get('solution'):
        entry['tested']=True
        entry['solutionSha256']=hashlib.sha256((ROOT/entry['solution']).read_bytes()).hexdigest()
(AR/'practice/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
summary=dict(reviewedCards=len(manifest),codingCards=sum('solution' in x for x in manifest),nonCodingCards=sum('solution' not in x for x in manifest),testedImplementations=len(modules),byLanguage=dict(collections.Counter(modules.values())))
(AR/'practice/validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))

from pathlib import Path
from html.parser import HTMLParser
import json,re
class Code(HTMLParser):
 def __init__(self):super().__init__();self.pre=0;self.in_code=False;self.blocks=[]
 def handle_starttag(self,tag,attrs):
  if tag=='pre':self.pre+=1
  # Only Python blocks are practice code; ```text example blocks render as language-plaintext.
  if tag=='code' and self.pre and 'language-python' in (dict(attrs).get('class') or ''):self.in_code=True;self.blocks.append('')
 def handle_endtag(self,tag):
  if tag=='code':self.in_code=False
  if tag=='pre':self.pre-=1
 def handle_data(self,data):
  if self.in_code:self.blocks[-1]+=data
def practice_section(text):
    """Return the '## 完整编程练习' section: from that heading up to the next level-2 heading."""
    body = text.split('---', 2)[2]
    start = body.index('## 完整编程练习')
    rest = body[start:]
    following = re.search(r'^## ', rest[2:], re.M)
    return rest if following is None else rest[:following.start() + 2]

root=Path(__file__).resolve().parents[1];ar=root/'content/sources/legacy-coding-audit-2026-10-18'
entries=json.loads((ar/'manifest.json').read_text())+json.loads((root/'content/sources/legacy-coding-repair-2026-10-18/manifest.json').read_text());bad=[];debug=0
for e in entries:
 text=(root/e['file']).read_text();section=re.search(r'^section: (.*)$',text,re.M)[1]
 html=json.loads((root/'public/content/us-tech-interview'/section/(e['id']+'.json')).read_text())
 p=Code();p.feed(html);expected=re.findall(r'^```python\n(.*?)^```',practice_section(text),re.M|re.S)
 if [s.strip() for s in p.blocks[:2]]!=[s.strip() for s in expected]:bad.append(e['id'])
 if '故意错误的起始片段（用于找 bug）' in text:
  if '故意错误的起始片段（用于找 bug）' not in html:bad.append(e['id']+' debug example stale')
  debug+=1
assert not bad,bad
print('Rendered code exactly matches all 70 current source cards; debug examples:',debug)

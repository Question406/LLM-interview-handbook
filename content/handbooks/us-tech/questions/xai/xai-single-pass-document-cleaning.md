---
id: xai-single-pass-document-cleaning
section: xai
order: 935
level: A
title: "xAI Data Coding：single-pass web-document cleaning 与 audit counters"
quick: "我会先把每个 reject reason 的优先级写出来。不然同一条数据既 license 不合格又太短，统计时可能被算两次，最后 counts 对不上。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI Data Coding：single-pass web-document cleaning 与 audit counters"
    url: "https://landthelab.com/companies/xai"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 xAI 目录提到百万 crawled documents 的 single-pass cleaning take-home。以下实现其 record-processing 核心；license allowlist、Unicode normalization、长度和 deduplication policy 由手册设定。

### 输入、接口与规则

实现 `clean_documents(records, allowed_licenses, min_chars=4) -> (accepted, counters)`。records 是只能遍历一次的 dict iterable；每条含唯一 string id、string text、string license、string url。min_chars 为非负整数，allowed_licenses 是 string set。不读真实 Parquet，也不访问 URL。

按如下优先级每条只记一个 outcome：license 不在 allowlist -> license；否则对 text 做 Unicode NFKC，再把所有空白折叠为一个 ASCII space 并 strip；长度小于 min_chars -> short；否则与此前 accepted 的 normalized text 完全相同 -> duplicate；其余 -> accepted。accepted 保持输入顺序，每条返回 id/url/normalized text/SHA-256 hex digest；counters 含 seen、license、short、duplicate、accepted 五个键。拒绝条目不参与 deduplication，不修改 records。

### 输入输出示例

```text
输入 ids 依次为 a:"Ａ B"/ok, b:"A  B"/ok, c:"x"/ok, d:"long"/bad，min_chars=3。
accepted 只有 a，normalized text="A B"。
counters={seen:4,license:1,short:1,duplicate:1,accepted:1}。
```

## 回答思路

> **Situation / Task：** Single pass 中必须固定规则顺序，audit counters 才能解释数据减少原因。  
> **Approach / Why：** 先 policy filter，再 normalization、长度检查和 exact deduplication，保留 lineage。  
> **Result / Check：** 检查 Unicode 等价、只消费一次输入、拒绝条目不污染 seen set。

## 解题思路与参考答案

我会先把每个 reject reason 的优先级写出来。不然同一条数据既 license 不合格又太短，统计时可能被算两次，最后 counts 对不上。

Normalization 后才做长度检查和 deduplication；输出保留原 id 与 URL，方便追查样本来源。这里用 exact normalized text 集合保证正确性，所以 single pass 不代表 constant memory。百万文档要按容量选择外部索引或落盘，不能只把 generator 当成解决全部规模问题。

### 完整参考实现

```python
import unicodedata
import hashlib


def clean_documents(records, allowed_licenses, min_chars=4):
    if min_chars < 0:
        raise ValueError('negative min_chars')
    accepted = []
    seen = set()
    counters = {k: 0 for k in ['seen', 'license', 'short', 'duplicate', 'accepted']}
    for record in records:
        counters['seen'] += 1
        if record['license'] not in allowed_licenses:
            counters['license'] += 1
            continue
        text = ' '.join(unicodedata.normalize('NFKC', record['text']).split())
        if len(text) < min_chars:
            counters['short'] += 1
            continue
        if text in seen:
            counters['duplicate'] += 1
            continue
        seen.add(text)
        counters['accepted'] += 1
        accepted.append(
            {
                'id': record['id'],
                'url': record['url'],
                'text': text,
                'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            }
        )
    return accepted, counters
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
rows = [
    {'id': i, 'text': t, 'license': lic, 'url': 'https://example.org/' + i}
    for i, t, lic in [
        ('a', 'Ａ B', 'ok'),
        ('b', 'A  B', 'ok'),
        ('c', 'x', 'ok'),
        ('d', 'long', 'bad'),
    ]
]


class Once:
    def __init__(self, rows):
        self.rows = rows
        self.used = False

    def __iter__(self):
        assert not self.used, 'second pass'
        self.used = True
        yield from self.rows


accepted, counts = clean_documents(Once(rows), {'ok'}, 3)
assert [r['id'] for r in accepted] == ['a']
assert accepted[0]['text'] == 'A B'
assert len(accepted[0]['sha256']) == 64
assert counts == {'seen': 4, 'license': 1, 'short': 1, 'duplicate': 1, 'accepted': 1}
assert rows[0]['text'] == 'Ａ B'
# A rejected earlier duplicate does not suppress a later acceptable document.
rows[0]['license'] = 'bad'
accepted, counts = clean_documents(iter(rows), {'ok'}, 3)
assert [r['id'] for r in accepted] == ['b']
assert counts['seen'] == sum(
    counts[k] for k in ['license', 'short', 'duplicate', 'accepted']
)
print('document pipeline tests passed')
```

## 复杂度与追问

总字符量 B、接受字符量 A，期望处理时间约 `O(B)`，空间 `O(A)` 加返回内容。Counters 满足 `seen=license+short+duplicate+accepted`。Allowlist 是题设 policy，不应从任意 URL 或 license string 推断真实使用授权。

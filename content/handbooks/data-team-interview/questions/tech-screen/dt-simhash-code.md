---
id: dt-simhash-code
section: tech-screen
order: 10
level: A
title: CoderPad：SimHash 怎么写，什么时候不用 MinHash？
quick: >-
  我会把特征哈希到 $f$ 维，按权重对每 bit 投 +1 / -1，符号变成指纹。汉明距离小就是近重复。
  短标题、URL、query 用 SimHash；长网页近重复仍用 `dt-minhash-code` 的 Jaccard。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - SimHash
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Similarity Estimation Techniques from Rounding Algorithms (Charikar)
    url: https://www.cs.princeton.edu/courses/archive/spring04/cos598B/bib/CharikarEstim.pdf
    type: primary
  - title: Detecting Near-Duplicates for Web Crawling (Manku et al., WWW 2007)
    url: https://www.wwwconference.org/www2007/papers/paper215.pdf
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
---

SimHash 先把特征哈希到 $f$ 维；每个特征按权重给各 bit 累加 +1 或 -1，最后用每一维的正负号生成指纹。汉明距离小就是近重复。短标题、URL、query 用它；长网页近重复仍用 `dt-minhash-code` 的 Jaccard。MinHash 近似集合 Jaccard，短文本集合太小，$J$ 对少量词的变化很敏感。

Charikar：每个特征 $t$ 有权重 $w_t$（词频或 BM25）。$f$ 个哈希把 $t$ 映到 $\pm 1$ 向量，按 $w_t$ 累加，每维看符号。Manku 2007 用来抓网页近重复，汉明距离 $\le 3$（64-bit）当候选。

## 指纹：加权随机投影的符号

```python
import hashlib
import re
from collections import Counter


def features(text):
    """词频当权重。"""
    return Counter(re.findall(r"\w+", text.lower()))


def _bits(token, f=64):
    digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
    return int.from_bytes(digest, "little") & ((1 << f) - 1)


def simhash(text, f=64):
    """f-bit SimHash：每个特征按权重给各 bit 投 +w / -w，最后取符号。"""
    if not 1 <= f <= 64:
        raise ValueError("f must be in [1, 64] (the feature hash has 64 bits)")
    acc = [0] * f
    for token, weight in features(text).items():
        bits = _bits(token, f)
        for i in range(f):
            acc[i] += weight if (bits >> i) & 1 else -weight
    fingerprint = 0
    for i, vote in enumerate(acc):
        if vote >= 0:
            fingerprint |= 1 << i
    return fingerprint


def hamming(a, b):
    return (a ^ b).bit_count()  # Python 3.10+
```

### 可执行测试

```python
title = "Apple announces new foundation models for on device intelligence"
near = "Apple announces new foundation models for on-device intelligence today"
different = "Recipe for a quick tomato pasta with garlic and basil"

# 相同文本指纹相同；大小写不影响
assert simhash(title) == simhash(title.upper())

# 近重复标题的汉明距离明显小于无关标题
assert hamming(simhash(title), simhash(near)) < hamming(simhash(title), simhash(different))
assert hamming(simhash(title), simhash(near)) <= 12

# 指纹不超过 f 位
assert simhash(title, f=32) < (1 << 32)

# 汉明距离按 bit 计
assert hamming(0b1010, 0b0110) == 2

# 特征哈希只有 64 bit，f 超过 64 是调用错误
try:
    simhash(title, f=128)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

近邻检索不能对所有文档两两计算汉明距离，否则需要 $O(N^2)$ 次比较。Manku 的办法：把 64-bit 切成 $k$ 块，对每块建表；只探「某一块完全相同」的桶，再算精确汉明。和 LSH band 是同一类思想，见 `dt-minhash-code`。

## 不同输入适合哪种指纹

| 输入 | 指纹 | 原因 |
| --- | --- | --- |
| 长网页、转载、改页脚 | MinHash + Jaccard | 集合重叠稳定 |
| 标题、query、短 caption | SimHash + 汉明 | shingle 集合太小 |
| 字节级复制 | 精确哈希 | 更便宜，先做 |
| 释义 / 翻译 | embedding | 词面指纹不够 |

短文档 SimHash 也对空白和词序更敏感。标题去重前先做 `dt-unicode-canon-code`。图文对的 caption 近重复可以 SimHash；图本身近重复走 pHash / embedding，见 `dt-clip-filter-code`。

## 追问

- **权重用 1 行吗？** 短文本可以。长网页用词频，停用词会主导符号，先剥导航再算。
- **64-bit 碰撞？** 指纹碰撞不等于近重复，汉明 0 仍要抽查。高价值许可书不要只靠这一层丢掉。
- **和 MinHash 能不能都跑？** 可以，当两路候选。最终仍用精确 Jaccard 或人工抽查定阈值。

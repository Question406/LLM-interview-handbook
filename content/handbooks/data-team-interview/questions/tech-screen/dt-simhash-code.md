---
id: dt-simhash-code
section: tech-screen
order: 10
level: A
title: CoderPad：SimHash 怎么写，什么时候不用 MinHash？
quick: "SimHash 把每个特征哈希到 $f$ 维，按权重给每个 bit 投 +1 或 -1，最后取各维的符号作为指纹，汉明距离小就是近重复。它适合短标题、URL 和 query，因为短文本的 shingle 集合太小，Jaccard 不稳；长网页近重复仍用 `dt-minhash-code` 的 Jaccard。"
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

SimHash 解决的是短文本近重复。MinHash 近似的是集合 Jaccard，标题、URL、query 这类短文本的 shingle 集合太小，改一两个词 $J$ 就大幅变化。SimHash 的做法是把特征哈希到 $f$ 维，每个特征按权重给各 bit 累加 +1 或 -1，最后取每一维的正负号作为指纹，汉明距离小就是近重复。长网页的近重复仍用 `dt-minhash-code` 的 Jaccard。

这是 Charikar 的构造：每个特征 $t$ 有权重 $w_t$（词频或 BM25），$f$ 个哈希把 $t$ 映到一个 $\pm 1$ 向量，按 $w_t$ 加权累加，每一维看符号。Manku 2007 用它抓网页近重复，64-bit 指纹下汉明距离 $\le 3$ 当候选。

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

检索近邻时不能对所有文档两两算汉明距离，那是 $O(N^2)$ 次比较。Manku 的办法是把 64-bit 切成 $k$ 块，每块建一张表，只探「某一块完全相同」的桶，再算精确汉明距离。这和 LSH 的 band 是同一类思想，见 `dt-minhash-code`。

## 不同输入适合哪种指纹

| 输入 | 指纹 | 原因 |
| --- | --- | --- |
| 长网页、转载、改页脚 | MinHash + Jaccard | 集合重叠稳定 |
| 标题、query、短 caption | SimHash + 汉明 | shingle 集合太小 |
| 字节级复制 | 精确哈希 | 更便宜，先做 |
| 释义 / 翻译 | embedding | 词面指纹不够 |

短文档的 SimHash 对空白和词序也更敏感，所以标题去重之前先做 `dt-unicode-canon-code`。图文对里，caption 的近重复可以用 SimHash；图片本身的近重复走 pHash 或 embedding，见 `dt-clip-filter-code`。

## 追问

- **权重都用 1 行不行？** 短文本可以。长网页用词频，但停用词会主导符号，要先剥掉导航再算。
- **64-bit 会碰撞吗？** 指纹碰撞不等于近重复，汉明距离为 0 也要抽查。高价值的许可书要再经过一层确认才能丢。
- **能和 MinHash 一起跑吗？** 可以，当作两路候选。最终仍用精确 Jaccard 或人工抽查来定阈值。

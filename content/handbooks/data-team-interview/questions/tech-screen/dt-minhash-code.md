---
id: dt-minhash-code
section: tech-screen
order: 2
level: A
title: CoderPad：手写 MinHash + LSH，近重复去重怎么讲规模？
quick: "先把文档拆成 shingle 集合，生成 MinHash 签名，再用 LSH 分段找候选。MinHash 某一维相等的概率对应 Jaccard；任一 band 完全相等就进入候选，最终仍用精确 Jaccard 复核。规模分析要估候选对数，不能声称精确去重只需 $O(N)$。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - MinHash
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Mining of Massive Datasets, Ch.3 (Finding Similar Items)"
    url: http://infolab.stanford.edu/~ullman/mmds/ch3n.pdf
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
---

先拆 shingle、生成 MinHash 签名，再让 LSH 找出可能重复的候选对。只有计算精确 Jaccard 后才决定是否去重。这样避免对所有文档两两比较，但总成本仍取决于候选数量，不能直接说精确去重是 $O(N)$。MinHash 也不是加密哈希。

Lee et al. 2021：训练集近重复浪费算力，也会让评测里「看起来像新文档」变熟。去重是能力干预，不是磁盘清理。

## 数学先说 20 秒

文档 $A,B$ 看成 shingle 集合。Jaccard $J(A,B)=|A\cap B|/|A\cup B|$。独立置换 $\pi$ 下，

$$
\Pr[\min\pi(A)=\min\pi(B)]=J(A,B).
$$

$k$ 个独立哈希得到长度 $k$ 的签名。LSH：把签名切成 $b$ 段、每段 $r$ 维，$k=br$。一对文档在某一 band 完全相同的概率是 $1-(1-J^r)^b$。阈值附近要陡，先定目标 $J_0$（网页常 0.8 左右），再选 $b,r$。

## 白板能跑的最小实现

```python
import hashlib
import re
from collections import defaultdict


def shingles(text, n=5):
    tokens = re.findall(r"\w+", text.lower())
    if len(tokens) < n:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def _hash(seed, s):
    return int(hashlib.blake2b(f"{seed}:{s}".encode(), digest_size=8).hexdigest(), 16)


def minhash(text, k=128, n=5):
    """k 个带种子的哈希各取最小值，组成长度 k 的签名。"""
    shingle_set = shingles(text, n)
    if not shingle_set:
        return tuple(0 for _ in range(k))
    return tuple(min(_hash(i, x) for x in shingle_set) for i in range(k))


def lsh_candidates(signatures, b=16, r=8):
    """signatures: list[(doc_id, signature)]，签名长度必须等于 b*r。

    任一 band 完全相同的两篇文档成为候选对，返回 {(小 id, 大 id)}。
    """
    buckets = defaultdict(set)
    for doc_id, signature in signatures:
        if len(signature) != b * r:
            raise ValueError(f"signature length {len(signature)} != b*r = {b * r}")
        for band in range(b):
            piece = signature[band * r:(band + 1) * r]
            buckets[(band, piece)].add(doc_id)
    pairs = set()
    for group in buckets.values():
        ids = sorted(group)
        for i, first in enumerate(ids):
            for second in ids[i + 1:]:
                pairs.add((first, second))
    return pairs


def jaccard(a, b, n=5):
    """两段文本 shingle 集合的精确 Jaccard，用来复核候选对。"""
    set_a = shingles(a, n)
    set_b = shingles(b, n)
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)
```

### 可执行测试

```python
base = " ".join(f"word{i}" for i in range(200))
reprint = base + " footer copyright example"  # 只改了页脚的转载
unrelated = " ".join(f"other{i}" for i in range(200))

# 精确 Jaccard：转载接近 1，无关文档为 0
assert jaccard(base, reprint) > 0.95
assert jaccard(base, unrelated) == 0.0
assert jaccard("", "") == 1.0

# 签名逐位相等的比例近似 Jaccard
sig_base = minhash(base)
sig_reprint = minhash(reprint)
agreement = sum(x == y for x, y in zip(sig_base, sig_reprint)) / len(sig_base)
assert agreement > 0.9

# LSH：转载成为候选对，无关文档不是
sigs = [("a", sig_base), ("b", sig_reprint), ("c", minhash(unrelated))]
assert lsh_candidates(sigs) == {("a", "b")}

# 短于 n 个词的文本整体当作一个 shingle
assert shingles("Hello, world") == {"hello world"}

# 签名长度和 b*r 不一致是调用错误
try:
    lsh_candidates([("a", sig_base)], b=10, r=10)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

写完我立刻讲三处工程补丁，否则像课后作业：

1. 哈希。生产用 $k$ 个独立乘法哈希或预计算的 permutation seed，不要在热路径上跑 $k\cdot|\mathrm{shingles}|$ 次 blake2。上面这样写是为了不依赖 numpy。
2. 候选爆炸。某个 band 若撞上「版权声明」这种全球重复 boiler，一个桶会进几百万文档。按域分片、先剥 boilerplate、对超大桶再切一层。
3. 复核。LSH 只出候选。最终用精确 Jaccard 或编辑距离，阈值按域、按长度分开。短文档 $J$ 不稳定，公式和许可证要单独白名单。

## 规模怎么报

$N=10^9$ 文档时，签名存盘是 $N\times k\times 8$ 字节量级（$k=128$ 约 1 TB）。LSH 是 shuffle `(band_id, band_key) → doc_id`，每个桶内两两，期望候选远小于 $N^2$。口播给数量级：目标 $J=0.8$、$r=8$、$b=16$ 时，$J=0.8$ 的召回接近 1，$J=0.4$ 的误召回被压下去。数字现场用 $1-(1-J^r)^b$ 算一个点就够，不要背表。

和评测隔离的顺序：先对冻结评测集算签名，训练文档只和评测桶比。训练内部去重可以更激进；对评测只要「像到不能当新题」。

## 追问

- **MinHash 能去语义重复吗？** 不能。它近似词面 Jaccard。释义、翻译、改写要上 embedding 近邻，成本高两个数量级，只对高价值子集做。
- **为什么不先精确哈希？** 精确哈希去的是字节级复制，便宜，先做。MinHash 吃的是改了空白和页脚的转载。
- **阈值怎么定？** 抽 1k 对人工看：误杀的正当 paraphrase vs 漏掉的转载。按域定，不要全局 0.8。

---
id: dt-minhash-code
section: tech-screen
order: 2
level: A
title: CoderPad：手写 MinHash + LSH，near-duplicate deduplication 怎么讲规模？
quick: >-
  先把文档拆成 shingle 集合并生成 MinHash 签名，再用 LSH 分段找候选：签名某一维相等的概率等于 Jaccard，任一 band
  完全相等就进候选。候选最后仍要用精确 Jaccard 复核。规模分析要估候选对数，因为总成本取决于候选数量。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Mining of Massive Datasets, Ch.3 (Finding Similar Items)'
    url: 'http://infolab.stanford.edu/~ullman/mmds/ch3n.pdf'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

为文本 near-duplicates 检测实现 shingle、MinHash 签名、LSH 候选对与精确 Jaccard 接口。候选对只表示可能相似，不能直接当成重复删除结论。

### 输入与接口

- `shingles(text,n=5)` 按小写的字母数字/下划线词片段形成 n 词窗口集合；非空短文本整体作为一个 shingle。
- `minhash(text,k=128,n=5)` 返回长度 k 的确定性整数签名。每个签名位置使用 `BLAKE2b(str(seed)+":"+shingle,digest_size=8)`，seed 为该位置的下标。
- `lsh_candidates(signatures,b=16,r=8)` 接受 `(doc_id,signature)` 列表，签名长度均为 b*r；`jaccard(a,b,n=5)` 接受两段文本。

### 输出与约束

`lsh_candidates` 返回 `(较小ID,较大ID)` 的无重复集合：只要两个签名任一对应 band 的 r 个值完全相同，就构成候选。`jaccard` 返回两侧 shingle 集合交集大小除以并集大小；两侧都空时为 1。

MinHash 每个位置表示该位置对应哈希在文档 shingle 集合上的最小值；空文档签名为 k 个 0。重复 shingle 不增加集合大小；ID 保证可排序，相同输入与参数结果必须可复现。

### 示例

```text
shingles("Hello, WORLD",n=5) -> {"hello world"}
jaccard("a b c","a b d",n=1) -> 0.5
lsh_candidates([("a",(1,2,3,4)),("b",(1,2,9,8)),("c",(7,6,5,4))],b=2,r=2)
-> {("a","b")}
```

## 解题思路与参考答案

我会分三步做：把文档拆成 shingle 集合并算 MinHash 签名，用 LSH 找出可能重复的候选对，再对候选算精确 Jaccard 决定去不去。这样省掉了全量两两比较，但总成本仍取决于候选数量，报规模时要估候选对数。

比如一篇 200 个词的文章，转载时只在末尾加了「footer copyright example」，字节级的精确哈希认不出来，Jaccard 却在 0.95 以上，这就是 MinHash 要抓的东西。要做 deduplication，是因为 Lee et al. 2021 指出，training set 里的 near-duplicates 浪费算力，也会让评测里「看起来像新文档」的内容变得眼熟，所以 deduplication 既改变模型能力，也改变评测结果的含义。另外 MinHash 不是加密哈希。

## 数学先说 20 秒

把文档 $A,B$ 看成 shingle 集合，Jaccard $J(A,B)=|A\cap B|/|A\cup B|$。在独立随机置换 $\pi$ 下，

$$
\Pr[\min\pi(A)=\min\pi(B)]=J(A,B).
$$

用 $k$ 个独立哈希得到长度 $k$ 的签名。LSH 把签名切成 $b$ 段、每段 $r$ 维，$k=br$。一对文档至少在某一个 band 上完全相同的概率是 $1-(1-J^r)^b$。我们希望这条曲线在阈值附近足够陡，所以先定目标 $J_0$（网页常取 0.8 左右），再选 $b,r$。

## 白板能跑的最小实现

```python
import hashlib
import re
from collections import defaultdict


def shingles(text, n=5):
    tokens = re.findall(r"\w+", text.lower())
    if len(tokens) < n:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


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
            piece = signature[band * r : (band + 1) * r]
            buckets[(band, piece)].add(doc_id)
    pairs = set()
    for group in buckets.values():
        ids = sorted(group)
        for i, first in enumerate(ids):
            for second in ids[i + 1 :]:
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

测试覆盖精确 Jaccard、签名一致率、LSH 候选、短文本和参数校验：

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

这份实现能跑，但离生产还差几处，写完我会马上讲。哈希这块，生产上用 $k$ 个独立的乘法哈希或预计算的 permutation seed，热路径上别跑 $k\cdot|\mathrm{shingles}|$ 次 blake2，上面这样写只是为了不依赖 numpy。复核这块，LSH 只给候选，最终用精确 Jaccard 或编辑距离判定，阈值按域、按长度分开；短文档的 $J$ 不稳定，公式和许可证要单独放白名单。

## 规模怎么报

$N=10^9$ 个文档时，签名存盘约 $N\times k\times 8$ 字节，$k=128$ 时约 1 TB。LSH 是一次 shuffle，`(band_id, band_key) → doc_id`，只在每个桶内两两比较，期望候选数远小于 $N^2$。给一个数量级就够：目标 $J=0.8$、取 $r=8$、$b=16$ 时，$J=0.8$ 的召回接近 1，$J=0.4$ 的误召回被压下去。现场用 $1-(1-J^r)^b$ 算一个点就行，不用背表。

和评测隔离也有先后：先对冻结 evaluation set 算签名，训练文档只和评测的桶比。training set 内部 deduplication 可以更激进；对评测，只要「像到不能当新题」就算命中。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert jaccard(base, reprint) > 0.95` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条 assertion 都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**MinHash 能去语义重复吗？**
不能，它近似的是词面 Jaccard。释义、翻译、改写要用 embedding nearest neighbors，成本高两个数量级，只对高价值子集做。

**为什么不先做精确哈希？**
要先做。精确哈希去的是字节级复制，很便宜；MinHash 处理的是改了空白和页脚的转载。

**阈值怎么定？**
抽 1k 对人工看，权衡被 false rejection 的正当 paraphrase 和漏掉的转载。阈值按域分别定，0.8 只是网页的起点。

**某个 band 撞上全网模板，桶爆了怎么办？**
按域分片、先剥 boilerplate、对超大桶再切一层。「版权声明」这种全网重复的模板能让一个桶进几百万文档，候选对数跟着爆炸。

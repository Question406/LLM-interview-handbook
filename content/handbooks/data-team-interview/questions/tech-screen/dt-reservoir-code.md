---
id: dt-reservoir-code
section: tech-screen
order: 9
level: S
title: CoderPad：十亿文档装不进内存，按 token 配额怎么流式抽？
quick: >-
  用加权水库 sampling：每条文档生成随机键 $k_i = u_i^{1/w_i}$，流式保留键最大的 $k$ 条，权重可以取 token
  数乘质量分。按域各维护一个水库，不用把全量装进内存。水库控制的是条数，要和 token 预算对上，超长文档要切块或限制权重；空域要报告。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Sampling
  - Streaming
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Weighted Random Sampling (Efraimidis & Spirakis)
    url: 'https://arxiv.org/abs/1012.0256'
    type: primary
  - title: Random Sampling with a Reservoir (Vitter 1985)
    url: 'https://www.cs.umd.edu/~samir/498/vitter.pdf'
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

从持续到达的文档流中维护最多 k 篇文档的加权随机样本，让 token 更多或质量更高的文档更容易入选。

### 输入与接口

实现 Doc(`doc_id`, `n_tokens`, quality) 和 Reservoir(k, rng)，提供 offer(doc) 与 docs()。`doc_id` 唯一，`n_tokens` 为非负整数，quality 为有限非负数；k 为正整数；rng 为可复现的随机数发生器。文档 sampling 权重为 max(`n_tokens`,1) × max(quality,0.000001)。

### 输出与约束

offer 更新内部样本；docs() 返回当前样本文档列表。容量限制是文档篇数，不能把 k 当作 token 预算。少于 k 篇时全部保留，空流返回空列表。结果顺序不作要求。

采用加权无放回 reservoir 的分布约定：每篇文档独立取得 U∈(0,1) 并以 `U^(1/weight)` 为优先值，保留优先值最大的 k 篇；优先值相同时按到达顺序优先。相同输入与相同 rng 初始状态必须可复现。k=1 时各文档入选概率与权重成正比。

### 示例

```text
k=5
offer(Doc("a",100,1.0))
offer(Doc("b",200,0.5))
docs() 中 doc_id 的集合 -> {"a","b"}
两篇文档权重均为100；容量未满，因此无需随机淘汰
```

## 解题思路与参考答案

$N=10^9$ 时我会换成流式的加权水库 sampling：每条文档生成一个键 $k_i = u_i^{1/w_i}$，只保留键最大的 $k$ 条，权重 $w$ 取 token 数乘质量分。扫一遍就能近似无放回 sampling，不必把全量装进内存。`dt-pipeline-talk` 和 `dt-temp-mix-code` 里那种全量放进内存再 `choices` 的写法，到这个规模撑不住。

背后的算法是这样的。无权重的水库是 Vitter 的版本，第 $i$ 条以 $k/i$ 的概率替换。有权重时用 Efraimidis 的 A-Res，每条独立抽 $u\sim U(0,1)$，键 $k_i=u^{1/w}$，保留键最大的 $k$ 条，$w$ 越大越容易进样本。举个最小的例子，$k=1$、两篇文档权重 9:1，重的那篇大约 90% 的时候胜出，测试里就验了这一条。

## A-Res：一遍扫，固定 $k$ 条

现场取 $w = n_{\text{tokens}}\times\text{quality}$，和配额 sampling 的权重是同一个形式。每个域各建一个水库，域的 $k$ 用 token 预算除以该域的平均文档长度来估。

```python
import random
from dataclasses import dataclass, field


@dataclass
class Doc:
    doc_id: str
    n_tokens: int
    quality: float


@dataclass
class Reservoir:
    """A-Res 加权水库：一遍扫描，保留键 u**(1/w) 最大的 k 条，无放回。"""

    k: int
    rng: random.Random
    heap: list = field(
        default_factory=list
    )  # (key, doc)，填满后按 key 升序，最小键在 [0]

    def __post_init__(self):
        if self.k <= 0:
            raise ValueError("k must be positive")

    def weight(self, doc):
        return max(doc.n_tokens, 1) * max(doc.quality, 1e-6)

    def offer(self, doc):
        u = self.rng.random() or 1e-16
        key = u ** (1.0 / self.weight(doc))
        if len(self.heap) < self.k:
            self.heap.append((key, doc))
            if len(self.heap) == self.k:
                self.heap.sort(key=lambda item: item[0])
            return
        if key > self.heap[0][0]:
            self.heap[0] = (key, doc)
            # 替换掉最小键后重新排序；k 小时 sort 足够，k 大时换成 heapq
            self.heap.sort(key=lambda item: item[0])

    def docs(self):
        return [doc for _, doc in self.heap]
```

测试覆盖少于 $k$、无放回、按权重的概率、空水库和参数校验：

```python
from collections import Counter

# 文档少于 k 时全部保留
reservoir = Reservoir(k=5, rng=random.Random(0))
for i in range(3):
    reservoir.offer(Doc(f"d{i}", 100, 1.0))
assert sorted(d.doc_id for d in reservoir.docs()) == ["d0", "d1", "d2"]

# 一遍扫完只保留 k 条，且无放回（不重复）
reservoir = Reservoir(k=10, rng=random.Random(0))
for i in range(1000):
    reservoir.offer(Doc(f"d{i}", 100, 1.0))
ids = [d.doc_id for d in reservoir.docs()]
assert len(ids) == 10
assert len(set(ids)) == 10

# k=1 时被选中的概率正比于权重：权重 9:1，heavy 约 90% 胜出
rng = random.Random(42)
wins = Counter()
for _ in range(5000):
    reservoir = Reservoir(k=1, rng=rng)
    reservoir.offer(Doc("light", 100, 0.1))
    reservoir.offer(Doc("heavy", 100, 0.9))
    wins[reservoir.docs()[0].doc_id] += 1
assert 0.87 < wins["heavy"] / 5000 < 0.93

# 一篇都没 offer 时水库为空，调用方要把这种空域报出来
assert Reservoir(k=3, rng=random.Random(0)).docs() == []

# k 必须为正
try:
    Reservoir(k=0, rng=random.Random(0))
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

CoderPad 里 $k$ 到几千，用 `sort` 就能过。生产实现可以用 `heapq`，键是浮点数，文档只存 id，正文二次读取。

## 和 token 配额对上

水库保证的是**条数**的期望，计费单位却是 token。平均 800 token 的域问题不大，但如果出现一份 2M token 的书，单条就可能超过预算。办法是把超长文档切块后再 offer，或者 offer 之前给 $w$ 设上限，切块的 id 写进 lineage。空域也要处理：某个水库 $k>0$，一遍扫完 `heap` 却是空的，要报出来，别静默少抽，这和 `dt-temp-mix-code` 里是同一类事故。

实际流水线通常扫两遍，第一遍只估各域的 token 总量，第二遍才抽，FineWeb 一类流水线就是先预聚合再 sampling。现场能说出这两遍，比背 A-Res 公式更有用。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert sorted(d.doc_id for d in reservoir.docs()) == ["d0", "d1", "d2"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**是有放回的吗？**
A-Res 是无放回的。同一文档别 offer 两次，exact deduplication 要在上游做完，见 `dt-exact-dedup-code`。

**质量分全是 1 呢？**
就退化成按 length bias 的普通加权水库，短模板进得少，这通常正是你想要的。

**分布式怎么做？**
每个 shard 各抽 $k$ 条并带上键，reducer 再按键取全局 top-$k$。别先把十亿行 shuffle 到一台机器上。

**一本 2M token 的书进了水库怎么办？**
单条就可能超预算。offer 之前切块，或者给 $w$ 设上限，切块 id 写进 lineage。

相关：`dt-pipeline-talk`、`dt-temp-mix-code`、`dt-exact-dedup-code`

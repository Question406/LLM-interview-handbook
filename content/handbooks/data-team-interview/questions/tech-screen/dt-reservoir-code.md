---
id: dt-reservoir-code
section: tech-screen
order: 9
level: S
title: CoderPad：十亿文档装不进内存，按 token 配额怎么流式抽？
quick: "用加权水库抽样：每条文档生成随机键 $k_i = u_i^{1/w_i}$，流式保留键最大的 $k$ 条，权重可以取 token 数乘质量分。按域各维护一个水库，不用把全量装进内存。水库控制的是条数，要和 token 预算对上，超长文档就得切块或限制权重；空域要报告。"
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
updatedAt: 2026-10-12
sources:
  - title: Weighted Random Sampling (Efraimidis & Spirakis)
    url: https://arxiv.org/abs/1012.0256
    type: primary
  - title: Random Sampling with a Reservoir (Vitter 1985)
    url: https://www.cs.umd.edu/~samir/498/vitter.pdf
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
---

$N=10^9$ 时，`dt-pipeline-talk` 和 `dt-temp-mix-code` 里那种把全量放进内存再 `choices` 的写法撑不住，要换成流式的加权水库抽样：每条文档生成一个键 $k_i = u_i^{1/w_i}$，只保留键最大的 $k$ 条，权重 $w$ 取 token 数乘质量分。这样扫一遍就能近似无放回抽样，不必把全量装进内存。空域和超长文档要另外处理。

背后的算法：无权重的水库是 Vitter 的版本，第 $i$ 条以 $k/i$ 的概率替换。有权重时用 Efraimidis 的 A-Res：每条独立抽 $u\sim U(0,1)$，键 $k_i=u^{1/w}$，保留键最大的 $k$ 条，$w$ 越大越容易进样本。

## A-Res：一遍扫，固定 $k$ 条

现场取 $w = n_{\text{tokens}}\times\text{quality}$，和配额采样的权重是同一个形式。每个域各建一个水库，域的 $k$ 用 token 预算除以该域的平均文档长度来估。

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
    heap: list = field(default_factory=list)  # (key, doc)，填满后按 key 升序，最小键在 [0]

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

### 可执行测试

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

水库保证的是**条数**的期望，计费单位却是 token。平均 800 token 的域问题不大；但如果出现一份 2M token 的书，单条就可能超过预算。办法是把超长文档切块后再 offer，或者 offer 之前给 $w$ 设上限，切块的 id 写进 lineage。

空域也要处理：某个水库 $k>0$，一遍扫完 `heap` 却是空的，要报出来，不要静默少抽。这和 `dt-temp-mix-code` 里是同一类事故。

实际流水线通常扫两遍：第一遍只估各域的 token 总量，第二遍才抽。FineWeb 一类流水线就是先预聚合再抽样。现场能说出这两遍，比背 A-Res 公式更有用。

## 追问

- **是有放回的吗？** A-Res 是无放回的。同一文档不要 offer 两次，精确去重要在上游做完，见 `dt-exact-dedup-code`。
- **质量分全是 1 呢？** 就退化成按长度偏置的普通加权水库，短模板进得少，这通常正是你想要的。
- **分布式怎么做？** 每个 shard 各抽 $k$ 条并带上键，reducer 再按键取全局 top-$k$。不要先把十亿行 shuffle 到一台机器上。

---
id: dt-reservoir-code
section: tech-screen
order: 9
level: S
title: CoderPad：十亿文档装不进内存，按 token 配额怎么流式抽？
quick: "对每条文档抽随机键 $k_i = u_i^{1/w_i}$，流式保留最大的 $k$ 个，权重可由 token 数和质量决定。按域维护水库，不装全量；条数与 token 预算并不相同，超长文档要切块或限制权重，空域要报告。"
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

加权水库对每条文档生成键 $k_i = u_i^{1/w_i}$，仅保留键最大的 $k$ 条，权重 $w$ 可用 token 数乘质量分。这样能流式近似无放回采样，不必把全量装入内存。空域和超长文档要另行处理；$N=10^9$ 时，`dt-pipeline-talk` 与 `dt-temp-mix-code` 中的内存 `choices` 示例需要换成这种大规模实现。

无权重的水库是 Vitter：第 $i$ 条以 $k/i$ 替换。有权重用 Efraimidis 的 A-Res：每条独立抽 $u\sim U(0,1)$，键 $k_i=u^{1/w}$，保留键最大的 $k$ 条。$w$ 越大越容易进样本。

## A-Res：一遍扫，固定 $k$ 条

现场 $w = n_{\text{tokens}}\times\text{quality}$，和配额采样的权重同构。按域各建一个水库，域的 $k$ 由 token 预算除以该域平均文档长度估。

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

CoderPad 里 $k$ 到几千，`sort` 能过。生产实现可用 `heapq`，键是浮点，文档只存 id，正文走二次读取。

## 和配额对上

水库保证的是**条数**期望，计费单位是 token。平均 800 token 的域还好；若出现一份 2M token 的书，单条就可能超过预算。可以：超长文档切块再 offer，或 offer 前把 $w$ cap 住，切块 id 写进 lineage。

空域：这个水库 $k>0$ 但一遍扫完 `heap` 为空，要报，不要静默少抽。和 `dt-temp-mix-code` 同一条事故。

多 pass：第一遍只估各域 token 总量，第二遍才抽。FineWeb 一类流水线就是预聚合再抽样。现场说得出两遍，比硬背 A-Res 公式有用。

## 追问

- **有放回吗？** A-Res 无放回。同一文档不要 offer 两次；精确去重要在上游做完，见 `dt-exact-dedup-code`。
- **质量分全是 1 呢？** 退化成按长度偏置的普通水库。短模板会少进，这通常是你想要的。
- **分布式怎么做？** 每个 shard 抽 $k$ 条带键，reducer 再按键取全局 top-$k$。不要先 shuffle 十亿行到一台。

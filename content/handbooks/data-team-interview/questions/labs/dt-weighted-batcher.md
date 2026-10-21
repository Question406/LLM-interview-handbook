---
id: dt-weighted-batcher
section: labs
order: 13
level: A
title: Anthropic 编程题：带权重的 DataBatcher，断点续跑怎么写？
quick: "按 token 预算组 batch，checkpoint 保存每个数据源的读取 offset 和随机数状态，恢复时从原位置继续读；只恢复随机种子，每个源会从头再读一遍。数据源耗尽时把它的概率设为零并报告，不悄悄改变配比。权重本身由上层决定，调配比就是改 `weights`。"
companies:
  - apple
tags:
  - Anthropic
  - CoderPad
  - Data Mix
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Data Batcher with Weighted Sampling (AceOffer, Anthropic reports)
    url: https://aceoffer.app/interviews/data_batcher_with_weighted_sampling
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

核心是两件事：batch 按 token 预算凑；断点续跑时保存每个源的 offset 和随机数状态，恢复后从原位置继续读。另外，某个源读完时要把它的概率打零并报出来，让配比的变化看得见，不悄悄把它的配额让给别的源。

## 为什么常见写法会错

最直接的写法是用 `random.choices` 按条采样，再在 checkpoint 里只存 RNG seed。这有两个问题。按条采样时，长文档会把 token 配额吃爆，实际 mix 和设定的权重对不上。只存 seed 的话，恢复后每个源的 iterator 会从头再读一遍，已经训过的样本被重复使用。这是 CoderPad 风格的 mix 题，和 `dt-temp-mix-code` 同一族，考点是可复现的 token 预算。

题目来源：AceOffer 记过两次（2025-10 到 2026-04）。`DataRegistry` 按名字取 iterator，iterator 接受 `offset`，后面几问依次加权重、断点和多源耗尽。

## 思路

1. registry 为每个数据集提供支持 offset 的 iterator。
2. 把权重归一化为采样概率，按 token 数累计，凑满预算就出一个 batch。
3. checkpoint 保存每个源的 offset 和随机数状态，恢复时用 `iterate(name, offset=saved)` 从原位置继续。
4. 某个源空了，概率打零并记录下来，供上层报警。

权重怎么定是上层的事。实际 mix 里，许可源、验证过的合成和 bulk 网页各是一个 iterator，权重写在 mix 卡上。AFM 2025 报告把多语比例从 8% 调到 30%，落到这里就是改 `weights`；桶内温度再套一层 `n_i**alpha`，见 `dt-temp-mix-code`。

```python
import random


class DataBatcher:
    """按权重从多个数据源抽样，凑满 batch_tokens 个 token 组成一个 batch。

    registry.iterate(name, offset) 返回从第 offset 条开始的迭代器，
    每条样本是带 "n_tokens" 字段的 dict。最后一条样本可能让 batch 略超预算。
    """

    def __init__(self, registry, names, weights, batch_tokens, rng=None):
        if len(names) != len(weights):
            raise ValueError("names and weights must have the same length")
        if any(weight < 0 for weight in weights):
            raise ValueError("weights must be non-negative")
        total_weight = sum(weights)
        if total_weight <= 0:
            raise ValueError("at least one weight must be positive")
        if batch_tokens <= 0:
            raise ValueError("batch_tokens must be positive")
        self.registry = registry
        self.names = list(names)
        self.p = [weight / total_weight for weight in weights]  # 采样概率，DoReMi 可在线改
        self.batch_tokens = batch_tokens
        self.rng = rng or random.Random(0)
        self.offsets = {name: 0 for name in self.names}
        self.exhausted = []  # 已耗尽的源，按耗尽顺序记录，供上层报警
        self.iters = {name: registry.iterate(name, offset=0) for name in self.names}

    def next_batch(self):
        batch = []
        used_tokens = 0
        while used_tokens < self.batch_tokens and sum(self.p) > 0:
            name = self.rng.choices(self.names, self.p, k=1)[0]
            try:
                sample = next(self.iters[name])
            except StopIteration:
                # 源耗尽：概率打零并记录，不悄悄把配额让给别的源
                self.p[self.names.index(name)] = 0.0
                self.exhausted.append(name)
                continue
            self.offsets[name] += 1
            batch.append(sample)
            used_tokens += sample["n_tokens"]
        return batch

    def state_dict(self):
        return {
            "offsets": dict(self.offsets),
            "p": list(self.p),
            "exhausted": list(self.exhausted),
            "rng": self.rng.getstate(),
        }

    def load_state_dict(self, state):
        """从 checkpoint 恢复：每个源从保存的 offset 继续读，而不是从头读。"""
        self.offsets = dict(state["offsets"])
        self.p = list(state["p"])
        self.exhausted = list(state["exhausted"])
        self.rng.setstate(state["rng"])
        self.iters = {
            name: self.registry.iterate(name, offset=self.offsets[name])
            for name in self.names
        }
```

### 可执行测试

```python
class ListRegistry:
    """测试桩：用内存里的 list 模拟支持 offset 的 DataRegistry。"""

    def __init__(self, data):
        self.data = data

    def iterate(self, name, offset=0):
        return iter(self.data[name][offset:])


def make_registry():
    return ListRegistry({
        "web": [{"id": f"web-{i}", "n_tokens": 10} for i in range(100)],
        "code": [{"id": f"code-{i}", "n_tokens": 10} for i in range(3)],
    })


# 每个 batch 凑满 token 预算
batcher = DataBatcher(make_registry(), ["web", "code"], [3, 1], batch_tokens=50)
first = batcher.next_batch()
assert sum(sample["n_tokens"] for sample in first) == 50

# 断点续跑：从 checkpoint 恢复后的后续 batch，与不中断时完全一致
state = batcher.state_dict()
expected = [batcher.next_batch() for _ in range(3)]
resumed = DataBatcher(make_registry(), ["web", "code"], [3, 1], batch_tokens=50)
resumed.load_state_dict(state)
assert [resumed.next_batch() for _ in range(3)] == expected

# 恢复后不会重读已经消费过的样本
seen_ids = [sample["id"] for batch in [first] + expected for sample in batch]
assert len(seen_ids) == len(set(seen_ids))

# 小源耗尽后概率打零并记录在 exhausted 里
for _ in range(10):
    batcher.next_batch()
assert batcher.exhausted == ["code"]
assert batcher.p[1] == 0.0

# 所有源都耗尽时返回空 batch，而不是死循环
tiny = DataBatcher(ListRegistry({"a": [{"n_tokens": 5}]}), ["a"], [1], batch_tokens=50)
assert len(tiny.next_batch()) == 1
assert tiny.next_batch() == []

# 权重全为零是配置错误
try:
    DataBatcher(make_registry(), ["web", "code"], [0, 0], batch_tokens=50)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

## 追问

- **packed 序列呢？** batch 按 token 凑齐之后，再按 `dt-packed-sft-code` 拼接，文档之间加 mask。Batcher 不负责交叉熵损失（CE）。
- **权重每 step 都变（DoReMi）怎么办？** 直接改 `p`，offset 继续。不要为了换权重把 iterator 重置，见 `dt-doremi-mix`。
- **多 worker 呢？** 每个源按 worker 切 shard，offset 是本 worker 内的。全局不重复靠 shard 划分，worker 之间不共享 iterator。

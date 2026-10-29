---
id: p3a-anthropic-coding-design-data-batcher
section: anthropic
order: 611
level: S
title: Anthropic：加权 DataBatcher：确定性 sampling 与断点续训
quick: >-
  我会把加权取样做成跨 batch 连续的确定性序列，batch 只负责截取其中一段。这样不会因每个 batch
  向下取整而饿死小权重源；保存调度位置和各源游标后，恢复输出就能和不中断时一致。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Anthropic · coding-design-data-batcher
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher
    type: secondary
---

## 题目描述

训练数据来自多个有限数据源。实现可循环读取、按固定整数比例混合、可保存和恢复进度的数据 batcher。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `Batcher(sources, weights)`：每个源是非空的有限列表，读完后从头循环；权重是正整数。调度周期按源的下标依次排列，每个源连续重复「权重」次。`sources` 与 `weights` 是等长非空列表。
- `next_batch(n)`：返回 `n` 个样本，`n` 可以是任意非负整数，调度位置跨 batch 保留。
- `state()`：返回 `(调度位置, 各源游标)`。
- `restore(state)`：校验后恢复状态，内部保存副本，之后修改传入的对象不影响 batcher。
- 这是确定性加权调度，不是独立随机抽样。所有源总长度和权重和都不超过 $10^4$。

### 输入输出示例

```text
batcher = Batcher([[a0, a1], [b0]], weights=[2, 1])
batcher.next_batch(2)   -> [a0, a1]
batcher.next_batch(3)   -> [b0, a0, a1]
```

调度周期是 [源 0, 源 0, 源 1]。第二个 batch 从周期第 3 位开始，先取 b0，然后源 0 已读完一轮，从 a0 重新开始。

## 解题思路与参考答案

## 题目

实现一个 DataBatcher：有多个数据源，每个源有一个权重，按权重比例从各个源取样本组成 batch。要支持从某个 offset 断点续训，而且 batch 大小不一定能整除权重和。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会让加权调度跨 batch 保持连续，避免每个 batch 各自取整。比如权重 3:1、batch 大小 2，第二个源理论上分到 0.5 个样本，如果每次都向下取整，它就永远取不到样本。

解决办法是让调度跨 batch 延续。可以把一个周期展开成序列，比如权重 [2, 1] 对应 [源 0, 源 0, 源 1]，用一个游标在序列上循环，batch 只是从当前位置往后截一段。这样无论 batch 多大，长期比例都严格等于权重比例。

断点续训要求恢复后的输出和不中断时完全一样，所以状态里要包含所有会影响后续输出的东西：调度游标、每个源各自的读取位置；如果用 random sampling，还要加上随机数生成器的状态。

动手前先问清楚：权重是严格比例（确定性调度）还是 sampling 概率（随机抽样）；源读完以后是循环、报错还是移出调度。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Batcher(sources, weights)`：每个源是非空的有限列表，读完后从头循环；权重是正整数。调度周期按源的下标依次排列，每个源连续重复「权重」次。参数不合法时抛 `ValueError`。
- `next_batch(n)`：返回 `n` 个样本，`n` 可以是任意非负整数，调度位置跨 batch 保留。
- `state()`：返回 `(调度位置, 各源游标)`。
- `restore(state)`：校验后恢复状态，内部保存副本，之后修改传入的对象不影响 batcher。
- 这是确定性加权调度，不是独立随机抽样。所有源总长度和权重和都不超过 $10^4$。

### 输入输出示例

```text
batcher = Batcher([[a0, a1], [b0]], weights=[2, 1])
batcher.next_batch(2)   -> [a0, a1]
batcher.next_batch(3)   -> [b0, a0, a1]
```

调度周期是 [源 0, 源 0, 源 1]。第二个 batch 从周期第 3 位开始，先取 b0，然后源 0 已读完一轮，从 a0 重新开始。

### 解题思路与正确性

输出序列完全由「调度位置」和「各源游标」决定：每取一个样本，从调度序列读出源编号，从该源的游标处取样本，然后两个游标各加一并取模。由于调度位置不在 batch boundaries 重置，分几次取和一次取完得到的是同一个序列，权重小的源在每个周期里都会出现。

恢复时把这两部分状态原样设回，后续的每一步都和不中断运行时一致。

### 完整参考实现（Python 3）

```python
class Batcher:
    """按权重确定性地轮流从多个数据源取样本，调度位置跨 batch 保留，可保存和恢复状态。"""

    def __init__(self, sources, weights):
        if not sources or len(sources) != len(weights):
            raise ValueError("need one weight per source and at least one source")
        if any(not source for source in sources):
            raise ValueError("every source must be non-empty")
        if any(type(weight) is not int or weight < 1 for weight in weights):
            raise ValueError("weights must be positive ints")
        self.sources = [list(source) for source in sources]
        # 一个调度周期：源 0 连续 weights[0] 次，源 1 连续 weights[1] 次……
        self.schedule = [
            index for index, weight in enumerate(weights) for _ in range(weight)
        ]
        self.pos = 0  # 在调度周期里的位置
        self.offsets = [0] * len(sources)  # 每个源下一个要读的下标

    def next_batch(self, n):
        """取 n 个样本。n 不必整除权重和，周期位置会延续到下一个 batch。"""
        if n < 0:
            raise ValueError(f"batch size must be non-negative, got {n}")
        batch = []
        for _ in range(n):
            index = self.schedule[self.pos]
            source = self.sources[index]
            batch.append(source[self.offsets[index]])
            self.offsets[index] = (self.offsets[index] + 1) % len(
                source
            )  # 源读完后从头循环
            self.pos = (self.pos + 1) % len(self.schedule)
        return batch

    def state(self):
        return self.pos, tuple(self.offsets)

    def restore(self, state):
        """恢复到 state()，之后的输出与不中断运行完全一致。"""
        pos, offsets = state
        if not 0 <= pos < len(self.schedule):
            raise ValueError(f"schedule position out of range: {pos}")
        if len(offsets) != len(self.sources):
            raise ValueError("need one offset per source")
        if any(
            not 0 <= offset < len(source)
            for offset, source in zip(offsets, self.sources)
        ):
            raise ValueError(f"source offset out of range: {offsets}")
        self.pos = pos
        self.offsets = list(offsets)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert batcher.next_batch(2) == ["a0", "a1"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def make():
    return Batcher([["a0", "a1"], ["b0"]], [2, 1])


# 按 2:1 的周期取数
batcher = make()
assert batcher.next_batch(2) == ["a0", "a1"]

# 保存状态后继续取，再恢复，应得到同样的输出
saved = batcher.state()
expected = batcher.next_batch(7)
batcher.restore(saved)
assert batcher.next_batch(7) == expected

# batch 大小不整除权重和：分两次取和一次取完结果相同，小权重源不会被饿死
batcher = make()
assert batcher.next_batch(2) + batcher.next_batch(3) == make().next_batch(5)
assert make().next_batch(3) == ["a0", "a1", "b0"]

# 非法状态
try:
    make().restore((3, (0, 0)))
except ValueError:
    pass
else:
    raise AssertionError("out-of-range state should raise ValueError")
```

### 复杂度与追问

设源的总长度为 $L$、权重和为 $W$、源个数为 $m$。构造是 $O(L + W)$，取 $n$ 个样本是 $O(n)$，状态大小是 $O(m)$。

- 权重很大（比如 1000:1）怎么办？展开的调度序列会很长。可以只存权重前缀和，用二分查找周期位置对应的源，空间降到 $O(m)$。另外，连续 1000 个都来自同一个源，局部混合不均匀，可以改用平滑加权轮询（smooth weighted round-robin）让各个源交错出现。
- 换成 random sampling 怎么办？状态里还要保存随机数生成器的状态和 sampling 算法的版本，否则代码升级后同一个种子也会产生不同的序列。
- 多机训练怎么办？每个 worker 要能根据全局样本编号推出自己该读的位置，恢复时所有 worker 从同一个全局步数开始。

---
id: p3a-perplexity-stream-sampling-and-distribution-verification
section: design
order: 606
level: A
title: Perplexity：Reservoir Sampling 与分布验证
quick: >-
  用 reservoir sampling：先放前 k 项，第 i 项以 k/i 概率入池，均匀替换一个槽位，一遍扫描只需 O(k)
  空间。均匀性用归纳法证明，分布验证则重复抽样，比较入选频率与理论概率。
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Perplexity · stream-sampling-and-distribution-verification
    url: >-
      https://www.1point3acres.com/interview/problems/company/perplexity/stream-sampling-and-distribution-verification
    type: secondary
---

## 题目描述

实现对未知长度流的固定容量均匀抽样，并通过重复实验检查样本分布。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `reservoir(stream, k, rng) -> list`：对未知长度的流扫描一遍，用 O(k) 空间均匀无放回地抽出 $\min(k, N)$ 项。`rng` 提供 `randrange`，`k` 为非负整数。
- 输出顺序不要求和原流一致；流的长度不超过 k 时返回全部元素。
- 流最多 $10^{6}$ 个元素。测试部分要用重复试验验证每个元素的入选概率约为 $k/N$。

### 输入输出示例

```text
reservoir(range(3), k=5, rng) -> [0, 1, 2]
reservoir(range(10), k=0, rng) -> []
reservoir(range(10), k=3, rng) 的一个可能结果 -> [7, 1, 4]
最后一个结果只是可能样本；每个元素被选中的理论概率均为 3/10。
```

## 解题思路与参考答案

## 题目

数据流长度未知，只能扫描一遍，要在 O(k) 空间里均匀地无放回抽出 k 个元素（reservoir sampling）。写完之后还要说明怎么验证抽样结果确实近似均匀。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会用 reservoir sampling，先把前 k 项放进池，之后第 i 项（从 1 开始）以 $k/i$ 概率入池，并均匀替换一个槽位。一次 `randrange(i)` 就能同时决定是否入池和替换位置：结果小于 k 就替换那个槽位。

证明时用归纳说明，处理完前 i 项后，每项留在池中的概率都是 $k/i$。验证实现时则重复很多次抽样，统计各项入选频率，与 $k/N$ 比较，容忍度按二项分布标准差确定；需要更严格时可以做卡方检验。固定种子只能让测试复现，一次结果本身说明不了分布。

还要先约定短流、输出顺序和重复值的语义。这份练习流比 k 短就全部返回，不要求保持顺序，重复值按位置抽样。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `reservoir(stream, k, rng) -> list`：对未知长度的流扫描一遍，用 O(k) 空间均匀无放回地抽出 $\min(k, N)$ 项。`rng` 提供 `randrange`，`k < 0` 抛 `ValueError`。
- 输出顺序不要求和原流一致；流的长度不超过 k 时返回全部元素。
- 流最多 $10^{6}$ 个元素。测试部分要用重复试验验证每个元素的入选概率约为 $k/N$。

### 输入输出示例

```text
reservoir(range(3), 5, rng)    -> [0, 1, 2]
reservoir(range(10), 0, rng)   -> []
reservoir(range(10), 3, rng)   -> 例如 [7, 1, 4]；重复 10000 次，每个数的入选频率约 0.3
```

### 解题思路与正确性

归纳：前 k 步每个元素都在池里，概率是 1。假设处理完前 i 个元素时每个都以 $k/i$ 的概率在池里。第 i+1 个元素以 $k/(i+1)$ 的概率进入；旧元素只有在新元素进入并恰好替换它时才会被挤掉，概率是 $\frac{k}{i+1} \cdot \frac{1}{k} = \frac{1}{i+1}$。所以旧元素继续留下的概率是 $\frac{k}{i} \cdot \frac{i}{i+1} = \frac{k}{i+1}$，和新元素一样。

测试里 10000 次试验、理论概率 0.3 时，频率的标准差约为 0.0046，容忍 0.025 大约是 5 倍标准差，种子固定后结果稳定。统计测试只能发现明显偏差，证明还是靠上面的归纳。

### 完整参考实现（Python 3）

```python
def reservoir(stream, k, rng):
    """一遍扫描未知长度的流，O(k) 空间均匀无放回抽取 min(k, N) 项。

    rng 需提供 randrange；返回顺序不保证是原顺序。
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    sample = []
    for index, item in enumerate(stream):
        if index < k:
            sample.append(item)
        elif k > 0:
            # 第 index + 1 个元素以 k / (index + 1) 的概率进入，进入时均匀替换一个槽位
            slot = rng.randrange(index + 1)
            if slot < k:
                sample[slot] = item
    return sample
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert reservoir(range(3), 5, random.Random(1)) == [0, 1, 2]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
import random

# 流比 k 短时全部返回；k = 0 时为空
assert reservoir(range(3), 5, random.Random(1)) == [0, 1, 2]
assert reservoir(range(10), 0, random.Random(1)) == []
assert reservoir(iter([]), 3, random.Random(1)) == []

# 重复试验：每个元素的入选频率应接近 k / N = 0.3，且一次抽样内不重复
trials = 10000
counts = [0] * 10
rng = random.Random(3)
for _ in range(trials):
    picks = reservoir(range(10), 3, rng)
    assert len(picks) == 3
    assert len(set(picks)) == 3
    for item in picks:
        counts[item] += 1
# 0.025 约为二项分布标准差 sqrt(0.3 * 0.7 / 10000) ≈ 0.0046 的 5 倍
assert all(abs(count / trials - 0.3) < 0.025 for count in counts)

try:
    reservoir(range(3), -1, random.Random(1))
except ValueError:
    pass
else:
    raise AssertionError("negative k should raise ValueError")
```

### 复杂度与追问

设流长为 N。时间 O(N)，每个元素最多一次随机数调用；空间 O(min(k, N))。

- 流里有重复值：这份实现按位置抽样，返回的值可能重复。如果要按不同的值均匀抽，就得先知道哪些值出现过，空间不再是 O(k)。
- 流很长、随机数调用成为瓶颈：可以用 Algorithm L，直接按几何分布算出下一个会被选中的位置，跳过中间的元素，期望只调用 O(k log(N/k)) 次随机数。
- 带权抽样：给每个元素算 $u^{1/w}$（$u$ 为 0 到 1 的均匀随机数，$w$ 为权重），保留最大的 k 个（A-Res 算法），用一个大小为 k 的堆实现。

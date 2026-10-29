---
id: p3a-anthropic-coding-q4-distributed-mode-median
section: anthropic
order: 606
level: A
title: Anthropic：分布式众数与中位数：低带宽通信
quick: >-
  众数要汇总每个值的计数，本地众数投票会漏掉全局最多的值。中位数可以在值域上二分，每轮让各 worker 只报不超过 mid
  的元素个数，用更多轮扫描和通信换取更少传输量。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Anthropic · coding-q4-distributed-mode-median
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q4-distributed-mode-median
    type: secondary
---

## 题目描述

在多个工作者保存数据分片的条件下，求全体数据的众数和中位数，并报告中位数查询的通信轮数。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`distributed_stats(shards)` 返回 `(mode, median, rounds)`。shards 是整数列表的列表，可以含空分片；总元素数为 1 到 100000，值在 `[-10^9,10^9]`。众数为全局出现次数最多的值，并列时选较小值。中位数是排序后中间值；总数为偶数时取中间两个值的平均，返回浮点数。

协调者不能直接收集所有原始元素。众数部分可传递各分片的值频次；中位数部分通过向各工作者询问“不大于给定阈值的元素个数”获得信息，rounds 记录此类全局阈值查询的次数。

### 示例

```text
shards = [[1,1,9],[2,2,2]]
mode = 2, median = 2.0
shards = [[1,4],[2,3]] 时 median = 2.5。
rounds 为实现实际执行的阈值查询轮数。
```

## 解题思路与参考答案

## 题目

数据分散在多个 worker 上，每个 worker 只持有自己的分片。在读取速度和节点间带宽都受限的条件下，求全局的众数和中位数。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

众数要按值聚合完整计数，中位数则可以反复查询计数来二分值域。比如分片 `[1, 1, 2]`、`[3, 3, 2]`、`[4, 4, 2]` 的本地众数是 1、3、4，全局众数却是 2，投票本地众数就会漏掉它。数据量大时可以按值哈希分区，让同一个值的计数汇总到同一个节点，各节点算出局部最优后再比较。

中位数不需要传原始数据。先让每个 worker 报告本地的最小值和最大值，得到全局值域；然后在值域上二分：coordinator 广播一个 `mid`，每个 worker 只回传本地 $\le$ `mid` 的元素个数，合计后就知道全局第 $k$ 小在 `mid` 左边还是右边。每轮每个 worker 只传一个整数，代价是要通信 $O(\log \text{值域})$ 轮，每轮各 worker 还要重新扫描本地数据。

面试中值得先确认：数据是不是整数、取值范围多大、重复值多不多；带宽和读取速度哪个更紧张。然后量化每轮读多少、传多少，判断多扫几轮换更少传输是否划算。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `distributed_stats(shards) -> (mode, median, rounds)`：`shards` 是整数列表的列表，每个列表代表一个 worker 的本地数据。
- 众数：每个 worker 生成本地 `Counter` 发给 coordinator 合并，返回全局众数，并列时取较小的值。
- 中位数：先用本地 min/max/个数确定全局值域和总数，再多轮请求各 worker 返回本地 $\le$ `mid` 的个数，不传原始数组。总数为偶数时取中间两个值的平均。`rounds` 是计数查询的轮数。
- 全局没有数据时抛 `ValueError`。总数 $N \le 10^5$，整数范围 $[-10^9, 10^9]$。
- 题卡里的带宽限制（如 1 B/s）只用于复杂度分析，这里不模拟真实时延。

### 输入输出示例

```text
distributed_stats([[1, 1, 9], [2, 2, 2]])[:2]  -> (2, 2.0)
distributed_stats([[], [7, 7]])[:2]            -> (7, 7.0)
distributed_stats([[1, 4], [2, 3]])[1]         -> 2.5
```

### 解题思路与正确性

众数直接在合并后的完整计数上取最大值，和单机结果一定相同。

求第 $k$ 小时，谓词「全局 $\le x$ 的个数 $\ge k$」随 $x$ 单调：$x$ 越大越容易成立。二分找到使它成立的最小 $x$，这个 $x$ 一定是数据中真实存在的值，也就是第 $k$ 小；有重复值时计数会一次跳过好几个，结论不变。总数为偶数时分别求第 $n/2$ 和第 $n/2 + 1$ 小再取平均。

测试用随机数据和 `statistics.median`、单机 `Counter` 对照。

### 完整参考实现（Python 3）

```python
from collections import Counter


def mode_of(counts):
    """出现次数最多的值；并列时取较小的值。"""
    return min(counts, key=lambda value: (-counts[value], value))


def count_at_most(local, threshold):
    """worker 端：只回传本地 <= threshold 的元素个数，不传原始数据。"""
    return sum(1 for value in local if value <= threshold)


def distributed_stats(shards):
    """shards 是各 worker 的本地整数列表。返回 (众数, 中位数, 计数查询轮数)。"""
    total_count = sum(len(local) for local in shards)
    if total_count == 0:
        raise ValueError("no data on any worker")

    # 众数：每个 worker 发完整的本地计数，由 coordinator 合并；只发本地众数会出错
    merged = Counter()
    for local in shards:
        merged.update(Counter(local))
    mode = mode_of(merged)

    # 中位数：先用各 worker 的 min/max 得到全局值域，再在值域上二分
    low = min(min(local) for local in shards if local)
    high = max(max(local) for local in shards if local)
    rounds = 0

    def kth_smallest(k):
        """全局第 k 小（从 1 开始）：最小的 x 使得全局 <= x 的个数 >= k。"""
        nonlocal rounds
        left, right = low, high
        while left < right:
            mid = (left + right) // 2
            rounds += 1
            # 每一轮 coordinator 只从每个 worker 收到一个计数
            count = sum(count_at_most(local, mid) for local in shards)
            if count >= k:
                right = mid
            else:
                left = mid + 1
        return left

    if total_count % 2:
        median = kth_smallest((total_count + 1) // 2)
    else:
        half = total_count // 2
        median = (kth_smallest(half) + kth_smallest(half + 1)) / 2
    return mode, median, rounds
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert distributed_stats([[1, 1, 9], [2, 2, 2]])[:2] == (2, 2.0)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
import random
import statistics

# 每个分片的本地众数是 1 和 2，全局众数是 2
assert distributed_stats([[1, 1, 9], [2, 2, 2]])[:2] == (2, 2.0)

# 空分片
assert distributed_stats([[], [7, 7]])[:2] == (7, 7.0)

# 偶数个元素取中间两个的平均
assert distributed_stats([[1, 4], [2, 3]])[1] == 2.5

# 全局为空
try:
    distributed_stats([[], []])
except ValueError:
    pass
else:
    raise AssertionError("empty input should raise ValueError")

# 和单机 statistics.median、Counter 随机对照
rng = random.Random(4)
for _ in range(100):
    values = [rng.randrange(-20, 20) for _ in range(21)]
    mode, median, _ = distributed_stats([values[:7], values[7:]])
    assert median == statistics.median(values)
    assert mode == mode_of(Counter(values))
```

### 复杂度与追问

设总数为 $N$、worker 数为 $W$、值域宽度为 $R$。

- 众数的通信量是各分片不同值个数之和，最坏是 $O(N)$ 条 (值, 计数)，在极低带宽下并不高效。如果只要近似众数，可以用 Count-Min Sketch 或 Misra-Gries 这类摘要，传输量固定。
- 中位数需要 $O(\log R)$ 轮，每轮通信 $W$ 个计数；参考实现每轮都扫描本地数据，总计算量 $O(N \log R)$。如果 worker 先把本地数据排好序，每轮的本地计数可以用二分在 $O(\log n_i)$ 内完成。
- 估算真实带宽成本时，要按编码后的字节数和网络往返轮次一起算，轮数多的方案在高延迟网络上可能反而更慢。

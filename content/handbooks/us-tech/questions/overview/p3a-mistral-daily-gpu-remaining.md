---
id: p3a-mistral-daily-gpu-remaining
section: overview
order: 800
level: A
title: Mistral：每日 GPU 余量统计
quick: '每天从满容量复制一份，再按 (day, cluster) 扣掉乱序记录里的用量，输出第 0 天到最大日的余量矩阵；前一天的余量不结转。'
companies:
  - mistral
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - mistral
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Mistral：每日 GPU 余量统计
    url: >-
      https://www.1point3acres.com/interview/problems/d17c9b3f-c87d-4976-b339-e901cdb6f076
    type: secondary
---

## 题目描述

计算各集群每日剩余 GPU，并比较自由切换与限制切换次数时的最大可用总量。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`remaining(capacity,usages)` 中 capacity 是 C 个集群每日容量，usages 是无序 `(day,cluster,count)` 列表，同日同集群用量相加。返回从第 0 天到最大 day 的 `[D,C]` 剩余量，缺失天按满容量处理，每天容量重新开始；空 usages 返回空列表。

`unlimited(remain)` 返回每天选一个集群、允许任意切换时的最大总剩余量。`limited(remain,k)` 返回相邻两天所选集群最多变化 k 次时的最大总量。容量、用量非负且不超配，D<=200、C<=50，k>=0。空日程的总量为 0。

### 示例

```text
capacity=[10,20], usages=[(1,0,3),(0,0,5),(0,1,13)]
remaining=[[5,7],[7,20]]；unlimited=27；limited(k=0)=27。
remain=[[9,1],[1,9],[9,1]]：limited(k=1)=19，limited(k=2)=27。
```

## 解题思路与参考答案

## 题目

给定每个集群每天的 GPU 容量，以及一批 `(day, cluster, gpus)` 使用记录，算出每一天每个集群还剩多少 GPU。每天容量从满额重新开始，使用记录可能乱序。

> 来源：一亩三分地 Mistral 题目详情（2026-10-18 读取），题面由网站从面经整理，网站收录也不等于公司官方确认。下面的接口、约束和测试是手册补的练习约定；这份练习把余量统计、无限切换和最多 K 次切换三问串成同一组接口。

## 思路

我会给每一天单独复制一份容量，再按记录里的 day 和 cluster 扣用量。比如前一天还有余量，也不带到第二天，因为每天重新从满容量开始；所以记录乱序不影响结果。同一天同一集群的多条用量要累计检查，超过容量就按练习约定报错。

动手前值得和面试官确认几件事：

- 输出覆盖哪些天。这份练习约定从第 0 天到出现过的最大 day，中间没有记录的日子按满容量输出。
- `usages` 为空时返回什么。这时没有「最大日」，练习约定返回 `[]`。
- 用量超过容量是报错还是截到 0。这里选择报错。

相关题：[[p3a-mistral-gpu-unlimited-switches]]（在这张余量矩阵上无限切换，求最大总量）、[[p3a-mistral-gpu-k-switches]]（最多 K 次切换，需要 DP）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `remaining(capacity, usages) -> list[list[int]]`：`capacity[c]` 是集群 c 每天的 GPU 容量，`usages` 是可以乱序的 `(day, cluster, gpus)` 记录。每天从满容量开始扣，返回第 0 天到最大 day 的余量矩阵；`usages` 为空时返回 `[]`。
- `unlimited(remain) -> int`：每天选一个集群、拿到它当天的余量，切换次数不限，返回总和的最大值。
- `limited(remain, k) -> int`：同样每天选一个集群，相邻两天选的集群不同记一次切换，最多 `k` 次。
- 容量和用量都非负；某天某集群的累计用量超过容量时抛 `ValueError`。规模 $D \le 200$ 天、$C \le 50$ 个集群、$k \ge 0$。

### 输入输出示例

```text
remaining([10, 20], [(1, 0, 3), (0, 0, 5), (0, 1, 13)])  -> [[5, 7], [7, 20]]
unlimited([[5, 7], [7, 20]])                             -> 27
limited([[5, 7], [7, 20]], 0)                            -> 27
limited([[9, 1], [1, 9], [9, 1]], 1)                     -> 19
limited([[9, 1], [1, 9], [9, 1]], 2)                     -> 27
```

第一个例子里两天都选集群 1（7 + 20）就是最优，不需要切换。第二个矩阵每天的最大值在两个集群之间交替，切换次数越多拿得越多。

### 解题思路与正确性

`remaining` 给每天复制一份容量，再逐条扣用量。每天的数据互不影响，所以记录顺序无关紧要，前一天的余量也不会带到第二天。用量非负，扣的过程中一旦出现负数，就说明这一天已经超额。

`unlimited` 里天与天之间没有任何约束，每天取行最大值，加起来就是全局最优。

`limited` 用 DP。`best[used][c]` 表示处理到当前这天、用了 `used` 次切换、当天停在集群 c 的最大总和。转移有两种：昨天也在 c，切换数不变；昨天在别的集群，切换数加一。两者取大，再加上今天的 `remain[day][c]`。第一天随便选，不算切换。状态把 0 到 k 的每个切换次数都单独记了，所以答案取最后一天所有状态的最大值，正好对应「最多 k 次」。D 天最多切 D−1 次，代码先把 k 截到 D−1，避免开无用的层。

### 完整参考实现（Python 3）

```python
def remaining(capacity, usages):
    """返回 remain[day][cluster]：每天从 capacity 重新开始，扣掉当天在该集群的用量。

    usages 是 (day, cluster, gpus) 三元组，可以乱序；输出覆盖第 0 天到最大的 day，
    没有记录的日子就是满容量。usages 为空时返回 []。
    """
    if not capacity or any(gpus < 0 for gpus in capacity):
        raise ValueError("capacity must be non-empty and non-negative")
    if not usages:
        return []
    for day, cluster, gpus in usages:
        if day < 0 or not 0 <= cluster < len(capacity) or gpus < 0:
            raise ValueError(f"invalid usage: {(day, cluster, gpus)!r}")

    last_day = max(day for day, _, _ in usages)
    remain = [list(capacity) for _ in range(last_day + 1)]  # 每天独立复制，余量不结转
    for day, cluster, gpus in usages:
        remain[day][cluster] -= gpus
        if remain[day][cluster] < 0:
            raise ValueError(f"day {day} cluster {cluster} is over capacity")
    return remain


def unlimited(remain):
    """切换次数不限：各天互不约束，每天取最大的那个集群。"""
    return sum(max(row) for row in remain)


def limited(remain, k):
    """每天选一个集群，相邻两天集群不同算一次切换，最多 k 次，返回最大总余量。"""
    if k < 0:
        raise ValueError("k must be non-negative")
    if not remain:
        return 0
    clusters = len(remain[0])
    if clusters == 0 or any(len(row) != clusters for row in remain):
        raise ValueError("remain must be a non-empty rectangular matrix")

    k = min(k, len(remain) - 1)  # D 天最多只能切换 D - 1 次
    neg_inf = float("-inf")
    # best[used][cluster]：到当前这天为止用了 used 次切换、当天停在 cluster 的最大总和
    best = [[neg_inf] * clusters for _ in range(k + 1)]
    best[0] = list(remain[0])  # 第一天的选择不算切换
    for row in remain[1:]:
        nxt = [[neg_inf] * clusters for _ in range(k + 1)]
        for used in range(k + 1):
            for dest in range(clusters):
                stay = best[used][dest]
                switch = neg_inf
                if used > 0:
                    switch = max(
                        (best[used - 1][src] for src in range(clusters) if src != dest),
                        default=neg_inf,
                    )
                nxt[used][dest] = max(stay, switch) + row[dest]
        best = nxt
    return max(max(layer) for layer in best)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert remain_matrix == [[5, 7], [7, 20]]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
import itertools
import random


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


def brute_force(remain, k):
    """枚举每天的集群选择，只保留切换次数不超过 k 的路径。"""
    totals = []
    for path in itertools.product(range(len(remain[0])), repeat=len(remain)):
        switches = sum(prev != cur for prev, cur in zip(path, path[1:]))
        if switches <= k:
            totals.append(sum(remain[day][cluster] for day, cluster in enumerate(path)))
    return max(totals)


# 乱序记录；每天容量重置，不把前一天的余量带过去
remain_matrix = remaining([10, 20], [(1, 0, 3), (0, 0, 5), (0, 1, 13)])
assert remain_matrix == [[5, 7], [7, 20]]
assert unlimited(remain_matrix) == 27
assert limited(remain_matrix, 0) == 27

# 中间没有记录的日子是满容量；同一天同集群的多条记录累加
assert remaining([4, 4], [(2, 1, 1), (2, 1, 2)]) == [[4, 4], [4, 4], [4, 1]]
assert remaining([4], []) == []

# 非法输入
expect_value_error(remaining, [5], [(0, 0, 3), (0, 0, 3)])  # 当天累计超额
expect_value_error(remaining, [5], [(0, 1, 1)])  # 集群越界
expect_value_error(remaining, [], [])  # 空容量
expect_value_error(limited, [[1]], -1)
expect_value_error(limited, [[1, 2], [3]], 1)  # 不是矩形

# 与暴力枚举对拍：交错的矩阵每多一次切换都能多拿分
zigzag = [[9, 1], [1, 9], [9, 1]]
for k in range(3):
    assert limited(zigzag, k) == brute_force(zigzag, k)
assert limited(zigzag, 10) == unlimited(zigzag) == 27

# 随机小矩阵对拍
rng = random.Random(0)
for _ in range(50):
    days, clusters = rng.randint(1, 4), rng.randint(1, 3)
    matrix = [[rng.randint(0, 9) for _ in range(clusters)] for _ in range(days)]
    for k in range(days + 1):
        assert limited(matrix, k) == brute_force(matrix, k)
```

### 复杂度与追问

设天数为 D、集群数为 C、记录数为 U。`remaining` 是 O(DC + U)，`unlimited` 是 O(DC)。`limited` 的每个状态都要扫一遍其他集群，时间 O($DKC^{2}$)；滚动数组只保留上一天那一层，空间 O(KC)。

**能不能降到 O(DKC)？**
可以。对上一层的每个 `used`，先算出最大值、它所在的集群和次大值。转移到 dest 时，如果最大值正好来自 dest，就用次大值，否则用最大值。次大值要定义成「去掉最大值所在下标之后的最大值」，这样最大值并列时次大值也等于它，不会误把另一个同样大的集群排除掉。
**如果每次切换扣固定代价呢？**
状态里就不需要 `used` 这一维，切换转移时减去代价即可，配合最大/次大值是 O(DC)。

---
id: p3a-openai-shard-rebalance
section: openai
order: 618
level: A
title: "OpenAI：分片区间重平衡：覆盖与重叠上限"
quick: "用所有端点把目标范围切成基本段，逐段看覆盖数：为 0 就补一个 owner，超过 limit 就删掉多余的，其余保留；在 shard 可任意切分的成本模型下，这样逐段达到下界就是全局最优。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · shard-rebalance"
    url: https://www.1point3acres.com/interview/problems/company/openai/shard-rebalance
    type: secondary
---

## 题目

一组 shard 各自负责 key 空间上的一段区间，区间之间可能重叠，也可能留有空洞。要求支持增删 shard，并做一次重平衡：目标范围内每个点被覆盖的次数不超过 limit，空洞要补上，同时尽量少迁移数据。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束、成本定义和测试是手册补的练习约定，不是原题。

## 思路

先把所有 shard 的端点排序，把目标范围切成若干基本段。在一个基本段内，覆盖它的 shard 集合不会变化，所以可以逐段独立处理：

- 覆盖数为 0：这是空洞，必须新增一个 owner；
- 覆盖数超过 limit：必须删掉多出来的 owner；
- 覆盖数在 1 到 limit 之间：全部保留，不需要任何迁移。

「最少迁移」要先和面试官把成本定义清楚：按 key 区间长度算、按数据字节数算，还是按变动的 shard 个数算，答案会不一样。也要确认 shard 能不能被任意切分。这份练习选了最简单的模型：shard 可以任意切分，成本是新增和删除的 owner 数乘以区间长度。先给出一个能验证的方案，再讨论更真实的成本模型。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `rebalance(shards, lo, hi, limit) -> tuple[list, int]`：`shards` 是 `(id, start, end)` 的列表，区间半开，`id` 唯一。返回 `(segments, cost)`：`segments` 是按位置排列的基本段 `(start, end, owners)`，使 `[lo, hi)` 上每个基本段都有 1 到 `limit` 个 owner；`cost` 是最小迁移成本。
- 空洞用新 owner `"__fill__"` 补上（这个 id 是保留名，输入里不能出现）；超额时保留字典序最小的 `limit` 个 owner。目标范围之外的部分忽略。
- 成本只计「新增或删除一个 owner 在某段上的成员关系」乘以段长，保留原 owner 不计成本。不考虑合并后的段数、节点容量或复制带宽。
- `lo < hi`、`limit >= 1`、每个 shard 的区间非空，否则抛 `ValueError`。shard 数不超过 1000。

### 输入输出示例

```text
rebalance([("a", 0, 5), ("b", 3, 8)], lo=0, hi=10, limit=1)
  -> segments = [(0, 3, ("a",)), (3, 5, ("a",)), (5, 8, ("b",)), (8, 10, ("__fill__",))]
     cost = 4
```

`[3, 5)` 被 a、b 同时覆盖，删掉 b，成本 2；`[8, 10)` 没有覆盖，补一个，成本 2。

### 解题思路与正确性

成本的下界是逐段的：覆盖数为 q 的段，若 $q > \text{limit}$，至少删 $q - \text{limit}$ 个；若 $q = 0$，至少加 1 个；否则可以是 0。因为 shard 可以任意切分，各段的决定互不影响，参考实现在每一段都恰好达到这个下界，所以总成本是全局最小的。

### 完整参考实现（Python 3）

```python
FILL = "__fill__"  # 补洞时使用的新 owner，保留名


def _check_inputs(shards, lo, hi, limit):
    if lo >= hi:
        raise ValueError(f"empty target range [{lo}, {hi})")
    if limit < 1:
        raise ValueError(f"limit must be >= 1, got {limit}")
    ids = [shard_id for shard_id, _, _ in shards]
    if len(set(ids)) != len(ids):
        raise ValueError("shard ids must be unique")
    if FILL in ids:
        raise ValueError(f"{FILL!r} is reserved")
    for shard_id, start, end in shards:
        if start >= end:
            raise ValueError(f"shard {shard_id!r} has empty range [{start}, {end})")


def rebalance(shards, lo, hi, limit):
    """让 [lo, hi) 上每一点被 1 到 limit 个 shard 覆盖，迁移成本最小。

    shards 是 (id, start, end) 的半开区间列表。返回 (基本段列表, 总成本)，
    每个基本段是 (start, end, owners)；成本是新增和删除的「owner × 长度」之和。
    """
    _check_inputs(shards, lo, hi, limit)

    # 覆盖集合只会在端点处变化，用端点把 [lo, hi) 切成基本段
    cuts = {lo, hi}
    for _, start, end in shards:
        for point in (start, end):
            if lo < point < hi:
                cuts.add(point)
    cuts = sorted(cuts)

    segments = []
    cost = 0
    for seg_start, seg_end in zip(cuts, cuts[1:]):
        owners = sorted(
            shard_id for shard_id, start, end in shards
            if start <= seg_start and seg_end <= end
        )
        length = seg_end - seg_start
        if not owners:
            # 缺口：至少新增一个 owner
            segments.append((seg_start, seg_end, (FILL,)))
            cost += length
        else:
            # 超额：保留字典序前 limit 个，删掉其余的
            segments.append((seg_start, seg_end, tuple(owners[:limit])))
            cost += length * max(0, len(owners) - limit)
    return segments, cost
```

### 可执行测试

```python
def expect_value_error(*args):
    try:
        rebalance(*args)
    except ValueError:
        return
    raise AssertionError(f"rebalance{args} should raise ValueError")

# [3, 5) 重叠删一个（成本 2），[8, 10) 缺口补一个（成本 2）
segments, cost = rebalance([("a", 0, 5), ("b", 3, 8)], 0, 10, 1)
assert cost == 4
assert segments == [
    (0, 3, ("a",)),
    (3, 5, ("a",)),
    (5, 8, ("b",)),
    (8, 10, (FILL,)),
]

# 没有任何 shard：整段补洞
assert rebalance([], 0, 3, 2) == ([(0, 3, (FILL,))], 3)

# limit 足够大时什么都不用动；目标范围外的部分忽略
assert rebalance([("a", -5, 5), ("b", 0, 9)], 0, 5, 2) == ([(0, 5, ("a", "b"))], 0)

# 非法输入
expect_value_error([("a", 0, 1), ("a", 1, 2)], 0, 2, 1)
expect_value_error([("a", 2, 2)], 0, 3, 1)
expect_value_error([(FILL, 0, 1)], 0, 1, 1)
expect_value_error([], 3, 3, 1)
expect_value_error([], 0, 3, 0)
```

### 复杂度与追问

设 shard 数为 N。基本段最多 2N + 1 个，每段扫描全部 shard 并给 owner 排序，最坏 O($N^2 \log N$) 时间；输出里每段最多 `limit` 个 owner。用扫描线维护「当前覆盖集合」可以避免每段重扫全部 shard。

- 如果原 shard 不能被切开，或者每个节点有容量上限，各段的选择就互相关联了，逐段最优不再等于全局最优，需要换成别的优化模型（例如整数规划或带容量的匹配）。
- 实际系统里通常还希望结果段数少、相邻段尽量由同一个 owner 负责，这需要在成本里加入段数或碎片化惩罚。

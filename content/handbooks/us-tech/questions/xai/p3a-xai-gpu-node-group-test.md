---
id: p3a-xai-gpu-node-group-test
section: xai
order: 613
level: A
title: "xAI：GPU 节点组测：识别坏节点与并行调度"
quick: "我会先测出一对好节点，再用其中一个作搭档逐个判断其他节点。所有二人组都失败时，好节点不足两个，测试无法区分「全坏」和「只有一个好」，返回 None；要缩短轮数，可以让多个已知好节点各带一个待测节点并行。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · gpu-node-group-test"
    url: https://www.1point3acres.com/interview/problems/company/xai/gpu-node-group-test
    type: secondary
---

## 题目描述

给定 n 个 GPU 节点和一个只能测试至少两个节点的 oracle，识别所有坏节点。oracle 只在被测组内每个节点都正常时返回 True；如果这种信息不足以区分可能的坏节点集合，返回 None。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `bad_nodes(n, test) -> set[int] | None`：节点编号为 `0..n-1`，返回坏节点集合。如果 oracle 提供的信息不足以确定答案（好节点少于两个），返回 `None`。
- `test(indices) -> bool`：只接受至少两个互不相同的节点，组内全是好节点时返回 `True`。
- oracle 是确定的、没有噪声，事先不告诉你任何好节点。$n \le 100$，`n >= 0`。

### 示例

```text
n = 4, 坏节点 {2}       -> {2}
n = 4, 坏节点 {}        -> set()
n = 3, 坏节点 {0, 1}    -> None    # 只剩一个好节点，所有二人组都失败
n = 2, 坏节点 {1}       -> None    # 唯一的测试失败，分不清是哪个坏
```

## 解题思路与参考答案

我会先判断测试能否区分答案，再找可靠搭档定位坏节点。例如所有二人组都失败时，「全部是坏的」和「只有一个是好的」表现完全相同，不能强行给出坏节点集合；只要测出一对好节点，剩下的就能逐个判断。

## 题目

有 n 个 GPU 节点，其中一些是坏的。唯一的检测手段是对一组节点做集合测试：组里至少要有两个节点，当且仅当组内全部是好节点时测试才通过。要求找出所有坏节点；并行安排测试时，同一个节点不能同时参加两组测试。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先讨论可识别性，再写代码。两个都未知的节点一起测试失败，你只知道「至少一个坏」，定位不了是哪个。如果手里没有任何已知的好节点，有些情况根本区分不开：比如所有二人组都失败时，「全部是坏的」和「只有某一个是好的」给出的测试结果一模一样。

某个二人组一旦通过，就获得了两个已知好节点。拿其中一个与待测节点组队，测试结果就只取决于待测节点：失败说明它坏，通过说明它好。每次仍满足至少两个节点的限制。

安排并行时，我会分别计算总测试次数和墙钟时间上的轮数。同一轮里的测试组必须互不相交，一个好搭档一轮只能测一个节点，所以想缩短轮数，就得先多找几个好节点，让它们各带一个待测节点同时测。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `bad_nodes(n, test) -> set[int] | None`：节点编号为 `0..n-1`，返回坏节点集合。如果 oracle 提供的信息不足以确定答案（好节点少于两个），返回 `None`。
- `test(indices) -> bool`：只接受至少两个互不相同的节点，组内全是好节点时返回 `True`。
- oracle 是确定的、没有噪声，事先不告诉你任何好节点。$n \le 100$，`n` 为负时抛 `ValueError`。
- 参考实现按顺序逐个测试，不追求最少轮数的并行调度。

### 输入输出示例

```text
n = 4, 坏节点 {2}       -> {2}
n = 4, 坏节点 {}        -> set()
n = 3, 坏节点 {0, 1}    -> None    # 只剩一个好节点，所有二人组都失败
n = 2, 坏节点 {1}       -> None    # 唯一的测试失败，分不清是哪个坏
```

### 解题思路与正确性

第一步按顺序测试所有二人组，找到第一个通过的 `(i, j)`。找到了，`i` 和 `j` 都是好的；第二步用 `i` 当搭档，对其余每个节点测试 `[i, node]`，失败就记为坏节点。因为搭档确定是好的，这一步的判断是准确的。

如果所有二人组都失败，说明好节点最多只有一个。此时任何至少两人的测试都会失败，不管好节点是哪个、还是根本没有，测试结果都一样，所以没有算法能分辨，返回 `None` 表示信息不足，而不是随便猜一个答案。

### 完整参考实现（Python 3）

```python
def find_good_pair(n, test):
    """顺序测试所有二人组，返回第一个通过的 (i, j)；全部失败时返回 None。"""
    for i in range(n):
        for j in range(i + 1, n):
            if test([i, j]):
                return i, j
    return None


def bad_nodes(n, test):
    """返回坏节点集合；oracle 提供的信息不足以确定答案时返回 None。

    test(group) 只接受至少两个不同节点，当且仅当组内全是好节点时返回 True。
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    pair = find_good_pair(n, test)
    if pair is None:
        # 所有二人组都失败，说明好节点最多一个，而含有坏节点的组都会失败，
        # 「全坏」和「只有某一个好」这些情况给出的测试结果完全相同，无法区分
        return None

    partner = pair[0]  # 通过测试的组里两人都是好节点，任选一个当搭档
    bad = set()
    for node in range(n):
        if node in pair:
            continue
        # 搭档是好的，所以 [partner, node] 失败当且仅当 node 是坏的
        if not test([partner, node]):
            bad.add(node)
    return bad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert len(group) >= 2` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
from itertools import product

# 穷举 n = 2..6 的所有好坏组合
for n in range(2, 7):
    for flags in product((False, True), repeat=n):
        bad = {node for node, is_bad in enumerate(flags) if is_bad}

        def oracle(group):
            assert len(group) >= 2
            assert len(set(group)) == len(group)
            return not any(node in bad for node in group)

        expected = bad if n - len(bad) >= 2 else None
        assert bad_nodes(n, oracle) == expected

# 不到两个节点时没有合法测试，无法判定
assert bad_nodes(0, lambda group: True) is None
assert bad_nodes(1, lambda group: True) is None
```



### 复杂度与追问

最坏情况是好节点排在最后，找好二人组要 $O(n^2)$ 次 oracle 调用；之后的逐个测试是 O(n) 次。额外空间是 O(n)，用来存结果。

- 追问「怎样减少轮数」：找到一对好节点后，每一轮让每个已知好节点各带一个待测节点并行测试，测出来的好节点下一轮也能当搭档。好节点占多数时，已知好节点数接近每轮翻倍，轮数大约是 O(log n)。同一轮里每个节点只能出现在一组里。
- 追问「能不能二分」：大组测试通过时可以一次确认很多好节点，坏节点少时有用；但大组失败只能说明组里至少有一个坏的，坏节点多时二分并不一定省次数，不能笼统说二分总能更快定位。

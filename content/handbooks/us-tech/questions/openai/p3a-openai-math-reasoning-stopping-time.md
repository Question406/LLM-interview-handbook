---
id: p3a-openai-math-reasoning-stopping-time
section: openai
order: 619
level: S
title: OpenAI：随机求解时间：LLM 推理重启策略
quick: >-
  固定阈值下，期望总时间是单次尝试的期望耗时除以成功概率，离散分布只需枚举支持点找最优阈值。每次重启必须有独立新随机性，并把预热成本计入
  overhead；未知分布需另谈通用重启序列。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - OpenAI
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · OpenAI · math-reasoning-stopping-time
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/math-reasoning-stopping-time
    type: secondary
---

## 题目描述

计算超时重启策略的期望完成时间，并寻找最佳超时阈值。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`expected_restart(times,probs,tau,overhead=0)` 返回浮点期望总耗时。每次独立尝试的自然完成时间 T 取 times 中的正值，概率为对应 probs，概率非负且和为 1。每次尝试先花 overhead，然后若 T<=tau 则再花 T 并成功；否则花 tau 后重新开始一次独立尝试。tau>0、overhead>=0；成功概率为 0 时返回正无穷。

`best_threshold(times,probs,overhead=0)` 仅在 times 中的阈值候选中选择，返回 `(最小期望耗时,阈值)`；最小期望相同时选较小阈值。支持点数不超过 1000。

### 示例

```text
times=[1,100], probs=[0.5,0.5], overhead=0。
expected_restart(...,tau=1)=2；tau=100 时为 50.5。
best_threshold(...)=(2,1)。
times=[2],probs=[1],tau=1 时返回 inf。
```

## 解题思路与参考答案

我会先求固定阈值下的期望总时间，再比较候选阈值。固定阈值 $\tau$ 表示每次最多跑 $\tau$，未解出就独立重启。设单次尝试的成功概率为 $s = P(T \le \tau)$，单次尝试的期望耗时为 $c = \text{overhead} + E[\min(T, \tau)]$。每次尝试要么成功结束，要么失败后回到起点，所以期望总时间 E 满足

## 题目

一个随机求解器（例如用 LLM 做数学推理）每次运行的耗时服从已知分布，有时很快解出，有时会跑很久。设计一个重启策略：跑到一定时间还没解出就放弃，从头独立重来，使得到解所需的期望总时间最小。还要讨论最坏情况。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

$$E = c + (1 - s)E,$$

解得 $E = c / s$。如果 $s = 0$，永远不会成功，期望时间为无穷。

例如一半概率 1 秒解出、一半概率 100 秒：不重启的期望是 50.5 秒；取 $\tau = 1$，每次尝试耗时 1 秒、成功率 0.5，期望只要 2 秒。重尾分布正是重启有用的场景。

这个公式成立的前提是每次重启都带来新的、独立的随机性。如果重跑走的是完全相同的确定性路径（比如固定种子、temperature 为 0），重启不会有任何改善。

最坏情况要分开讨论：分布未知或可能是对抗构造的时候，不能直接用已知分布下算出的最优阈值，要讨论不依赖分布的通用重启序列（例如 Luby 序列）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `expected_restart(times, probs, tau, overhead=0.0) -> float`：完成时间是离散分布，取值 `times`（都大于 0），概率 `probs`（非负，和为 1）。每次尝试先付 `overhead`，若 $T \le \tau$ 则成功，否则耗时 $\tau$ 后独立重来。返回期望总耗时，永远不可能成功时返回 `math.inf`。
- `best_threshold(times, probs, overhead=0.0) -> tuple[float, float]`：在 `times` 的各个取值里选期望耗时最小的阈值，返回 `(期望耗时, tau)`，并列时取较小的 `tau`。
- 分布不合法、`tau <= 0` 或 `overhead < 0` 时抛 `ValueError`。支持点不超过 1000 个。

### 输入输出示例

```text
expected_restart([1, 100], [0.5, 0.5], tau=1)   -> 2.0
expected_restart([1, 100], [0.5, 0.5], tau=100) -> 50.5     # 等价于不重启
best_threshold([1, 100], [0.5, 0.5])            -> (2.0, 1)
expected_restart([2], [1], tau=1)               -> inf
```

### 解题思路与正确性

`expected_restart` 直接计算 $c / s$。

`best_threshold` 只需要枚举支持点。原因是 $\tau$ 落在两个相邻支持点之间时，成功概率 $s$ 不变，而 $E[\min(T, \tau)]$ 随 $\tau$ 增大不减，所以把 $\tau$ 往下挪到左边的支持点不会更差。取最大的支持点作为阈值时一定成功，等价于不重启，因此「不重启」也已经在候选里。

### 完整参考实现（Python 3）

```python
import math


def _check_distribution(times, probs, overhead):
    if not times or len(times) != len(probs):
        raise ValueError("times and probs must be non-empty and the same length")
    if any(t <= 0 for t in times):
        raise ValueError("solve times must be positive")
    if any(p < 0 for p in probs) or not math.isclose(sum(probs), 1.0):
        raise ValueError("probs must be non-negative and sum to 1")
    if overhead < 0:
        raise ValueError("overhead must be non-negative")


def expected_restart(times, probs, tau, overhead=0.0):
    """阈值为 tau 的重启策略下，求解完成的期望总耗时。

    每次尝试先付 overhead，跑到 min(T, tau)；T <= tau 算成功，否则从头独立重来。
    """
    _check_distribution(times, probs, overhead)
    if tau <= 0:
        raise ValueError("tau must be positive")

    success = sum(p for t, p in zip(times, probs) if t <= tau)
    if success == 0:
        return math.inf
    cost_per_attempt = overhead + sum(p * min(t, tau) for t, p in zip(times, probs))
    # E = cost + (1 - success) * E  =>  E = cost / success
    return cost_per_attempt / success


def best_threshold(times, probs, overhead=0.0):
    """在所有支持点里找期望耗时最小的阈值，返回 (期望耗时, tau)，并列取较小的 tau。"""
    candidates = sorted(set(times))  # 最大的支持点等价于「不重启」
    return min(
        (expected_restart(times, probs, tau, overhead), tau) for tau in candidates
    )
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert expected_restart([1, 100], [0.5, 0.5], 1) == 2` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 一半概率 1 秒解出，一半 100 秒：tau = 1 时期望 2，不重启是 50.5
assert expected_restart([1, 100], [0.5, 0.5], 1) == 2
assert expected_restart([1, 100], [0.5, 0.5], 100) == 50.5
assert best_threshold([1, 100], [0.5, 0.5]) == (2.0, 1)

# 阈值小于所有求解时间，永远不会成功
assert expected_restart([2], [1], 1) == math.inf

# 每次尝试的固定开销
assert expected_restart([2], [1], 2, 1) == 3

# 开销大到重启不划算时，最佳阈值就是不重启
assert best_threshold([1, 100], [0.5, 0.5], 100) == (150.5, 100)

# 非法分布
expect_value_error(expected_restart, [1, 2], [0.5, 0.6], 1)
expect_value_error(expected_restart, [0], [1], 1)
expect_value_error(expected_restart, [1], [1], 0)
```

### 复杂度与追问

设支持点有 N 个。一次 `expected_restart` 是 O(N)，`best_threshold` 枚举 N 个阈值，共 O($N^2$)。把支持点排序后用前缀和维护成功概率和 $E[\min(T, \tau)]$，可以降到 O(N log N)。

- 分布未知怎么办？可以用 Luby 序列这类通用重启序列，它对任意分布的期望时间都在最优固定阈值的对数因子以内。已知分布下的最优阈值公式不能拿来声称最坏情况最优。
- 重启有缓存或预热成本时，把它计入 `overhead`；如果重启可以复用部分计算（例如保留 prompt 的 KV cache），尝试之间不再完全独立，需要重新建模。

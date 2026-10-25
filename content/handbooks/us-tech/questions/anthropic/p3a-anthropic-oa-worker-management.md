---
id: p3a-anthropic-oa-worker-management
section: anthropic
order: 616
level: A
title: "Anthropic：员工管理：打卡、晋升和重叠奖金"
quick: "我会在每次入场时冻结工资率，晋升留到下一次入场才用。结算只看已结束会话，先与查询区间求交，再按奖金端点切段，逐段计算时长、工资率和叠加倍率。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · oa-worker-management"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/oa-worker-management
    type: secondary
---

## 题目描述

实现员工工时与工资记录，支持下次上班起生效的工资调整和可重叠的奖金时段。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`Workers.add(worker_id, rate)` 注册员工；`enter(id,t)` 与 `leave(id,t)` 形成半开工作区间 `[进入时间,离开时间)`。每位员工的操作时间单调不减，工作段互不重叠。`promote(id,new_rate)` 只在该员工下一次 enter 起生效，不改变正在进行的工作段；多次待生效调整以后一次为准。

`bonus(start,end,multiplier)` 注册半开奖金区间，multiplier>=1；重叠奖金的倍率相乘。`salary(id,start,end)` 返回已结束工作段与查询半开区间交集的工资总和，各工作段按进入时锁定的基础工资率计算。未结束工作段不计入；空查询区间返回 0。时间与基础工资为整数，工作段、奖金记录各不超过 1000。

### 示例

```text
add("a",10); enter("a",0); promote("a",20); leave("a",10)
bonus(2,4,2)
salary("a",0,10) = 120；salary("a",3,5) = 30
enter("a",10); leave("a",12)
salary("a",10,12) = 40
```

## 解题思路与参考答案

## 题目

实现一个员工工时与工资系统：记录员工打卡进出，支持晋升（新工资率从下一次入场开始生效），支持在某个时间段发放奖金倍率，最后能查询某员工在任意时间区间内挣了多少钱。奖金区间可能互相重叠，也可能只和工作区间部分重叠。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

我会在入场时把工资率存进本次会话，之后晋升只登记为待生效值。比如入场工资率是 10，中途晋升到 20，这次离场前仍按 10 算，下次入场才按 20。这样不会追溯改掉已经结束或进行中的会话。

每个员工分别存已结束会话、进行中会话和待生效晋升。`promote` 只登记新工资率，下一次 `enter` 一次性应用并清掉待生效值。进行中的会话先不结算，避免离场后重复算。

结算时先求会话和查询区间的交集，再用交集内的全部奖金端点切段。一小段内部没有奖金开始或结束，倍率就固定，用“时长 × 工资率 × 倍率”累加即可。重叠奖金是相乘、相加还是取最大，要先确认；这份练习选相乘。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Workers.add(worker_id, rate)`：新增员工，id 重复或工资率为负时抛 `ValueError`。
- `enter(worker_id, t)` / `leave(worker_id, t)`：打卡进出。每个员工的会话不重叠，时间不能倒退，重复入场或未入场就离场都抛 `ValueError`。
- `promote(worker_id, new_rate)`：下次 `enter` 才生效；再次 `promote` 会覆盖还没生效的旧值。
- `bonus(start, end, multiplier)`：在半开区间 `[start, end)` 内工资乘以 `multiplier`，要求 `multiplier >= 1`；多个奖金重叠时倍率相乘。
- `salary(worker_id, start, end)`：只统计已结束会话与 `[start, end)` 的交集，每个会话按入场时的工资率计费。
- 时间和金额都是整数，会话和奖金各不超过 1000 个。

### 输入输出示例

```text
add("a", 10); enter("a", 0); promote("a", 20); leave("a", 10); bonus(2, 4, 2)
salary("a", 0, 10)   -> 120    # 8 × 10 + 2 × 10 × 2，[2, 4) 双倍
enter("a", 10); leave("a", 12)
salary("a", 10, 12)  -> 40     # 晋升在这次入场时生效：2 × 20
salary("a", 3, 5)    -> 30     # [3, 4) 双倍 20 + [4, 5) 10
```

### 解题思路与正确性

工资率在入场时冻结进会话，之后的 `promote` 只改 `pending_rate`，所以历史会话和进行中的会话都不会被追溯修改。

结算时，交集区间内部的所有奖金端点把它切成若干小段。任意一段内部没有端点，所以每个奖金要么完全覆盖这段、要么完全不覆盖，倍率是常数，用左端点查一次即可。逐段累加后，重叠奖金、跨越查询边界的奖金、只覆盖会话一部分的奖金都能正确处理。倍率相乘是这份练习的约定，原题可能有不同规则。

### 完整参考实现（Python 3）

```python
from dataclasses import dataclass, field


@dataclass
class Worker:
    rate: int
    pending_rate: int | None = None   # 晋升后的新工资率，下次入场才生效
    active: tuple | None = None       # 进行中的会话 (入场时间, 冻结的工资率)
    sessions: list = field(default_factory=list)  # 已结束的 (start, end, rate)
    last_time: float = float("-inf")


class Workers:
    def __init__(self):
        self.workers = {}
        self.bonuses = []  # (start, end, multiplier)，半开区间

    def add(self, worker_id, rate):
        if worker_id in self.workers or rate < 0:
            raise ValueError(f"cannot add worker {worker_id!r} with rate {rate}")
        self.workers[worker_id] = Worker(rate)

    def enter(self, worker_id, t):
        worker = self.workers[worker_id]
        if worker.active is not None or t < worker.last_time:
            raise ValueError(f"invalid enter for {worker_id!r} at {t}")
        if worker.pending_rate is not None:  # 晋升在入场这一刻一次性生效
            worker.rate = worker.pending_rate
            worker.pending_rate = None
        worker.active = (t, worker.rate)  # 工资率冻结到本次会话
        worker.last_time = t

    def leave(self, worker_id, t):
        worker = self.workers[worker_id]
        if worker.active is None or t < worker.last_time:
            raise ValueError(f"invalid leave for {worker_id!r} at {t}")
        start, rate = worker.active
        worker.sessions.append((start, t, rate))
        worker.active = None
        worker.last_time = t

    def promote(self, worker_id, new_rate):
        """登记新工资率；新的 promote 覆盖还没生效的旧值。"""
        if new_rate < 0:
            raise ValueError("rate must be non-negative")
        self.workers[worker_id].pending_rate = new_rate

    def bonus(self, start, end, multiplier):
        if end <= start or multiplier < 1:
            raise ValueError("bonus needs start < end and multiplier >= 1")
        self.bonuses.append((start, end, multiplier))

    def _multiplier_at(self, t):
        """时刻 t 生效的总倍率：所有覆盖 t 的奖金倍率相乘。"""
        product = 1
        for start, end, multiplier in self.bonuses:
            if start <= t < end:
                product *= multiplier
        return product

    def salary(self, worker_id, start, end):
        """已结束会话与 [start, end) 交集内的工资，按会话的冻结工资率乘奖金倍率。"""
        if end < start:
            raise ValueError("end must be >= start")
        total = 0
        for session_start, session_end, rate in self.workers[worker_id].sessions:
            lo = max(session_start, start)
            hi = min(session_end, end)
            if lo >= hi:
                continue
            # 奖金端点把 [lo, hi) 切成倍率不变的小段
            cuts = {lo, hi}
            for bonus_start, bonus_end, _ in self.bonuses:
                cuts.update(x for x in (bonus_start, bonus_end) if lo < x < hi)
            points = sorted(cuts)
            for left, right in zip(points, points[1:]):
                total += (right - left) * rate * self._multiplier_at(left)
        return total
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert workers.salary("a", 0, 10) == 120` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
# 会话中途晋升不影响当前会话；[2, 4) 双倍：8 * 10 + 2 * 10 * 2 = 120
workers = Workers()
workers.add("a", 10)
workers.enter("a", 0)
workers.promote("a", 20)
workers.leave("a", 10)
workers.bonus(2, 4, 2)
assert workers.salary("a", 0, 10) == 120

# 下次入场才用新工资率 20
workers.enter("a", 10)
workers.leave("a", 12)
assert workers.salary("a", 10, 12) == 40

# 查询区间截断会话和奖金：[3, 4) 双倍 20 + [4, 5) 10 = 30；空区间为 0
assert workers.salary("a", 3, 5) == 30
assert workers.salary("a", 10, 10) == 0

# 重叠奖金倍率相乘：[1, 2) 只有 3 倍，[2, 3) 是 2 * 3 = 6 倍
overlap = Workers()
overlap.add("b", 1)
overlap.bonus(2, 4, 2)
overlap.bonus(1, 3, 3)
overlap.enter("b", 0)
overlap.leave("b", 4)
assert overlap.salary("b", 0, 4) == 1 + 3 + 6 + 2

# 进行中的会话不计入；重复入场报错
overlap.enter("b", 5)
assert overlap.salary("b", 0, 100) == 12
try:
    overlap.enter("b", 6)
except ValueError:
    pass
else:
    raise AssertionError("entering twice should raise ValueError")
```

### 复杂度与追问

设某员工有 S 个已结束会话、系统里有 B 个奖金。每个会话切出最多 O(B) 段，每段查倍率又扫一遍 B 个奖金，单次查询 O(S · (B log B + $B^{2}$))；空间 O(S + B)。

- 查询很频繁时：先把所有奖金端点排序，扫描一遍得到「倍率恒定的区间」列表，再对「倍率 × 时长」做前缀和。每段会话的奖金加成就能用二分查两个端点得到，单次查询降到 O(S log B)。
- 如果允许事后补登或修改历史打卡、奖金，上面预处理的索引和缓存要随之失效重建。

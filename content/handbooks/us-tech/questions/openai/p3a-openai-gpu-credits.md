---
id: p3a-openai-gpu-credits
section: openai
order: 600
level: A
title: "OpenAI：GPU Credits：乱序事件、过期额度与负余额变体"
quick: "把发放和扣款存成事件日志，查询时按时间戳重放，每次扣款只用当时有效、最早到期的 grant；先确认到期端点和透支规则。"
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
  - title: "1Point3Acres · OpenAI · gpu-credits"
    url: https://www.1point3acres.com/interview/problems/company/openai/gpu-credits
    type: secondary
---

## 题目

实现一个 GPU 额度账本，支持三种操作：发放带有效期的额度、在某个时刻扣款、查询某个时刻的余额。扣款优先花最早过期的额度，而且事件可以乱序到达。

> 来源：一亩三分地 OpenAI GPU Credits 详情页（2026-10-18 读取），包含闭区间到期、乱序重放和负余额变体，是网站对候选人报告的归纳，没有逐条核对原帖。原页面有一条重放建议有歧义：不能在查询时先丢弃所有已过期的 grant，而要逐个事件判断有效性，因为这个 grant 可能付过更早的扣款。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

最稳的做法是把所有操作存成事件日志，查询时按时间戳排序重放。重放时，每次扣款只能用那个时刻有效的 grant。这样做天然处理了乱序到达，也保证历史上已经花掉的额度不会因为查询时间不同而「复活」。

这道题的细节变体很多，动手前要和面试官确认：

- 到期是闭区间还是半开区间。这里的版本是闭区间，到期那一刻还能用。
- 透支怎么处理。这里的版本是透支后余额返回 `None`，新的额度会先还债，还清后恢复；另有「透支后永久失败」的版本。
- 余额恰好为零时返回 `0`，有债务或者没有有效 grant 时返回 `None`。

先写出重放版本作为正确性基准，再谈优化：顺序到达时用按到期时间排序的最小堆，乱序时加检查点，插入较早事件后让它之后的检查点失效。

相关题：[[openai-gpu-credits]]（另一份转述，用半开区间并拒绝透支。两个契约不同，要分开练，不能混用端点和负余额规则）；[[p3a-perplexity-credit-tracker-with-expiring-credits]]（Perplexity 的同类题，共用同一份练习代码）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Credits.add(grant_id, amount, start, duration)`：发放一笔额度，有效期是闭区间 $[start, start + duration]$。`grant_id` 不能重复。
- `Credits.subtract(amount, timestamp)`：在 `timestamp` 时刻扣款，优先花最早到期的额度；到期时间相同时按 `grant_id` 排序。
- `Credits.balance(timestamp)`：返回该时刻的可用余额。有未还清的债务，或者没有任何有效 grant 时返回 `None`；额度恰好花完但 grant 仍在有效期内返回 `0`。
- 调用可以乱序到达，结果只取决于事件时间戳。每个时间戳只能有一个事件，重复则抛 `ValueError`。
- 扣款超过可用额度时，差额记为债务，之后到来的 grant 先还债。这是「可恢复的负余额」版本，不是「透支后永久失败」的版本。
- 最多 1000 个事件，金额和时间都是非负整数。

### 输入输出示例

```text
subtract(2, 35)          # 扣款先到
add("a", 4, 20, 40)      # 有效期 [20, 60]
add("b", 3, 30, 10)      # 有效期 [30, 40]
balance(40) -> 5         # 35 时先花 b 的 2，剩 a=4、b=1
balance(41) -> 4         # b 过期
balance(19) -> None      # 还没有任何 grant
```

把 `subtract` 放到最后调用，结果完全一样。

### 解题思路与正确性

`balance` 每次都从空状态开始，按时间戳顺序重放所有不晚于查询时刻的事件。因为只看时间戳，不看调用顺序，乱序到达不影响结果；查询也不修改事件日志。

重放时只在处理每个事件之前，淘汰在那个时刻已经过期的 grant。这一点决定了正确性：一个 grant 可能在早期付过一笔扣款，到查询时才过期。如果查询时先把所有过期 grant 一起丢掉再算，就等于把这笔早期扣款转嫁给了别的 grant。测试里的第三个场景就是这个情况。

扣款按到期时间从早到晚花，花不完的部分累加到 `debt`；`add` 先用新额度还债，剩下的才进入可用额度。

### 完整参考实现（Python 3）

```python
class Credits:
    """带有效期的额度账本。事件可以乱序到达，查询时按时间戳重放。

    grant 在闭区间 [start, start + duration] 内有效；扣款优先花最早到期的 grant，
    不够的部分记为债务，之后到来的 grant 先还债。
    """

    def __init__(self):
        self.events = {}  # 时间戳 -> 事件；同一时间戳只允许一个事件
        self.grant_ids = set()

    def _record(self, timestamp, event):
        if timestamp < 0:
            raise ValueError(f"timestamp must be non-negative: {timestamp}")
        if timestamp in self.events:
            raise ValueError(f"duplicate timestamp: {timestamp}")
        self.events[timestamp] = event

    def add(self, grant_id, amount, start, duration):
        if grant_id in self.grant_ids:
            raise ValueError(f"duplicate grant id: {grant_id!r}")
        if amount < 0 or duration < 0:
            raise ValueError("amount and duration must be non-negative")
        self._record(start, ("add", grant_id, amount, start + duration))
        self.grant_ids.add(grant_id)

    def subtract(self, amount, timestamp):
        if amount < 0:
            raise ValueError(f"amount must be non-negative: {amount}")
        self._record(timestamp, ("subtract", amount))

    def balance(self, timestamp):
        """返回 timestamp 时刻的可用余额；有债务或没有有效 grant 时返回 None。"""
        active = {}  # grant id -> [到期时间, 剩余额度]
        debt = 0
        for event_time, event in sorted(self.events.items()):
            if event_time > timestamp:
                break
            # 只淘汰「这个事件发生时」已经过期的 grant。
            # 一个 grant 可能先付过早期扣款、到查询时才过期，所以不能按查询时间提前丢弃。
            active = drop_expired(active, event_time)
            if event[0] == "add":
                _, grant_id, amount, end = event
                repaid = min(debt, amount)
                debt -= repaid
                active[grant_id] = [end, amount - repaid]
            else:
                debt += spend_earliest_expiring(active, event[1])

        active = drop_expired(active, timestamp)
        if debt or not active:
            return None
        return sum(remaining for _, remaining in active.values())


def drop_expired(active, now):
    """保留到期时间 >= now 的 grant（闭区间，到期那一刻仍然有效）。"""
    return {grant_id: grant for grant_id, grant in active.items() if grant[0] >= now}


def spend_earliest_expiring(active, amount):
    """按到期时间从早到晚扣 amount，原地修改 active，返回扣不完的差额。"""
    need = amount
    for grant_id in sorted(active, key=lambda gid: (active[gid][0], gid)):
        if need == 0:
            break
        paid = min(need, active[grant_id][1])
        active[grant_id][1] -= paid
        need -= paid
    return need
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 扣款先于 grant 到达：重放后结果和按时间顺序到达一样
credits = Credits()
credits.subtract(2, 35)
credits.add("a", 4, 20, 40)
credits.add("b", 3, 30, 10)
assert credits.balance(40) == 5   # 35 时先花最早到期的 b
assert credits.balance(41) == 4   # b 在 40 之后过期
assert credits.balance(19) is None

# 恰好花完但 grant 仍有效返回 0；过期后没有有效 grant 返回 None
credits = Credits()
credits.add("a", 4, 0, 10)
credits.subtract(4, 5)
assert credits.balance(10) == 0
assert credits.balance(11) is None

# 已过期的 a 付过早期扣款，这笔钱不能改算到 b 头上
credits = Credits()
credits.add("a", 4, 0, 1)
credits.subtract(3, 1)
credits.add("b", 10, 3, 10)
assert credits.balance(3) == 10

# 先透支形成债务，新 grant 先还债
credits = Credits()
credits.subtract(4, 1)
assert credits.balance(1) is None
credits.add("a", 6, 2, 10)
assert credits.balance(2) == 2

# 非法输入
expect_value_error(credits.add, "a", 1, 50, 1)   # grant id 重复
expect_value_error(credits.subtract, 1, 2)       # 时间戳重复
expect_value_error(credits.subtract, -1, 60)     # 负金额
```

### 复杂度与追问

设事件数为 E、grant 数为 G。每次查询要排序事件 O(E log E)，每次扣款再对活跃 grant 排序 O(G log G)，所以单次查询是 $O(E \log E + E \cdot G \log G)$，空间 O(E + G)。

- 事件按时间顺序到达时怎么优化？维护一个按到期时间排序的最小堆，扣款时从堆顶取，余额增量更新，每个操作 O(log G)。
- 乱序到达又要快速查历史余额呢？按时间存一些检查点（某时刻的完整状态）。插入一个较早的事件后，它之后的检查点全部失效，从前一个检查点开始重放。只维护一个「当前余额」变量回答不了历史查询。
- 透支后是永远失败，还是还清债务后恢复？面经里两种版本都出现过，要先和面试官确认，本练习实现的是可恢复版本。

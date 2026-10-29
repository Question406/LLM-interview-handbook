---
id: openai-gpu-credits
section: openai
order: 40
level: S
title: OpenAI：GPU credit，调用乱序也要按时间重放
quick: >-
  调用乱序时，我会只追加事件日志，查询再按时间戳重放，扣款优先花最早到期的额度。这样后来到达的早期事件也能影响历史查询；先确认区间端点和欠款规则，再实现对应版本。
tags:
  - 完整编程练习
  - OpenAI
  - Coding
  - Intervals
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 'Targeting OpenAI SWE Roles, r/leetcode'
    url: >-
      https://www.reddit.com/r/leetcode/comments/1qlzflr/targeting_openai_swe_roles_insights_on_what_to/
    type: candidate-first-hand
  - title: 'Openai Tech Phone Screen: GPU Credit Calculator'
    url: 'https://www.1point3acres.com/interview/thread/1098314'
    type: candidate-first-hand
  - title: 'FAANG-Coding-Interview-Questions, OpenAI bank'
    url: >-
      https://github.com/ombharatiya/FAANG-Coding-Interview-Questions/blob/main/FAANG-Recent-Questions.md
    type: secondary
---

## 题目描述

实现带有效期的额度账本，支持乱序录入、按事件时间查询和透支债务。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`Credits.add(credit_id,amount,start,duration)` 注册唯一编号的额度，有效期为闭区间 `[start,start+duration]`。`subtract(amount,timestamp)` 在该时刻消费，优先使用到期较早的有效额度，到期相同按 `credit_id` 字典序；不足部分形成债务，后续生效的新额度优先偿还债务。

`balance(t)` 按事件时间重建截至该时刻的结果，与方法调用顺序无关。若仍有债务或当时没有有效额度，返回 None；有有效额度但余额恰为零时返回 0。输入时间非负，不同事件时间互异，额度和消费金额非负，事件总数不超过 1000。

### 示例

```text
按调用顺序：subtract(2,35)；add("a",4,20,40)；add("b",3,30,10)。
balance(19)=None；balance(40)=5；balance(41)=4。
35 时先消费较早到期的 b；b 在 40 时仍有效，41 时过期。
```

## 解题思路与参考答案

我会保留完整事件日志，查余额时按事件时间重放到查询点，扣款从最早到期的额度开始。比如先收到 35 时刻扣 2，后收到 20 和 30 时刻生效的额度，仍能按 20、30、35 的顺序算对。区间是半开还是闭区间、余额不足是失败还是欠款，要先和面试官约定。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。公开转述没给全的接口和 decision boundary 由手册补齐。Python 3 标准库即可运行。

### 题面、接口与约束

- `Credits.add(credit_id, amount, start, duration)`：登记一笔额度，在闭区间 `[start, start + duration]` 内有效。`credit_id` 重复时抛 `ValueError`。
- `Credits.subtract(amount, t)`：在时刻 `t` 扣款，优先花最早到期的额度（到期时刻相同时按 id 排）。有效额度不够时，差额记成债务，之后生效的额度先拿来还债。
- `Credits.balance(t)`：返回时刻 `t` 的可用余额。有未还清的债务、或者没有任何有效额度时返回 `None`；额度恰好用完但仍在有效期内时返回 0。
- 调用可以乱序到达，结果只取决于事件自己的时间戳。所有事件（包括 `add` 的 `start`）的时间戳互不相同，重复的直接拒绝。
- 本练习采用「可以欠款、之后补上」的版本，不是「余额不够就永久失败」的版本，也不要直接套到别的面经上。最多 1000 个事件，金额、时长都是非负整数。

### 输入输出示例

```text
subtract(2, t=35)                     # 最先到达，但时间最晚
add("a", 4, start=20, duration=40)    # 有效期 [20, 60]
add("b", 3, start=30, duration=10)    # 有效期 [30, 40]

balance(19) -> None    # 还没有有效额度
balance(40) -> 5       # 35 时先花更早到期的 b：a = 4，b = 1
balance(41) -> 4       # b 已过期
```

### 解题思路与正确性

`add`、`subtract` 先记进日志，`balance(t)` 从空状态开始，只重放时间不晚于 `t` 的事件。排序以后，同一组事件得到同一结果，和调用到达顺序无关，查询也不修改日志。

重放到某个事件时，只淘汰在这个时刻已经过期的额度。一笔额度可能在过期之前就付掉了某次扣款；如果一开始就把「到 `t` 时已过期」的额度全部删掉，这次扣款就会被错算到别的额度上。

每笔有效额度只记剩余量，扣款时按到期时刻从早到晚扣减。扣不完的部分进入债务，下一笔生效的额度先还债，剩下的才变成可用余额。

### 完整参考实现（Python 3）

```python
class Credits:
    """GPU credit 账本：调用可以乱序到达，查询时按事件时间重放。

    额度在闭区间 [start, start + duration] 内有效，扣款优先用最早到期的额度；
    额度不够时记成债务，之后生效的额度先还债。
    """

    def __init__(self):
        self.events = {}  # 时间戳 -> 事件；所有事件的时间戳互不相同
        self.credit_ids = set()

    def _record(self, timestamp, event):
        if timestamp < 0 or timestamp in self.events:
            raise ValueError(f"timestamp {timestamp} is negative or already used")
        self.events[timestamp] = event

    def add(self, credit_id, amount, start, duration):
        if credit_id in self.credit_ids:
            raise ValueError(f"duplicate credit id {credit_id!r}")
        if amount < 0 or duration < 0:
            raise ValueError(
                f"amount and duration must be non-negative, got {amount} and {duration}"
            )
        self._record(start, ("add", credit_id, amount, start + duration))
        self.credit_ids.add(credit_id)

    def subtract(self, amount, timestamp):
        if amount < 0:
            raise ValueError(f"amount must be non-negative, got {amount}")
        self._record(timestamp, ("subtract", amount))

    @staticmethod
    def _drop_expired(active, now):
        return {cid: grant for cid, grant in active.items() if grant[0] >= now}

    def balance(self, t):
        """时刻 t 的可用余额；有未还清的债务或没有有效额度时返回 None。不修改日志。"""
        active = {}  # credit_id -> [end, remaining]
        debt = 0
        for timestamp, event in sorted(self.events.items()):
            if timestamp > t:
                break
            # 只淘汰在当前事件时刻已经过期的额度；之后才过期的额度此刻仍然能花
            active = self._drop_expired(active, timestamp)
            if event[0] == "add":
                _, credit_id, amount, end = event
                repaid = min(debt, amount)  # 新额度先还债
                debt -= repaid
                active[credit_id] = [end, amount - repaid]
            else:
                need = event[1]
                by_expiry = sorted(active, key=lambda cid: (active[cid][0], cid))
                for credit_id in by_expiry:
                    paid = min(need, active[credit_id][1])
                    active[credit_id][1] -= paid
                    need -= paid
                    if need == 0:
                        break
                debt += need  # 有效额度不够的部分记成债务
        active = self._drop_expired(active, t)
        if debt or not active:
            return None
        return sum(remaining for _, remaining in active.values())
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert credits.balance(40) == 5  # 扣款先花更早到期的 b：a=4, b=1` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 题面示例：扣款先于两笔额度到达，结果和按时间顺序到达一样
credits = Credits()
credits.subtract(2, 35)
credits.add("a", 4, 20, 40)
credits.add("b", 3, 30, 10)
assert credits.balance(40) == 5  # 扣款先花更早到期的 b：a=4, b=1
assert credits.balance(41) == 4  # b 在 40 之后过期
assert credits.balance(19) is None  # 还没有任何有效额度

# 查询不修改日志：重复查询结果相同
assert credits.balance(40) == 5

# 恰好用完但额度仍有效时返回 0；到期之后返回 None（闭区间，10 时仍有效）
credits = Credits()
credits.add("a", 4, 0, 10)
credits.subtract(4, 5)
assert credits.balance(10) == 0
assert credits.balance(11) is None

# 已过期的 a 在过期前付掉了早先的扣款，不能把这笔扣款改记到 b 上
credits = Credits()
credits.add("a", 4, 0, 1)
credits.subtract(3, 1)
credits.add("b", 10, 3, 10)
assert credits.balance(3) == 10

# 超额扣款形成债务，之后的额度先还债
credits = Credits()
credits.subtract(4, 1)
credits.add("a", 6, 2, 10)
assert credits.balance(2) == 2

# 债务比新额度还多：仍欠着，返回 None
credits = Credits()
credits.subtract(10, 1)
credits.add("a", 4, 2, 10)
assert credits.balance(3) is None

# 非法输入：时间戳重复、额度 id 重复、负数金额或时长
credits = Credits()
credits.add("a", 4, 0, 10)
expect_value_error(credits.subtract, 1, 0)
expect_value_error(credits.add, "a", 1, 5, 10)
expect_value_error(credits.add, "b", -1, 6, 10)
expect_value_error(credits.add, "c", 1, 7, -1)
expect_value_error(credits.subtract, -1, 8)
```

### 复杂度与追问

设事件数为 E、额度数为 G。参考实现每次查询要排序 E 个事件，每次扣款再按到期时刻排序一次有效额度，总共 O(E log E + E·G log G)；空间 O(E + G)。

- 追问「每次查询都重放太慢」：如果事件按时间顺序到达，可以维护一个按到期时刻排序的最小堆，边到达边处理。乱序插入时，插入点之后的检查点都要作废，不能只靠一个可变的「当前余额」回答历史时刻的查询，见下文追问。

## 真题记录

Reddit 上一篇 2026 年 OpenAI SWE 面试总结把 GPU Credit Calculator 列为最近考过的题，并给出了接口。一亩三分地有一条电话面帖子，标题就是 Implementing a GPU Credit Calculator，正文要登录才能看。GitHub 上 ombharatiya 的 2025–2026 题单把它列为 OpenAI 核心题：区间半开，先消耗最快过期的额度，任意时刻都能查余额。

公开转述里的接口是这三个：

- `addCredit(credit_id, amount, timestamp, expiration)`：额度从 `timestamp` 起可用。`expiration` 在不同转述里有人写成时长，有人写成结束时刻，现场要先问。GitHub 题单用的是半开区间 `[start, end)`。
- `useCredit(timestamp, amount)`：在这个时刻扣款。余额不够就失败，不能扣成负数。
- `getBalance(timestamp)`：这个时刻扣款、过期都处理完之后还剩多少。

调用顺序不等于时间顺序。可能先收到 `useCredit(20, 30)`，后收到 `addCredit(..., 50, start=10, end=50)`。时刻 20 落在这笔额度的有效区间里，这次使用仍然成立。

## 公开版本和练习版本的差别

上面的练习为了能写出确定的测试，选了一套和公开转述不同的约定：区间是闭区间 `[start, start + duration]`，余额不够时记债务而不是失败。面试时按面试官给的版本来。如果是公开转述的「半开区间、不够就失败」版本，写法如下。

这个版本同样保留事件日志。`add` 分别记录生效和过期，`use` 记扣款；`getBalance(t)` 取时间不超过 `t` 的事件，排序重放。

同一时刻的事件顺序要定死：先过期，再生效，再扣款。否则「恰好在过期时刻使用」这种情况会和测试对不上。重放时把还有效的额度按结束时刻排好，每次扣款从最快过期的开始扣，扣到够为止。

```python
RANK = {"expire": 0, "add": 1, "use": 2}  # 同一时刻：先过期，再生效，再扣款


def replay(events, t):
    """events: (kind, timestamp, *payload)。返回时刻 t 的余额；某次扣款不够时返回 None。"""
    active = []  # [end, remaining, credit_id]
    chosen = sorted((e for e in events if e[1] <= t), key=lambda e: (e[1], RANK[e[0]]))
    for kind, _timestamp, *payload in chosen:
        if kind == "expire":
            credit_id = payload[0]
            active = [grant for grant in active if grant[2] != credit_id]
        elif kind == "add":
            amount, end, credit_id = payload
            active.append([end, amount, credit_id])
        else:
            need = payload[0]
            active.sort()  # 最快过期的排在前面
            for grant in active:
                if need == 0:
                    break
                take = min(grant[1], need)
                grant[1] -= take
                need -= take
            if need:
                return None
            active = [grant for grant in active if grant[1] > 0]
    return sum(grant[1] for grant in active)
```

这个版本最难的是「失败」怎么定义。失败的 `use` 不能留在日志里，否则每次重放都会在它那里返回 `None`；只有成功的 `use` 才追加。但一次 `use` 是否成功，取决于时间更早的那些事件，而它们可能更晚才到达：后到的 `add` 可能让一次早先被拒绝的 `use` 本该成功。所以不能简单地按「收到调用那一刻的余额」决定成败，否则乱序的 `add` 一来，历史就错了。现场要和面试官确认：`useCredit` 是否必须当场返回结果，以及后到的事件能不能改变之前的判定。

## 追问

**每次查询都重放会不会太慢？**
面试时先交出正确的重放版本。事件很多时，可以按时间建检查点，查询从最近的检查点继续往后放。检查点必须早于所有还可能到达的事件，否则会漏掉更晚才收到、时间却更早的事件。所以检查点只能覆盖「时间戳和到达顺序都已经稳定」的那段前缀。

**同一笔额度被两次 use 各扣一部分怎么办？**
额度里存的是剩余量，不是原始面额。处理过期事件时按 `credit_id` 删掉剩下的部分，不要再按原始金额减一次。

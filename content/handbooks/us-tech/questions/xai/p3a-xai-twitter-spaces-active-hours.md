---
id: p3a-xai-twitter-spaces-active-hours
section: xai
order: 607
level: A
title: "xAI：Spaces 活跃时长与流式并发 top-K"
quick: "对每个房间里的每个用户记下加入时刻，离开时把在线时长累加到房间上，查询时把仍在线的会话临时算到当前时刻；流式 top-K 要处理人数下降带来的过期条目。"
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
  - title: "1Point3Acres · xAI · twitter-spaces-active-hours"
    url: https://www.1point3acres.com/interview/problems/company/xai/twitter-spaces-active-hours
    type: secondary
---

## 题目

给一串 Twitter Spaces 的 create / join / leave 日志，算出每个房间里所有用户的累计在线时长；进一步要求在事件流上实时维护当前并发人数最多的 top-K 房间。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

对每个（房间，用户）记下加入时刻。用户离开时，用离开时刻减去加入时刻，加到这个房间的累计时长上，然后删掉这条记录。查询时，还在线的用户临时算到查询时刻，不写回状态，这样重复查询不会重复计数。

动手前要和面试官确认几种边界：

- 同一个用户重复 join 怎么算：这份练习保留最早的加入时刻，后面的 join 忽略。
- 没有 join 就 leave，或者日志结束时还没 leave：前者忽略，后者在 `finish` 时算到给定时刻。
- 同一时刻的多个事件按什么顺序处理：这里按输入顺序。

还要分清两种「时长」：这里统计的是所有用户在线时长之和（人秒数），几个人同时在线时会大于房间本身存在的时间。

流式 top-K 的难点在于计数会下降。只往堆里追加新计数、不处理旧条目，堆顶可能是一个早已过时的人数。要么给堆条目带版本号、弹出时丢掉过期的，要么用有序结构在 join / leave 时同步更新。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Spaces.event(op, space, user, t)`：按时间顺序处理一条事件，`op` 是 `create`、`join` 或 `leave`。时间倒退、未知房间、未知 `op` 都抛 `ValueError`。
- 重复 `create` 不重置房间；重复 `join` 保留最早的加入时刻；没加入过的 `leave` 忽略。用户可以同时在多个房间。
- `finish(now)`：把还没离开的会话算到 `now`，返回 `{space: 人秒数}`，不修改内部状态。
- `top(k)`：返回当前在线人数最多的 k 个房间，人数降序，人数相同时房间名升序。
- 事件数不超过 $10^5$。

### 输入输出示例

```text
create(s, 0); join(s, a, 1); join(s, a, 2); join(s, b, 3); leave(s, a, 5)
finish(6) -> {"s": 7}      # a 在线 1..5 共 4 秒，b 在线 3..6 共 3 秒
top(1)    -> [("s", 1)]    # 现在只有 b 在线
```

### 解题思路与正确性

每段会话只在 `leave` 时入账一次，入账后就从在线表里删掉，所以不会被重复计入。还在线的会话由 `finish` 临时累加，不写回 `closed_total`，因此连续调用 `finish` 得到的结果一致。

`top` 每次直接按当前在线表的大小排序。实现简单，代价是每次查询都要扫一遍所有房间。另外要注意，非法事件在抛错前已经推进了时钟，这份练习不回滚时钟。

### 完整参考实现（Python 3）

```python
class Room:
    def __init__(self):
        self.joined_at = {}     # 在线用户 -> 加入时刻
        self.closed_total = 0   # 已离开会话的人秒数之和


class Spaces:
    """按时间顺序处理 create / join / leave 事件，统计每个房间的用户在线人秒数。"""

    def __init__(self):
        self.rooms = {}
        self.last_time = float("-inf")

    def _advance_clock(self, t):
        if t < self.last_time:
            raise ValueError(f"time went backwards: {t} < {self.last_time}")
        self.last_time = t

    def event(self, op, space, user, t):
        self._advance_clock(t)
        if op == "create":
            self.rooms.setdefault(space, Room())  # 重复 create 不重置房间
            return
        if space not in self.rooms:
            raise ValueError(f"unknown space: {space!r}")

        room = self.rooms[space]
        if op == "join":
            room.joined_at.setdefault(user, t)  # 重复 join 保留最早的加入时刻
        elif op == "leave":
            if user in room.joined_at:  # 没加入过的 leave 直接忽略
                room.closed_total += t - room.joined_at.pop(user)
        else:
            raise ValueError(f"unknown op: {op!r}")

    def finish(self, now):
        """把还没离开的会话临时算到 now，返回 {space: 人秒数}。不修改内部状态。"""
        if now < self.last_time:
            raise ValueError(f"time went backwards: {now} < {self.last_time}")
        return {
            space: room.closed_total + sum(now - t for t in room.joined_at.values())
            for space, room in self.rooms.items()
        }

    def top(self, k):
        """当前在线人数最多的 k 个房间，人数降序、房间名升序。"""
        counts = [(space, len(room.joined_at)) for space, room in self.rooms.items()]
        counts.sort(key=lambda item: (-item[1], item[0]))
        return counts[:k]
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

spaces = Spaces()
spaces.event("create", "s", "", 0)
spaces.event("join", "s", "a", 1)
spaces.event("join", "s", "a", 2)  # 重复 join，忽略
spaces.event("join", "s", "b", 3)
spaces.event("leave", "s", "a", 5)  # a 在线 4 秒

# b 从 3 到 6 还在线，算 3 秒；合计 7
assert spaces.finish(6) == {"s": 7}
assert spaces.top(1) == [("s", 1)]

# finish 不入账，重复调用结果不变
assert spaces.finish(6) == {"s": 7}

# 错误输入
expect_value_error(spaces.event, "join", "missing", "a", 6)
expect_value_error(spaces.event, "join", "s", "c", 4)
expect_value_error(spaces.event, "kick", "s", "b", 6)

# top 按人数降序、名字升序
spaces.event("create", "r", "", 7)
spaces.event("create", "q", "", 7)
spaces.event("join", "q", "x", 7)
spaces.event("join", "q", "y", 7)
assert spaces.top(3) == [("q", 2), ("s", 1), ("r", 0)]
```

### 复杂度与追问

设房间数为 R、当前在线会话数为 A。`event` 是 O(1)；`finish` 是 O(R + A)；`top` 每次排序，O(R log R)。

如果 `top` 调用很频繁，可以维护一个按（人数，房间名）排序的有序集合：join 时把房间从旧计数挪到新计数，leave 时反向操作，每次 O(log R)，查询直接取前 k 个。用堆的话要给每个房间记当前版本，弹出时比对版本，丢掉过期条目。

如果日志可能乱序到达，就不能再一边读一边入账。可以先按时间缓冲一个窗口再处理，或者为每个会话保存完整区间，最后统一计算。

## 相关题

- [[p3a-microsoft-top-k-largest-retain]]：静态数组上的 top-K，用大小为 K 的最小堆加复合排序键，不涉及计数下降和过期条目。

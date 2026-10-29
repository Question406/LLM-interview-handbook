---
id: xai-atomic-hierarchical-sliding-limiter
section: xai
order: 934
level: A
title: "xAI：user / team / company 的 atomic sliding-window rate limiter"
quick: "我会把三层检查和提交放在同一个 lock 内。只分别给每层加 lock 还不够：如果 user 已扣费、team 才发现满了，就得回滚，复杂度也会增加。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI：user / team / company 的 atomic sliding-window rate limiter"
    url: "https://landthelab.com/questions/pluggable-hierarchical-rate-limiter"
    type: secondary
---

## 题目描述

来源：Land the Lab 将 hierarchical rate limiter 题型列在 xAI / Cursor 下。这里采用精确 sliding window，并明确多层扣费必须 all-or-none。

### 输入、接口与规则

实现 `HierarchicalLimiter(limits, window)`，limits 为正整数容量 dict，key 使用 `('user',id)`、`('team',id)`、`('company',id)` 这样的 tuple；window 为正整数时间长度。`allow(user,team,company,cost,now)->bool` 一次同时计入对应三层，cost 为正整数，now 为非负整数时间。

窗口是 `(now-window,now]`：恰好落在左端点的历史 cost 已过期。三个 limits 全部有余量才接受，并在三层各计入相同 cost；被拒绝的调用不能在任何层留下新扣费。缺少配置抛 KeyError。多个 threads 可并发调用；now 在 lock 实际处理顺序中必须 nondecreasing，否则抛 ValueError。不实现网络、跨进程一致性或真实时钟；不修改 limits。

### 输入输出示例

```text
limits={user:u:2, team:t:3, company:c:3}, window=10。
allow("u","t","c",2,0) -> True；同样请求 cost=1,now=1 -> False。
now=10 时原 cost 过期，再请求 cost=1 -> True。
```

## 回答思路

> **Situation / Task：** 一次请求影响三层额度，拒绝不能造成部分扣费。  
> **Approach / Why：** 一个 lock 内清理过期记录、检查三层，再统一 append 与更新 totals。  
> **Result / Check：** 测试 cutoff、不同 users 共享 team，以及并发时 accepted cost 不超限。

## 解题思路与参考答案

我会把三层检查和提交放在同一个 lock 内。只分别给每层加 lock 还不够：如果 user 已扣费、team 才发现满了，就得回滚，复杂度也会增加。

每个 key 用 deque 保存时间与 cost，配一个 running total。先移除窗口外记录，再检查所有层；只有全部通过后才 append。这个 reference 适用于单进程，distributed 部署需要另一套 atomic storage 操作。

### 完整参考实现

```python
from collections import deque
from threading import Lock


class HierarchicalLimiter:
    def __init__(self, limits, window):
        if window <= 0 or any(v <= 0 for v in limits.values()):
            raise ValueError('positive limits/window required')
        self.limits = dict(limits)
        self.window = window
        self.events = {}
        self.totals = {}
        self.last = -1
        self.lock = Lock()

    def allow(self, user, team, company, cost, now):
        if cost <= 0 or now < 0:
            raise ValueError('invalid cost/time')
        keys = [('user', user), ('team', team), ('company', company)]
        with self.lock:
            capacities = [self.limits[key] for key in keys]
            if now < self.last:
                raise ValueError('time must not decrease')
            self.last = now
            for key in keys:
                events = self.events.setdefault(key, deque())
                total = self.totals.get(key, 0)
                while events and events[0][0] <= now - self.window:
                    total -= events.popleft()[1]
                self.totals[key] = total
            if any(self.totals[key] + cost > cap for key, cap in zip(keys, capacities)):
                return False
            for key in keys:
                self.events[key].append((now, cost))
                self.totals[key] += cost
            return True
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
from concurrent.futures import ThreadPoolExecutor

limits = {('user', 'u'): 2, ('user', 'v'): 2, ('team', 't'): 3, ('company', 'c'): 3}
r = HierarchicalLimiter(limits, 10)
assert r.allow('u', 't', 'c', 2, 0)
assert not r.allow('u', 't', 'c', 1, 1)
assert r.allow('v', 't', 'c', 1, 1)
assert not r.allow('v', 't', 'c', 1, 1)
assert r.allow('u', 't', 'c', 2, 10)
# Rejected request must not consume the other user's capacity.
r = HierarchicalLimiter(
    {('user', 'u'): 100, ('team', 't'): 7, ('company', 'c'): 100}, 10
)
with ThreadPoolExecutor(max_workers=16) as pool:
    outcomes = list(pool.map(lambda _: r.allow('u', 't', 'c', 1, 0), range(100)))
assert sum(outcomes) == 7
assert r.totals[('user', 'u')] == 7
assert r.totals[('company', 'c')] == 7
assert r.allow('u', 't', 'c', 7, 10)
try:
    r.allow('u', 't', 'c', 1, 9)
except ValueError:
    pass
else:
    raise AssertionError('decreasing time accepted')
print('hierarchical limiter tests passed')
```

## 复杂度与追问

每条 accepted event 在每层入队、出队各一次，清理 amortized cost 为 `O(1)`，单次最坏与本次过期记录数相关。空间与活跃窗口内 accepted events 和配置 key 数相关。追问实时生产环境应使用 monotonic clock，并讨论闲置 key 的 cleanup。

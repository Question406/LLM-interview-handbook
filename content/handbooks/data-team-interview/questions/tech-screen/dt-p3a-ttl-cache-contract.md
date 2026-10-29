---
id: dt-p3a-ttl-cache-contract
section: tech-screen
order: 73
level: A
title: Apple Sr MLE 原帖扩展：TTL 缓存到底何时过期、何时删除？
quick: >-
  先定义过期语义，再实现数据结构：本练习在 now 达到写入时刻加 TTL
  时过期，读取不续期，覆盖写入重置期限。逻辑上过期与物理删除分开，测试用注入时间，不依赖 sleep。
companies:
  - apple
tags:
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: apple Sr MLE onsite挂经，候选人原帖，Chrome核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1170122-1-1.html'
    type: interview
  - title: Python time.monotonic documentation
    url: 'https://docs.python.org/3/library/time.html#time.monotonic'
    type: primary
---

## 题目描述

### 原帖核对与练习约定

- 原帖：[apple Sr MLE onsite 挂经](https://www.1point3acres.com/bbs/thread-1170122-1-1.html)，发帖时间为页面显示的 2026-03-25 01:00:17；作者回复说明团队为 IS&T，不是 AFM team。
- 采集日期：2026-10-26。Chrome 中可见主楼及作者说明团队的回复。
- 原帖披露：工程与代码轮考缓存处理，TTL 超时的定义和删除时机需要澄清；没有披露完整接口、淘汰规则或并发要求。
- **本题练习约定**：实现单线程、无容量限制、读取不续期的 TTL cache，接口、半开有效期、主动清理和测试均为手册扩展。

### 输入与接口

实现 `TTLCache()`，初始为空，并提供：

- `put(key: str, value, ttl: float, now: float) -> None`：写入或覆盖键，value 不为 None。有效期为 `[now,now+ttl)`；ttl 非负。ttl=0 时立刻删除该键的旧值且不保存新值。
- `get(key: str, now: float)`：有效时返回 value，否则返回 None。过期键在访问时物理删除；成功读取不延长有效期。
- `expire(now: float) -> list[str]`：主动物理删除所有截止时间不大于 now 的条目，并返回按键名字典序排列的删除键列表。

### 输出与约束

所有时间以秒为单位，为有限数，now 与 ttl 的和有限；单个缓存的调用 now 全局非递减。key 可为空字符串，最多执行 100000 次操作。不要求容量淘汰或多线程同步。必须使用传入的 now，不能调用真实时间或 sleep。

### 示例

```text
put('a','old',ttl=2,now=10)
get('a',now=11) -> 'old'
get('a',now=12) -> None
put('a','new',ttl=5,now=12)
expire(now=17) -> ['a']
```

## 解题思路与参考答案

字典保存 value 和绝对过期时刻。读取时先检查 now 是否达到截止时刻，再决定返回或删除。覆盖写入替换整个记录，不会遗留一个能误删新值的旧过期事件。

```python
class TTLCache:
    def __init__(self):
        self.entries = {}

    def put(self, key, value, ttl, now):
        if ttl == 0:
            self.entries.pop(key, None)
        else:
            self.entries[key] = (value, now + ttl)

    def get(self, key, now):
        entry = self.entries.get(key)
        if entry is None:
            return None
        value, deadline = entry
        if now >= deadline:
            del self.entries[key]
            return None
        return value

    def expire(self, now):
        expired = sorted(
            key for key, (_, deadline) in self.entries.items() if now >= deadline
        )
        for key in expired:
            del self.entries[key]
        return expired
```

put/get 平均时间为 $O(1)$；主动 expire 扫描 M 个存储条目并对 K 个过期键排序，时间为 $O(M+K\log K)$。存储包含尚未物理清理的过期记录，不能把逻辑不可见误说成已经释放内存。

## 简单测试怎么写

把实现和测试保存成 `solution.py`，运行 `python3 solution.py`。用明确时刻直接验证 interval endpoints，无需等待真实时间；覆盖写入测试应跨过旧截止时间。

```python
cache = TTLCache()
cache.put('a', 'old', 2, 10)
assert cache.get('a', 11) == 'old'
assert cache.get('a', 12) is None
assert 'a' not in cache.entries
cache.put('a', 'new', 5, 12)
assert cache.expire(17) == ['a']
assert cache.get('a', 17) is None
cache.put('b', 'first', 2, 20)
cache.put('b', 'replacement', 10, 21)
assert cache.get('b', 22) == 'replacement'
assert cache.expire(22) == []
# 成功get不续期：截止31，到31即过期。
assert cache.get('b', 30) == 'replacement'
assert cache.get('b', 31) is None
cache.put('z', 1, 2, 40)
cache.put('c', 2, 2, 40)
assert cache.expire(42) == ['c', 'z']
cache.put('', 'x', 5, 50)
cache.put('', 'y', 0, 50)
assert cache.get('', 50) is None
assert cache.expire(100) == []
```

## 面试追问

**真实服务用什么时间？** 单进程测量经过时长通常用单调时钟，避免系统墙上时间被调整。持久化和跨机器期限需要额外定义时钟、重启与误差语义，不能直接持久化一个进程本地单调时间值。

**用最小堆主动清理怎么防止覆盖后误删？** 堆项包含键、deadline 和版本。弹出时对照字典当前版本，旧写入留下的堆项只跳过，不能删除覆盖后的新值。

**get 也要更新 TTL 呢？** 那是滑动有效期，需明确每次读按原 ttl 还是新值延期，并更新堆或版本。它不是本题默认行为，应先确认而非擅自实现。

---
id: p3a-perplexity-kv-store-with-timestamps-and-restore
section: design
order: 604
level: A
title: "Perplexity：历史 KV：时间戳操作与 restore"
quick: "每个 key 保存按时间排序的版本和删除标记，查询取最后一个不晚于目标时刻的版本；restore 要先约定是覆盖当前状态还是另开分支。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · kv-store-with-timestamps-and-restore"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/kv-store-with-timestamps-and-restore
    type: secondary
---

## 题目

实现一个带时间戳的 KV 存储，`set`、`get`、`delete` 都带时间参数，`get` 可以查询过去某一时刻的值。之后再加一个 `restore`，把数据恢复到某个历史状态。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

每个 key 保存一串按时间排序的版本，删除也写成一个版本（删除标记）。查询时找最后一个不晚于目标时刻的版本：是删除标记就返回空，否则返回它的值。只维护一个「当前值」字典是回答不了历史查询的。

`restore` 动手前要先和面试官讲清两件事：

- 恢复是覆盖当前状态，还是从历史点另开一个分支，让当前状态和恢复后的状态并存；
- 恢复之后的写入用什么时间，恢复这个动作本身算不算一次写入。

这份练习选择覆盖：`restore(now, backup_id)` 是发生在 `now` 的一次写入，把所有字段改成备份里的内容，`now` 之前的历史不变。备份和恢复的单位是「某一时刻的全部有效字段」。练习用 key/field 两级结构，单层 KV 把 `field` 固定为 `"value"` 即可。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `DB()`：所有操作都带时间参数 `t`。写操作（`set`、`delete`、`restore`）的时间全局单调不减，倒退时抛 `ValueError`；读操作（`get`、`scan`、`backup`）可以查询任意历史时刻。
- `set(t, key, field, value, ttl=None)`：写入值。`value` 不能是 `None`；给了 `ttl` 时必须为正，有效期是 $[t, t + ttl)$。同一时刻写入多次，以最后一次为准。
- `delete(t, key, field) -> bool`：从 `t` 起删除字段，返回删除前它是否有效。
- `get(t, key, field)`：返回 `t` 时刻的值；字段不存在、已删除或已过期时返回 `None`。
- `scan(t, key, prefix="")`：返回 `t` 时刻 `key` 下字段名以 `prefix` 开头的有效字段，格式是 `[(field, value)]`，按字段名升序。
- `backup(t) -> int`：保存 `t` 时刻所有有效字段的值和剩余 TTL，返回备份 id。
- `restore(now, backup_id)`：在写入时间 `now` 用备份覆盖当前全部状态，TTL 从 `now` 重新计时，`now` 之前的历史不变。备份 id 不存在时抛 `ValueError`。
- 存入和取出的值都做深复制。总版本数不超过 $10^4$。
- 单层的时间 KV 把 `field` 固定为 `"value"` 即可。

### 输入输出示例

```text
set(0, "a", "x", 7, ttl=5)
get(4, "a", "x")   -> 7
get(5, "a", "x")   -> None    # 5 不在 [0, 5) 内
backup(2)          -> 0       # 记下 x=7，剩余 TTL 为 3
restore(10, 0)
get(12, "a", "x")  -> 7
get(13, "a", "x")  -> None    # 恢复后的有效期是 [10, 13)
get(1, "a", "x")   -> 7       # restore 不改写更早的历史
```

### 解题思路与正确性

每个 `(key, field)` 维护两条一一对应的列表：写入时间，以及对应的版本 `(value, expires_at)`。写入时间单调不减，所以直接 append 就能保持有序。查询时用 `bisect_right` 找到最后一个写入时间不晚于 `t` 的版本；同一时刻有多次写入时，它自然落在最后一次上。

找到版本后只看这一个版本。如果它是删除标记，或者 `t` 已经到了 `expires_at`，就返回 `None`，不能再往前找更早的值，否则一个已过期的新值会让被它覆盖的旧值重新出现。

`backup` 不复制历史，只记下那一刻有效的值和剩余寿命 `expires_at - t`。`restore` 在 `now` 先给所有字段写删除标记，再按备份重新 `set`，过期时刻是 `now` 加剩余寿命。删除和写回都追加在 `now` 这一刻，同一时刻后写覆盖先写，所以 `now` 之后看到的是备份内容，`now` 之前看到的仍是原来的历史。

### 完整参考实现（Python 3）

```python
from bisect import bisect_right
from copy import deepcopy


class DB:
    """带历史版本、TTL 和备份恢复的 key/field 数据库。

    每个 (key, field) 按写入时间保存一串版本。版本的 value 为 None 表示删除标记，
    expires_at 为 None 表示永不过期。写入时间全局单调不减，查询可以回看任意历史时刻。
    """

    def __init__(self):
        self.times = {}     # (key, field) -> [写入时间, ...]，单调不减，供二分查找
        self.versions = {}  # (key, field) -> [(value, expires_at), ...]，与 times 一一对应
        self.clock = float("-inf")  # 最近一次写入的时间
        self.backups = []

    def _advance_clock(self, t):
        if t < self.clock:
            raise ValueError(f"write time {t} is earlier than last write {self.clock}")
        self.clock = t

    def _append(self, t, key, field, value, expires_at):
        self.times.setdefault((key, field), []).append(t)
        self.versions.setdefault((key, field), []).append((value, expires_at))

    def _at(self, t, key, field):
        """返回 t 时刻生效的 (value, expires_at)；不存在、已删除或已过期都返回 (None, None)。"""
        times = self.times.get((key, field), [])
        # 最后一个写入时间 <= t 的版本；同一时刻有多次写入时取最后一次
        index = bisect_right(times, t) - 1
        if index < 0:
            return None, None
        value, expires_at = self.versions[(key, field)][index]
        if expires_at is not None and t >= expires_at:
            return None, None  # 最新版本已过期时不能退回更早的旧值
        return value, expires_at

    def set(self, t, key, field, value, ttl=None):
        """在 t 时刻写入 value；有 ttl 时有效期是 [t, t + ttl)。"""
        if value is None:
            raise ValueError("value must not be None")
        if ttl is not None and ttl <= 0:
            raise ValueError(f"ttl must be positive, got {ttl}")
        self._advance_clock(t)
        expires_at = None if ttl is None else t + ttl
        self._append(t, key, field, deepcopy(value), expires_at)

    def delete(self, t, key, field):
        """在 t 时刻写入删除标记，返回删除前该字段是否有效。"""
        self._advance_clock(t)
        existed = self._at(t, key, field)[0] is not None
        self._append(t, key, field, None, None)
        return existed

    def get(self, t, key, field):
        return deepcopy(self._at(t, key, field)[0])

    def scan(self, t, key, prefix=""):
        """返回 t 时刻 key 下字段名以 prefix 开头的有效字段 [(field, value)]，按字段名升序。"""
        fields = sorted(f for k, f in self.times if k == key and f.startswith(prefix))
        result = []
        for field in fields:
            value = self.get(t, key, field)
            if value is not None:
                result.append((field, value))
        return result

    def backup(self, t):
        """保存 t 时刻所有有效字段的值和剩余 TTL，返回备份 id。备份只读，不推进时钟。"""
        snapshot = {}
        for key, field in self.times:
            value, expires_at = self._at(t, key, field)
            if value is None:
                continue
            remaining = None if expires_at is None else expires_at - t
            snapshot[(key, field)] = (deepcopy(value), remaining)
        self.backups.append(snapshot)
        return len(self.backups) - 1

    def restore(self, now, backup_id):
        """在 now 时刻用备份覆盖当前全部状态。更早的历史不变，TTL 从 now 重新计时。"""
        if not isinstance(backup_id, int) or not 0 <= backup_id < len(self.backups):
            raise ValueError(f"unknown backup id: {backup_id!r}")
        self._advance_clock(now)
        for key, field in list(self.times):
            self.delete(now, key, field)
        # 同一时刻后写覆盖先写，所以先删全部、再写回备份内容
        for (key, field), (value, remaining) in self.backups[backup_id].items():
            self.set(now, key, field, value, remaining)
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# TTL 有效期是左闭右开区间 [0, 5)
db = DB()
db.set(0, "a", "x", 7, 5)
backup_id = db.backup(2)
assert db.get(4, "a", "x") == 7
assert db.get(5, "a", "x") is None

# 备份时剩余 3，恢复后从 10 重新计时，有效到 13 之前
db.restore(10, backup_id)
assert db.get(12, "a", "x") == 7
assert db.get(13, "a", "x") is None

# restore 不改更早的历史
assert db.get(1, "a", "x") == 7

# 同一时刻后写覆盖先写
db.set(14, "a", "z", 8)
db.set(14, "a", "z", 9)
assert db.scan(14, "a") == [("z", 9)]

# 删除只影响删除时刻及以后
assert db.delete(15, "a", "z") is True
assert db.get(14, "a", "z") == 9
assert db.get(15, "a", "z") is None
assert db.delete(16, "a", "z") is False

# scan 按字段名升序并按前缀过滤
db.set(20, "u", "task-2", "b")
db.set(20, "u", "task-1", "a")
db.set(20, "u", "note", "c")
assert db.scan(20, "u", "task") == [("task-1", "a"), ("task-2", "b")]

# 存进去的可变值被深复制，外部修改不影响历史
payload = {"n": 1}
db.set(21, "u", "obj", payload)
payload["n"] = 2
assert db.get(21, "u", "obj") == {"n": 1}

expect_value_error(db.set, 19, "a", "x", 1)      # 写入时间倒退
expect_value_error(db.set, 22, "a", "x", 1, 0)   # ttl 必须为正
expect_value_error(db.set, 22, "a", "x", None)   # None 留给删除标记
expect_value_error(db.restore, 22, 99)           # 不存在的备份 id
expect_value_error(db.restore, 22, -1)           # 负数 id 不能当成「最后一个」
```

### 复杂度与追问

设某个字段的版本数为 v，字段总数为 F，某个 key 下的字段数为 $F_k$。`set` 和 `delete` 均摊 O(1)（`delete` 还要一次 O(log v) 的查询），`get` 是 O(log v)。`scan` 要先扫一遍所有字段筛出这个 key，再排序和逐个查询，共 $O(F + F_k \log F_k + F_k \log v)$。`backup` 和 `restore` 都是 O(F log v)。

- 追问「要另开分支怎么办」：把版本历史改成以版本 id 为节点的链，每个分支记录自己的最新版本 id；恢复就是新建一个分支，指向备份时刻的版本，不复制数据。
- 追问「能不能直接恢复到时刻 t，而不是先备份」：可以，`restore` 时直接用 `get(t, ...)` 读出每个字段在 t 的值和剩余 TTL，效果等于先在 t 做一次 `backup`。

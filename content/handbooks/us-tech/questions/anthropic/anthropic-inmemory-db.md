---
id: anthropic-inmemory-db
section: anthropic
order: 1
level: A
title: Anthropic：实现带 TTL 的内存数据库，后续怎么加备份和并发？
quick: >-
  我会从第一层就让接口带时间戳，读时检查 TTL，再用过期堆主动回收。备份保存过滤后的一致快照，值做深拷贝、TTL
  存剩余时长，恢复时从当前时间重新计时；需要历史查询时还要保留版本。
tags:
  - 完整编程练习
  - Anthropic
  - Coding
  - TTL
  - Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Anthropic interview questions (IGotAnOffer)
    url: 'https://igotanoffer.com/en/advice/anthropic-interview-questions'
    type: secondary
  - title: Anthropic SDE OA — Memory Database and Bank System
    url: 'https://programhelp.net/en/oa/anthropic-sde-oa-interview-guide/'
    type: secondary
---

## 题目描述

实现一个支持历史查询的内存数据库。每个记录由 key 和 field 两级标识，字段可以带生存时间 TTL。除了读写与扫描，还要保存备份，并在将来的时刻恢复备份；恢复不能改写已有的历史查询结果。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `DB.set(t, key, field, value, ttl=None)`：写入一个字段。`value` 不能是 `None`，`ttl` 给出时为正。带 TTL 的值在 $[t, t+\text{ttl})$ 内有效。
- `DB.delete(t, key, field) -> bool`：删除字段，返回删除前它在时刻 `t` 是否存在。
- `DB.get(t, key, field)`：返回时刻 `t` 的值，不存在、已删除或已过期时返回 `None`。查询可以回看任意历史时刻。
- `DB.scan(t, key, prefix="") -> list[(field, value)]`：返回时刻 `t` 该 key 下以 `prefix` 开头、仍然有效的字段，按字段名升序。
- `DB.backup(t) -> int`：保存时刻 `t` 所有有效字段的快照（值深拷贝，TTL 存剩余时长），返回备份 id。
- `DB.restore(now, backup_id)`：在时刻 `now` 用快照覆盖当前全部状态，TTL 从 `now` 重新起算；更早的历史不变。
- 写操作（`set`、`delete`、`restore`）的时间全局单调不减，假定不会倒退；同一时刻后写的覆盖先写的。版本总数不超过 $10^4$。

### 示例

```text
set(0, "a", "x", 7, ttl=5)
get(4, "a", "x")  -> 7
get(5, "a", "x")  -> None      # 有效期是 [0, 5)
backup(2)         -> 0         # 剩余 TTL = 3
restore(10, 0)
get(12, "a", "x") -> 7         # 从 10 起再活 3
get(13, "a", "x") -> None
get(1, "a", "x")  -> 7         # 历史不受 restore 影响
```

## 解题思路与参考答案

我会让所有操作共用显式时间戳，按版本读取字段，再把备份定义成某一时刻有效状态的深拷贝。比如字段在备份时还剩一段 TTL，恢复后就从恢复时间重新计算这段时长，过去的查询结果保持不变。

## 完整编程练习（手册重构版）

> 来源网站只披露了题型（见下文「真题记录」）。下面的接口、约束和测试是手册补的练习约定。Python 3，只用标准库。

### 题面、接口与约束

- `DB.set(t, key, field, value, ttl=None)`：写入一个字段。`value` 不能是 `None`（内部用它表示删除），`ttl` 给出时必须为正，否则抛 `ValueError`。带 TTL 的值在 $[t, t+\text{ttl})$ 内有效。
- `DB.delete(t, key, field) -> bool`：删除字段，返回删除前它在时刻 `t` 是否存在。
- `DB.get(t, key, field)`：返回时刻 `t` 的值，不存在、已删除或已过期时返回 `None`。查询可以回看任意历史时刻。
- `DB.scan(t, key, prefix="") -> list[(field, value)]`：返回时刻 `t` 该 key 下以 `prefix` 开头、仍然有效的字段，按字段名升序。
- `DB.backup(t) -> int`：保存时刻 `t` 所有有效字段的快照（值深拷贝，TTL 存剩余时长），返回备份 id。
- `DB.restore(now, backup_id)`：在时刻 `now` 用快照覆盖当前全部状态，TTL 从 `now` 重新起算；更早的历史不变。
- 写操作（`set`、`delete`、`restore`）的时间全局单调不减，倒退时抛 `ValueError`；同一时刻后写的覆盖先写的。版本总数不超过 $10^4$。
- 不同面经的分层：任务管理题可以把 user 当 key、task id 当 field；只有一个值的时间 KV 题固定 `field="value"`。

### 输入输出示例

```text
set(0, "a", "x", 7, ttl=5)
get(4, "a", "x")  -> 7
get(5, "a", "x")  -> None      # 有效期是 [0, 5)
backup(2)         -> 0         # 剩余 TTL = 3
restore(10, 0)
get(12, "a", "x") -> 7         # 从 10 起再活 3
get(13, "a", "x") -> None
get(1, "a", "x")  -> 7         # 历史不受 restore 影响
```

### 解题思路与正确性

每个 `(key, field)` 存一个按时间追加的版本列表，版本是 `(写入时间, 值, 过期时间)`，删除写一个值为 `None` 的墓碑。查询时刻 `t` 时，从后往前找最后一个写入时间不晚于 `t` 的版本：这个版本决定结果。如果它已过期或是墓碑，就返回 `None`，不能再往前退回更旧的值，否则一个被删掉或过期的字段会「复活」。

`restore` 不改历史，而是在 `now` 追加一轮写入：先给所有现有字段写墓碑，再把快照里的字段逐个写回，TTL 用快照存的剩余时长。因为是追加，`now` 之前的查询结果都不变。快照在备份和恢复时各深拷贝一次，之后改动调用方手里的对象不会影响数据库。

### 完整参考实现（Python 3）

```python
from copy import deepcopy
from typing import Any, NamedTuple, Optional


class Version(NamedTuple):
    time: int
    value: Any  # None 表示删除墓碑
    expires_at: Optional[int]  # None 表示永不过期


class DB:
    """带 TTL、历史查询和备份恢复的内存数据库。每个 (key, field) 保存按时间追加的版本列表。"""

    def __init__(self):
        self.log = {}  # (key, field) -> [Version, ...]，按写入时间递增
        self.clock = float("-inf")
        self.backups = []  # backup id -> {(key, field): (value, 剩余 ttl 或 None)}

    def _advance(self, t):
        if t < self.clock:
            raise ValueError(f"write time went backwards: {t} < {self.clock}")
        self.clock = t

    def _append(self, t, key, field, value, expires_at):
        self.log.setdefault((key, field), []).append(Version(t, value, expires_at))

    def _at(self, t, key, field):
        """返回时刻 t 生效的 (value, expires_at)；不存在、已删除或已过期时 value 为 None。"""
        for version in reversed(self.log.get((key, field), [])):
            if version.time <= t:
                if version.expires_at is None or t < version.expires_at:
                    return version.value, version.expires_at
                return None, None  # 最新版本已过期，不退回更旧的值
        return None, None

    def set(self, t, key, field, value, ttl=None):
        if value is None:
            raise ValueError("value must not be None")
        if ttl is not None and ttl <= 0:
            raise ValueError(f"ttl must be positive, got {ttl}")
        self._advance(t)
        expires_at = None if ttl is None else t + ttl
        self._append(t, key, field, deepcopy(value), expires_at)

    def delete(self, t, key, field):
        """写墓碑；返回删除前该字段在时刻 t 是否存在。"""
        existed = self.get(t, key, field) is not None
        self._advance(t)
        self._append(t, key, field, None, None)
        return existed

    def get(self, t, key, field):
        return deepcopy(self._at(t, key, field)[0])

    def scan(self, t, key, prefix=""):
        """时刻 t 该 key 下以 prefix 开头的有效字段，按字段名升序。"""
        result = []
        for log_key, field in sorted(self.log):
            if log_key != key or not field.startswith(prefix):
                continue
            value = self.get(t, key, field)
            if value is not None:
                result.append((field, value))
        return result

    def backup(self, t):
        """保存时刻 t 的有效字段，TTL 存剩余时长。返回备份 id。"""
        snapshot = {}
        for key, field in self.log:
            value, expires_at = self._at(t, key, field)
            if value is not None:
                remaining = None if expires_at is None else expires_at - t
                snapshot[(key, field)] = (deepcopy(value), remaining)
        self.backups.append(snapshot)
        return len(self.backups) - 1

    def restore(self, now, backup_id):
        """在时刻 now 用快照整体替换当前状态；只追加版本，不改历史。"""
        snapshot = deepcopy(self.backups[backup_id])
        self._advance(now)
        for key, field in list(self.log):
            self.delete(now, key, field)
        for (key, field), (value, remaining) in snapshot.items():
            self.set(now, key, field, value, remaining)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert db.get(4, "a", "x") == 7` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


db = DB()
db.set(0, "a", "x", 7, 5)
backup_id = db.backup(2)

# TTL 有效期是 [0, 5)
assert db.get(4, "a", "x") == 7
assert db.get(5, "a", "x") is None

# restore 后剩余 TTL 从 now 重新起算
db.restore(10, backup_id)
assert db.get(12, "a", "x") == 7
assert db.get(13, "a", "x") is None

# restore 不改历史
assert db.get(1, "a", "x") == 7

# 同一时刻后写覆盖先写
db.set(14, "a", "z", 8)
db.set(14, "a", "z", 9)
assert db.scan(14, "a") == [("z", 9)]

# 删除后历史仍可查，当前返回 None
assert db.delete(15, "a", "z") is True
assert db.get(14, "a", "z") == 9
assert db.get(15, "a", "z") is None
assert db.delete(15, "a", "z") is False

# scan 按字段名升序，支持前缀
db.set(16, "u", "task-2", "b")
db.set(16, "u", "task-1", "a")
db.set(16, "u", "note", "n")
assert db.scan(16, "u", "task-") == [("task-1", "a"), ("task-2", "b")]
assert [field for field, _ in db.scan(16, "u")] == ["note", "task-1", "task-2"]

# 备份深拷贝：之后修改原对象不影响快照
items = [1]
db.set(17, "m", "list", items)
items.append(2)
snapshot_id = db.backup(17)
db.set(18, "m", "list", [99])
db.restore(19, snapshot_id)
assert db.get(19, "m", "list") == [1]

# 非法输入：时间倒退、非正 TTL、None 值
expect_error(ValueError, db.set, 0, "a", "x", 1)
expect_error(ValueError, db.set, 20, "a", "x", 1, 0)
expect_error(ValueError, db.set, 20, "a", "x", None)
```

### 复杂度与追问

设某个字段的版本数为 $v$、字段总数为 $F$。`get` 从后往前扫是 $O(v)$；版本按时间有序，可以用二分降到 $O(\log v)$。`scan` 是 $O(F\log F+Fv)$，`backup` 是 $O(Fv)$，`restore` 在此基础上再为每个字段追加常数个版本。

- 追问「内存会一直涨」：历史查询要求保留旧版本，不能直接丢。如果题目允许只查最近一段时间，可以按时间窗口压缩，或者只保留每个字段最后一个早于窗口的版本。
- 追问「快照里的可变值」：必须深拷贝，否则调用方改了自己手里的列表，快照也跟着变（测试里的 `items` 一例）。

## 真题记录

- 公司：Anthropic
- 岗位：SWE / 部分 RE 的 CodeSignal 或现场编码
- 来源：IGotAnOffer 汇总的高频题；OA 拆解文把「Memory Database（TTL + backup/restore）」和「Bank System」列为分层解锁的题
- 形态：90 分钟、4 层，前一层单测不过，后一层不开放

难点在层数和时钟，不在单层算法。如果第一层把 `get/set` 写成不带时间参数的 dict，到第三层加 TTL 时就只能推倒重来。

## TTL 和快照怎么衔接

值保存成 `(value, expire_at | None)`。所有读路径都用同一个 `now`：OA 里的时间是命令自带的整数时间戳，不要用墙上时钟，否则单测没法复现。

过期策略有两种：

- **惰性删除：** 在 `get` / `scan` 时丢掉过期的键，写路径简单。
- **主动回收：** 用 min-heap 存 `(expire_at, key)`，推进时间时弹出到期的键。这样能避免「只写不读，内存被过期键撑满」。

生产系统两种都要。面试里至少实现惰性删除，并说出主动回收。过期堆要处理「同一个 key 被续期」：堆里会留着旧的时间戳，弹出时核对当前的 `expire_at`，对不上就跳过。

备份时要过滤过期字段，再深拷贝状态，浅层的 `dict.copy()` 还不够。具体约定有几处要先确定：

1. 按当前 `now` 丢掉过期的键。
2. 拷贝 value，可变对象要 deepcopy。
3. restore 是覆盖整个命名空间还是 merge，由题目规定，默认整库替换。
4. 快照里存绝对过期时间还是剩余 TTL？存绝对时间更简单，但如果 restore 发生在时间已经推进之后，绝对时间可能让整份备份一恢复就全部过期。存剩余 TTL 更合理，restore 时 `expire_at = now + remaining`，参考实现就是这么做的。

因此恢复前先确认题目要保留的是绝对截止时间还是剩余寿命，再写 `self.data = snapshot` 这类赋值。

## 后续层次和并发

Bank 变体（开户、转账、合并、cashback）和 DB 变体有一个共同点：余额和版本号都放在记录里，操作返回成功或失败，不要抛出一个只更新了一半的异常。转账时先检查两个账户都存在、金额非负、源账户余额足够，再同时改两处。合并账户要定义谁的主键留下、历史 cashback 怎么合并。

并发是现场常见的 follow-up，单线程的 OA 不考锁。可以每个键一把锁，再规定全局加锁顺序（比如按 account id 排序）来避免 AB/BA 死锁。`setAll` 或全表 backup 需要停写，或者用 copy-on-write 加版本号，不能在遍历过程中被 `set` 改掉。

## 追问

**TTL 用 Redis 那种 expire 命令模型，还是滑动窗口？**
先实现绝对过期。滑动 TTL 每次 get 都要续期，堆的更新更麻烦，留作 follow-up。

**为什么不每秒扫一遍全表？**
每次唤醒都是 $O(n)$。过期堆插入是 $O(\log n)$，每次只弹出到期的 $k$ 个键，代价 $O(k\log n)$。

**和计算机使用 / 工具超时有什么关系？**
是同一类状态机：每个资源有 deadline，过期后的行为必须确定，不能「偶尔读到旧值」。工具超时见 computer-use 章。

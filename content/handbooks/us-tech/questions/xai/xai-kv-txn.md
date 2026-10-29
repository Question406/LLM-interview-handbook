---
id: xai-kv-txn
section: xai
order: 1
level: A
title: xAI：内存 KV 怎么加事务？15 分钟屏幕上的 race 怎么找？
quick: >-
  我会在 begin 固定快照，把写入留在事务缓冲；commit 在锁内验证读写集版本，全部通过才原子发布，冲突就 abort。BankAccount 的
  lost update 同样要锁住整个读改写过程：两个线程都读到 100、都写成 110，就会丢掉一次存款。
tags:
  - 完整编程练习
  - xAI
  - Concurrency
  - KV Store
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: xAI Interview Question Bank (1Point3Acres)
    url: 'https://www.1point3acres.com/interview/problems/company/xai'
    type: secondary
  - title: xAI interview questions from candidate reports
    url: 'https://aceoffer.app/interviews/xai'
    type: secondary
---

## 题目描述

实现线程安全数据库的乐观事务：每个事务读自己的固定快照及本地写入，提交时检测它访问过的键是否发生并发变更。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `Database.begin() -> Transaction`：线程安全，开始一个事务并固定 begin 时的快照。
- `Transaction.get(key)`：读快照，能读到自己的写入；key 不存在返回 `None`。
- `Transaction.put(key, value)`、`Transaction.delete(key)`：写入只进事务自己的缓冲区。值限定为不可变字符串；删除不存在的 key 合法。
- `Transaction.commit() -> bool`：所有读过或写过的 key 自 begin 后都没被别人改过，就原子地应用全部写入并返回 `True`；否则返回 `False`，什么都不写。
- `Transaction.rollback()`：丢弃写入。提交或回滚后的事务不能再用，再调用抛 `RuntimeError`。
- 约束：事务之间不嵌套，每个事务只由一个线程调用；数据库本身可以被多个线程同时调用。这是针对固定 key 读写的乐观并发控制，不提供范围查询，也不是完整的 MVCC。

### 输入输出示例

```text
初始 a = "1"
T1 = begin(); T2 = begin()
T1.put("a", "2"); T1.commit()     -> True
T2.get("a")                       -> "1"     # T2 仍读 begin 时的快照
T2.put("b", "3"); T2.commit()     -> False   # T2 读过的 a 已被 T1 改掉
```

## 解题思路与参考答案

我会用快照加读写集版本验证实现事务，提交时在同一把锁内完成检查和发布。比如两个事务都准备改 `a`，先提交的会改变版本，后提交的必须 abort，不能覆盖它。BankAccount 的竞态也是共享读改写没有被原子保护。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3，只用标准库。

### 题面、接口与约束

- `Database.begin() -> Transaction`：线程安全，开始一个事务并固定 begin 时的快照。
- `Transaction.get(key)`：读快照，能读到自己的写入；key 不存在返回 `None`。
- `Transaction.put(key, value)`、`Transaction.delete(key)`：写入只进事务自己的缓冲区。值限定为不可变字符串，否则抛 `ValueError`；删除不存在的 key 合法。
- `Transaction.commit() -> bool`：所有读过或写过的 key 自 begin 后都没被别人改过，就原子地应用全部写入并返回 `True`；否则返回 `False`，什么都不写。
- `Transaction.rollback()`：丢弃写入。提交或回滚后的事务不能再用，再调用抛 `RuntimeError`。
- 约束：事务之间不嵌套，每个事务只由一个线程调用；数据库本身可以被多个线程同时调用。这是针对固定 key 读写的乐观并发控制，不提供范围查询，也不是完整的 MVCC。

### 输入输出示例

```text
初始 a = "1"
T1 = begin(); T2 = begin()
T1.put("a", "2"); T1.commit()     -> True
T2.get("a")                       -> "1"     # T2 仍读 begin 时的快照
T2.put("b", "3"); T2.commit()     -> False   # T2 读过的 a 已被 T1 改掉
```

### 解题思路与正确性

`begin` 在锁内复制数据和版本表，所以快照是某一时刻的一致状态。事务读快照、写缓冲区；`commit` 在同一把锁里先验证、再应用，验证和写入之间不会插进别的提交，其他事务也看不到提交了一半的状态。

版本表在 key 被删除后仍保留它的版本号。这样即使一个 key 在事务期间被创建又删除（ABA），版本号也已经变了，冲突照样能发现。

验证范围包括读集，不只写集，所以固定 key 上的 write skew 也会被拦下：两个事务各读对方要写的 key 时，后提交的那个会失败。这比只检查写写冲突的 snapshot isolation 更严格。

### 完整参考实现（Python 3）

```python
from threading import RLock


class Database:
    """线程安全的内存 KV，事务用乐观并发控制：begin 拍快照，commit 时验证版本。"""

    def __init__(self):
        self.data = {}  # key -> 当前值（只存字符串）
        self.versions = {}  # key -> 最后一次提交写它的版本号；删除后保留，用来发现 ABA
        self.clock = 0
        self.lock = RLock()

    def begin(self):
        with self.lock:
            return Transaction(self, self.data.copy(), self.versions.copy())


class Transaction:
    """单线程使用的事务：读快照、缓冲写入，提交或回滚后不能再用。"""

    def __init__(self, db, snapshot, versions):
        self.db = db
        self.snapshot = snapshot  # begin 时的数据
        self.versions = versions  # begin 时的版本表
        self.reads = set()
        self.writes = {}  # key -> 新值；None 表示删除
        self.closed = False

    def _check_open(self):
        if self.closed:
            raise RuntimeError("transaction already committed or rolled back")

    def get(self, key):
        """先看自己的写缓冲，再看快照；不存在返回 None。"""
        self._check_open()
        self.reads.add(key)
        return self.writes.get(key, self.snapshot.get(key))

    def put(self, key, value):
        self._check_open()
        if not isinstance(value, str):
            raise ValueError(f"values must be strings, got {type(value).__name__}")
        self.writes[key] = value

    def delete(self, key):
        """删除不存在的 key 也合法。"""
        self._check_open()
        self.writes[key] = None

    def commit(self):
        """读过或写过的 key 自 begin 后都没被别人提交过，才原子地应用全部写入。"""
        self._check_open()
        with self.db.lock:
            self.closed = True
            touched = self.reads | self.writes.keys()
            if any(
                self.db.versions.get(key, 0) != self.versions.get(key, 0)
                for key in touched
            ):
                return False
            if self.writes:
                self.db.clock += 1
                for key, value in self.writes.items():
                    if value is None:
                        self.db.data.pop(key, None)
                    else:
                        self.db.data[key] = value
                    self.db.versions[key] = self.db.clock
            return True

    def rollback(self):
        self._check_open()
        self.closed = True
        self.writes.clear()
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert setup.commit()` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"{fn.__name__} should raise {error_type.__name__}")


db = Database()
setup = db.begin()
setup.put("a", "1")
assert setup.commit()

# T1、T2 同时 begin：T1 改 a 并提交；T2 仍读到旧快照，但它读过 a，提交必须失败
first, second = db.begin(), db.begin()
first.put("a", "2")
assert first.get("a") == "2"  # 读到自己的写入
assert first.commit()
assert second.get("a") == "1"
second.put("b", "3")
assert not second.commit()
assert db.begin().get("b") is None  # 失败的事务不留下任何写入

# 不相交的 key：两个事务都能提交
first, second = db.begin(), db.begin()
first.put("c", "x")
second.put("d", "y")
assert first.commit()
assert second.commit()

# ABA：key 在 old 读过之后被创建又删除，版本号变了，old 仍要冲突
old = db.begin()
assert old.get("ghost") is None
creator = db.begin()
creator.put("ghost", "x")
assert creator.commit()
deleter = db.begin()
deleter.delete("ghost")
assert deleter.commit()
assert not old.commit()

# rollback 丢弃写入；回滚后的事务不能再用
txn = db.begin()
txn.delete("a")
txn.rollback()
assert db.begin().get("a") == "2"
expect_error(RuntimeError, txn.get, "a")

# 删除不存在的 key 合法；值必须是字符串
txn = db.begin()
txn.delete("never-existed")
expect_error(ValueError, txn.put, "a", 3)
assert txn.commit()

# 两个线程同时写同一个 key：恰好一个提交成功
barrier = Barrier(2)


def compete(value):
    txn = db.begin()
    txn.put("same", value)
    barrier.wait()
    return txn.commit()


with ThreadPoolExecutor(2) as pool:
    assert sum(pool.map(compete, ["x", "y"])) == 1
```

### 复杂度与追问

设当前 key 数为 $N$、版本表大小为 $V$（含已删除 key 的版本）。`begin` 是 $O(N+V)$；`get`、`put`、`delete` 均摊 $O(1)$；`commit` 是 $O(\text{读集}+\text{写集})$。每个事务占 $O(N+V+\text{读写集})$ 空间。

- 追问「版本表一直变大」：已删除 key 的版本是墓碑，长期运行要在没有活跃快照还引用它时回收。
- 追问「库很大，复制快照太贵」：改用每个 key 一条版本链，begin 只记一个时间戳，读的时候找不晚于它的最新版本。
- 原卡里的 BankAccount 变体见 `xai-me-live-debug`，那张卡也有完整实现。

## 真题记录

- 公司：xAI
- 来源：一亩三分地 xAI 题库（2026-08 更新）列出了 in-memory KV with transactions 和 BankAccount race 两道 15 分钟视频面题目；AceOffer 汇总了 80 多份报告，KV + 事务和 race 都是高频题。
- 风格：题目短、贴近系统，要你当场改对。算法技巧不是重点。

这题和 Anthropic 的内存数据库（`anthropic-inmemory-db`）是近亲，但 xAI 更关注并发正确性。TTL 不是主线，事务和 race 才是。

面试时间怎么分配、面试官迟到时的 90 秒自我介绍、要不要先和 coordinator 确认有编码环节，见 `xai-screen-15min`。这道 race 题是可选的附加题，不是 PhD 候选人的开场题。为什么选 xAI 的产品背景见 `xai-spacexai-now`。

## KV + 事务

单个对象的 `get` / `put` 用一把锁或 concurrent map 就够了。加事务就要先说清隔离级别。本卡用固定 key 的读写集版本验证，比只检测写写冲突的 snapshot isolation 更严格。参考实现的步骤是：

1. `begin`：在锁内拷贝当前数据和每个 key 的版本号，作为这个事务的快照。
2. `get` / `put` / `delete`：读快照，写进自己的写缓冲区，不直接改全局数据；同时记下读集。
3. `commit`：在全局锁内检查读集和写集里每个 key 的版本有没有被别人改过，有就 abort；没有就一次性应用写集，并给这些 key 升版本。

如果想提高并发度，可以把全局锁换成每个 key 一把锁，commit 时对读写集按 key 排序后依次加锁，避免死锁。

先把固定 key 的读写集、冲突检测和 commit 原子性实现清楚，再讨论版本链等优化。单测要能演示「`T1` 和 `T2` 都写 `a`，必有一个 abort」。

同一个题库里还出现过 rollback 和可恢复迭代器：迭代到一半要能从 cursor 恢复。这类题难在状态机，不在算法。cursor 要做成 `(key, version)`，不要用 list 下标这种插入数据后就会失效的位置。

## 15 分钟 BankAccount race

公开的题目预览是一段 `deposit`：读余额、sleep、再写回。这是经典的 lost update。排查思路：

- 共享的可变状态是 `balance`。
- 临界区是「读、改、写」这一整段，sleep 只是把出错的时间窗口拉大。
- 修法：用 `synchronized` / mutex 包住整段，或者用 `compareAndSet` 循环。在 Java 里只给方法加 `synchronized` 还要留意：follow-up 可能不允许改原类，要求你 subclass 或 wrap。那是在外面包一层锁的装饰器，而不是再写一个 balance 字段。

现场要用数据竞争的语言讲：两个线程都读到 100，都写回 110，丢了一次存款。不要只说「加个锁」，要说清楚锁住哪几行。

Rate limiter 和令牌桶（token bucket）是相邻题，也可以先画共享计数器和时间窗口，再谈分布式。另外，xAI 的报告里还出现过「能不能接受每周 60–100 小时、在 Palo Alto 坐班」，这是文化匹配问题，按自己的实际情况回答。

## 追问

**为什么不直接用一把全局大锁做 serializable？**
能写对，但 throughput 差。面试里先保证正确，再提高并发度。

**和训练 checkpoint 有什么关系？**
是同一类问题：版本要原子地变得可见。权重文件要么完整可见，要么不可见，不能出现半份。

**会追问 Go / Rust 吗？**
政府相关岗位的报告里出现过。普通 SWE 岗以简历上的语言为准。

## 相关题

- [[p3a-xai-transactional-key-value-store]]：同为 xAI 事务 KV，但契约是嵌套 begin / commit / rollback 的栈，不做并发冲突检测。
- [[xai-lru-cache]]：缓存题，和本题的衔接点是缓存里只能放已提交的版本。
- [[p3a-xai-multithreaded-bank-account-bug-hunt]]：本卡 BankAccount race 一节的完整编程练习，还要求用包装类修竞态。
- [[xai-me-live-debug]]：同一道 race 题的面经版，讲在 CoderPad 上一路改到测试通过。

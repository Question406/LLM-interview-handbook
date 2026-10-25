---
id: p3a-microsoft-kv-store-with-snapshot
section: microsoft
order: 604
level: A
title: "Microsoft AI / Copilot：快照 KV：基于历史版本分支写入"
quick: "我会先用深拷贝保证快照不可变、fork 后相互独立，明确快照是否包含未提交改动。数据大了再改成复制写入或持久结构，分支读取沿父版本找，删除用 tombstone，避免祖先的旧值重新出现。"
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · kv-store-with-snapshot"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/kv-store-with-snapshot
    type: secondary
---

## 题目描述

实现内存 KV 存储，支持嵌套事务、只读快照与从快照创建独立分支。事务的提交和回滚只作用于最内层；读取可变对象时不能让调用者通过返回值绕过存储接口改写内部状态。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `KV(data=None)`：可选初始数据，构造时深拷贝一份。
- `get(key)`：返回当前可见的值，不存在返回 `None`。返回的是深拷贝。
- `set(key, value)`：值必须可 JSON 序列化且不能是 `None`（`None` 留给「不存在」）。
- `delete(key) -> bool`：删掉返回 `True`，键本来不存在返回 `False`。
- `begin()` / `commit()` / `rollback()`：事务可以嵌套。`commit` 只把最内层合并进父层，`rollback` 只丢弃最内层；调用 commit/rollback 时假定已有打开的事务。
- `snapshot() -> int`：记录当前可见数据，返回快照 id。快照之后的写入不影响它。
- `fork(snapshot_id) -> KV`：从快照创建独立的新实例；假定 id 存在。
- 最多 $10^4$ 次操作。快照和分支的后续修改彼此隔离。

### 示例

```text
set("a", 1); begin(); set("a", 2); get("a")   -> 2
rollback(); get("a")                           -> 1
id = snapshot(); b = fork(id); b.set("a", 3)
get("a")                                       -> 1
b.get("a")                                     -> 3
```

## 解题思路与参考答案

我会先保证快照和分支互不影响，再优化复制成本。例如分支删除一个键，读取时就不能继续从父版本找回旧值；完整副本可以直接删键，共享版本则要写 tombstone。

## 题目

实现一个支持快照的 KV 存储：可以随时生成快照，按 snapshot id 读取当时的数据，并从某个快照分出一个新分支继续写入，分支上的写入不影响原数据和其他快照。

> 来源：一亩三分地 Microsoft AI / Copilot 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

核心要求是快照不可变：拍下之后，不管原实例还是分支怎么写，快照里的内容都不能变。最简单的做法是拍快照时整份深拷贝，`fork` 再从这份拷贝建一个独立实例。

数据量大时整份复制太贵，常见的改进是复制写入或持久数据结构，让各个版本共享没改过的部分。这时版本之间形成一棵树：每个版本记住父版本，读一个键时沿着本分支往祖先找，而不是按时间戳查全局历史，因为不同分支在同一时刻可能有不同的值。删除也要写 tombstone，否则分支上删掉的键会从祖先版本里「复活」。

动手前可以和面试官确认：快照是否包含未提交事务里的改动、snapshot id 是全局的还是每个实例各自编号、是否需要直接按 snapshot id 读而不先 `fork`。

这份练习复用 xAI 嵌套事务题的 `KV`，所以也保留了事务接口。下面先用整份复制把语义讲清楚，版本共享作为后续优化。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `KV(data=None)`：可选初始数据，构造时深拷贝一份。
- `get(key)`：返回当前可见的值，不存在返回 `None`。返回的是深拷贝。
- `set(key, value)`：值必须可 JSON 序列化且不能是 `None`（`None` 留给「不存在」），否则抛 `ValueError`。
- `delete(key) -> bool`：删掉返回 `True`，键本来不存在返回 `False`。
- `begin()` / `commit()` / `rollback()`：事务可以嵌套。`commit` 只把最内层合并进父层，`rollback` 只丢弃最内层；没有打开的事务时两者都抛 `ValueError`。
- `snapshot() -> int`：记录当前可见数据，返回快照 id。快照之后的写入不影响它。
- `fork(snapshot_id) -> KV`：从快照创建独立的新实例；id 不存在抛 `ValueError`。
- 最多 $10^4$ 次操作。这份练习用整份复制换取清楚的语义，不是高性能 MVCC。

### 输入输出示例

```text
set("a", 1); begin(); set("a", 2); get("a")   -> 2
rollback(); get("a")                           -> 1
id = snapshot(); b = fork(id); b.set("a", 3)
get("a")                                       -> 1
b.get("a")                                     -> 3
```

### 解题思路与正确性

`layers[0]` 是已提交数据，每次 `begin` 把当前顶层深拷贝一份压栈，之后的读写只碰顶层。`commit` 弹出顶层并用它替换父层，因为顶层本来就是「父层 + 本事务改动」的完整结果；`rollback` 直接弹出，父层原封不动。删除就是从顶层字典里移除，不需要 tombstone，因为每层都是完整副本，不会从下层「漏」出旧值。

快照和 `get` 都用深拷贝，所以调用方拿到的列表、字典和存储里的对象不共享引用，改了也不会回写。`snapshot` 记录的是顶层，也就是包含未提交改动的视图；如果面试官希望快照只看已提交数据，改成拷贝 `layers[0]` 即可。

### 完整参考实现（Python 3）

```python
from copy import deepcopy


class KV:
    """支持嵌套事务和快照分支的 KV。

    layers[0] 是已提交数据，之后每一层是一个打开的事务，保存进入该事务时的完整工作副本。
    所有读写都只看最顶层。
    """

    def __init__(self, data=None):
        self.layers = [deepcopy(data or {})]
        self.snapshots = []

    def _require_transaction(self):
        if len(self.layers) == 1:
            raise ValueError("no active transaction")

    def get(self, key):
        """不存在返回 None；返回深拷贝，调用方改返回值不会影响存储。"""
        return deepcopy(self.layers[-1].get(key))

    def set(self, key, value):
        if value is None:
            raise ValueError("None is reserved for missing keys")
        self.layers[-1][key] = deepcopy(value)

    def delete(self, key):
        """删除成功返回 True，键本来不存在返回 False。"""
        return self.layers[-1].pop(key, None) is not None

    def begin(self):
        self.layers.append(deepcopy(self.layers[-1]))

    def commit(self):
        """只提交最内层事务：用它的工作副本替换父层。"""
        self._require_transaction()
        committed = self.layers.pop()
        self.layers[-1] = committed

    def rollback(self):
        """丢弃最内层事务的全部改动。"""
        self._require_transaction()
        self.layers.pop()

    def snapshot(self):
        """记录当前可见数据（含未提交事务的改动），返回快照 id。"""
        self.snapshots.append(deepcopy(self.layers[-1]))
        return len(self.snapshots) - 1

    def fork(self, snapshot_id):
        """从快照创建一个独立的新 KV，两边后续写入互不影响。"""
        if not 0 <= snapshot_id < len(self.snapshots):
            raise ValueError(f"unknown snapshot id: {snapshot_id}")
        return KV(self.snapshots[snapshot_id])
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert store.get("a") is None` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 嵌套事务：内层删除，回滚后恢复外层的值
store = KV()
store.set("a", 1)
store.begin()
store.set("a", 2)
store.begin()
store.delete("a")
assert store.get("a") is None
store.rollback()
assert store.get("a") == 2
store.commit()
assert store.get("a") == 2

# 单层事务回滚回到提交前的值
store.begin()
store.set("a", 5)
store.rollback()
assert store.get("a") == 2

# fork 出来的分支写入不影响原实例
snapshot_id = store.snapshot()
branch = store.fork(snapshot_id)
branch.set("a", 3)
assert store.get("a") == 2
assert branch.get("a") == 3

# get 返回的可变值是副本
store.set("a", [1])
value = store.get("a")
value.append(2)
assert store.get("a") == [1]

# 没有事务时 commit/rollback 报错；None 不能作为值；未知快照报错
expect_value_error(store.commit)
expect_value_error(store.rollback)
expect_value_error(store.set, "b", None)
expect_value_error(store.fork, 99)
assert store.delete("missing") is False
```

### 复杂度与追问

设当前键数为 n、单个值的大小为 s。`get` / `set` 是 O(s)（深拷贝值），`delete` 是 O(1)；`begin`、`snapshot`、`fork` 都要复制整份数据，是 O(n·s)；`commit` 和 `rollback` 是 O(1)。

追问「事务很多、数据很大，复制太贵怎么办」：每层只存本事务改过的键，删除写一个 tombstone 标记，`get` 从顶层往下找，遇到 tombstone 就返回不存在；`commit` 把子层的改动和 tombstone 合并进父层，最外层提交时才真正写进基础存储并清掉 tombstone。快照则可以换成持久化结构（如持久 HAMT 或带父指针的版本链），未改动的部分在版本间共享。这两种做法都要重新验证「内层删除、外层回滚」这类组合的结果。

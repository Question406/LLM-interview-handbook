---
id: p3a-xai-weighted-lru-cache
section: xai
order: 605
level: A
title: xAI：按总权重限容的 LRU
quick: >-
  哈希表和双向链表维护 LRU，再用 used 记录总权重。put 先检查单项是否超容，更新已有 key
  时扣旧权重，再循环淘汰最久未用项；超容写入按练习约定返回 False 并保留旧值。
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
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · xAI · weighted-lru-cache
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/weighted-lru-cache
    type: secondary
---

## 题目描述

实现按条目总权重计容量的 LRU 缓存，并支持保存和恢复顺序。还要为函数调用构造稳定缓存键，保证参数类型和内容不同的调用不会被错误地当成同一个缓存项。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Cache(capacity)`：总权重上限，`capacity` 不能为负。
- `get(key)`：命中返回值并把该项移到最近使用端，未命中返回 `None`。
- `put(key, value, weight=1) -> bool`：`weight` 必须为正。单项权重超过 `capacity` 时拒绝写入、保留旧值并返回 `False`；否则写入（更新已有 key 时同样移到最近使用端），必要时连续淘汰最久未用的条目，返回 `True`。
- `save(path)` / `Cache.load(path)`：把容量和按 LRU 顺序排列的条目写成 JSON 快照，原子替换目标文件；加载后顺序和总权重与保存时一致。键和值都限 JSON 可表示的类型。
- `call_key(args, kwargs) -> str`：为一次函数调用生成缓存键。kwargs 的传入顺序不影响结果；`True` 和 `1`、`tuple` 和 `list` 要得到不同的键；嵌套 dict 的 key 必须是字符串；假定使用受支持的类型。
- 最多 $10^4$ 项。

### 示例

```text
cache = Cache(5)
put("a", "A", 3); put("b", "B", 2); get("a")   -> "A"
put("c", "C", 2)                               # 总权重 7 > 5，淘汰最久未用的 b
get("b")                                       -> None
put("a", "bad", 6)                             -> False，get("a") 仍是 "A"
call_key((1,), {"x": 2, "y": 3}) == call_key((1,), {"y": 3, "x": 2})   -> True
call_key((True,), {}) == call_key((1,), {})                           -> False
```

## 解题思路与参考答案

我会沿用哈希表加双向链表的 LRU 结构，再用 `used` 记录总权重；Python 可以直接用 `OrderedDict`。一次插入可能要腾出多个条目的空间，所以淘汰条件检查总权重，循环直到放得下。

## 题目

实现一个 LRU 缓存，每个条目带一个权重（大小），限制的是所有条目的总权重而不是条目个数。插入一个大条目时，可能要连续淘汰好几个最久未用的条目才能放得下。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定。这份练习和 Anthropic 的 LRU 调试题共用一份实现，所以还带了缓存键和持久化接口。

几个容易出错的地方：

- 更新已有 key 时，要先减掉旧权重再判断要不要淘汰，否则会多淘汰；
- 淘汰要写成循环，一次插入可能淘汰多项；
- 单项权重超过容量时，要先和面试官约定是拒绝还是直接不缓存。如果不处理，淘汰循环会把缓存清空后仍然放不下，或者错误地把超限条目留在里面。这份练习约定拒绝写入、保留旧值并返回 `False`。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Cache(capacity)`：总权重上限，`capacity` 不能为负。
- `get(key)`：命中返回值并把该项移到最近使用端，未命中返回 `None`。
- `put(key, value, weight=1) -> bool`：`weight` 必须为正，否则抛 `ValueError`。单项权重超过 `capacity` 时拒绝写入、保留旧值并返回 `False`；否则写入（更新已有 key 时同样移到最近使用端），必要时连续淘汰最久未用的条目，返回 `True`。
- `save(path)` / `Cache.load(path)`：把容量和按 LRU 顺序排列的条目写成 JSON 快照，原子替换目标文件；加载后顺序和总权重与保存时一致。键和值都限 JSON 可表示的类型。
- `call_key(args, kwargs) -> str`：为一次函数调用生成缓存键。kwargs 的传入顺序不影响结果；`True` 和 `1`、`tuple` 和 `list` 要得到不同的键；嵌套 dict 的 key 必须是字符串；不支持的类型抛 `ValueError`。
- 最多 $10^4$ 项。

### 输入输出示例

```text
cache = Cache(5)
put("a", "A", 3); put("b", "B", 2); get("a")   -> "A"
put("c", "C", 2)                               # 总权重 7 > 5，淘汰最久未用的 b
get("b")                                       -> None
put("a", "bad", 6)                             -> False，get("a") 仍是 "A"
call_key((1,), {"x": 2, "y": 3}) == call_key((1,), {"y": 3, "x": 2})   -> True
call_key((True,), {}) == call_key((1,), {})                           -> False
```

### 解题思路与正确性

`OrderedDict` 的顺序就是从最久未用到最近使用，`move_to_end` 和 `popitem(last=False)` 都是 O(1)，相当于哈希表加双向链表。`put` 先扣掉旧权重，再不断从最旧端淘汰，直到 `used + weight <= capacity`；因为事先已拒绝了超过容量的单项，这个循环一定会停。

`save` 先写同目录下的临时文件并 `fsync`，再用 `os.replace` 原子替换，所以崩溃时目标文件要么是旧快照，要么是新快照，不会是半截 JSON。这是显式调用 `save` 的契约，不保证每次 `put` 之后都已落盘。

`call_key` 把每个参数编码成「类型名 + 内容」，dict 按 key 排序，再用 JSON 序列化成字符串。它不会把函数默认参数补齐：`f(1)` 和 `f(1, b=2)` 即使语义相同也是两个键，要 normalization 得先用 `inspect.signature(f).bind(...)` 再 `apply_defaults()`。

### 完整参考实现（Python 3）

```python
from collections import OrderedDict
import json
import os
import tempfile


def _freeze(value):
    """把参数编码成带类型标签的 JSON 结构，使 True 和 1、tuple 和 list 得到不同的键。"""
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("dict keys in cache key must be str")
        return ["dict", sorted((key, _freeze(item)) for key, item in value.items())]
    if isinstance(value, (tuple, list)):
        return [type(value).__name__, [_freeze(item) for item in value]]
    if value is None or type(value) in (bool, int, float, str):
        return [type(value).__name__, value]
    raise ValueError(f"unsupported cache key type: {type(value).__name__}")


def call_key(args, kwargs):
    """根据一次函数调用的 args 和 kwargs 生成缓存键；kwargs 的传入顺序不影响结果。"""
    return json.dumps([_freeze(args), _freeze(kwargs)], sort_keys=True, allow_nan=False)


class Cache:
    """按总权重限容的 LRU。data 里从最久未用到最近使用排列，值为 (value, weight)。"""

    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.data = OrderedDict()
        self.used = 0

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key][0]

    def put(self, key, value, weight=1):
        """插入或更新；单项权重超过容量时拒绝并返回 False，旧值保留。"""
        if weight <= 0:
            raise ValueError("weight must be positive")
        if weight > self.capacity:
            return False
        if key in self.data:
            _, old_weight = self.data.pop(key)
            self.used -= old_weight
        # 一次插入可能要连续淘汰好几个最久未用的条目
        while self.used + weight > self.capacity:
            _, (_, evicted_weight) = self.data.popitem(last=False)
            self.used -= evicted_weight
        self.data[key] = (value, weight)
        self.used += weight
        return True

    def save(self, path):
        """写临时文件并 fsync，再原子替换目标文件，读者不会看到写了一半的快照。"""
        directory = os.path.dirname(os.path.abspath(path))
        fd, tmp_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd, "w") as file:
                json.dump([self.capacity, list(self.data.items())], file)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @classmethod
    def load(cls, path):
        """按保存时的顺序逐个 put，恢复 LRU 顺序和总权重。"""
        with open(path) as file:
            capacity, items = json.load(file)
        cache = cls(capacity)
        for key, (value, weight) in items:
            cache.put(key, value, weight)
        return cache
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert cache.get("a") == "A"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

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


# 访问 a 之后插入 c，最久未用的 b 被淘汰
cache = Cache(5)
cache.put("a", "A", 3)
cache.put("b", "B", 2)
assert cache.get("a") == "A"
cache.put("c", "C", 2)
assert cache.get("b") is None
assert cache.get("c") == "C"

# 超过容量的单项被拒绝，旧值保留
assert not cache.put("a", "bad", 6)
assert cache.get("a") == "A"

# 一次插入连续淘汰多项
cache.put("d", "D", 5)
assert list(cache.data) == ["d"]
assert cache.used == 5

# 权重必须为正
expect_value_error(cache.put, "e", "E", 0)

# 缓存键：kwargs 顺序无关，bool 和 int 不同，tuple 和 list 不同
assert call_key((1,), {"x": 2, "y": 3}) == call_key((1,), {"y": 3, "x": 2})
assert call_key((True,), {}) != call_key((1,), {})
assert call_key(([1],), {}) != call_key(((1,),), {})
expect_value_error(call_key, (object(),), {})

# 保存后加载，顺序和总权重一致
cache = Cache(5)
cache.put("a", "A", 3)
cache.put("b", "B", 2)
cache.get("a")
with tempfile.TemporaryDirectory() as directory:
    path = os.path.join(directory, "cache.json")
    cache.save(path)
    restored = Cache.load(path)
    assert list(restored.data) == list(cache.data) == ["b", "a"]
    assert restored.used == cache.used
```

### 复杂度与追问

设缓存条目数为 n。`get` 是 O(1)；单次 `put` 最坏要淘汰 O(n) 项，但每个条目只会被淘汰一次，按插入次数均摊是 O(1)；`save` 和 `load` 都是 O(n)。

- 断电后也要保证快照存在：`os.replace` 之后还要对父目录做 `fsync`，否则目录项的更新可能丢失。
- 要求每次写入返回前就持久化：改成先追加写 WAL（write-ahead log）并 `fsync`，再改内存；恢复时加载最近快照，再按顺序重放之后的日志。
- 多个进程写同一个快照文件：需要文件锁或单写者约定，否则后完成的 `replace` 会覆盖另一个进程的结果。

## 相关题

- [[p3a-anthropic-coding-q2-lru-cache-durability]]：和本题共用同一份练习实现；Anthropic 那题的题面是修缓存键和加持久化，本题的题面是按总权重淘汰。
- [[xai-lru-cache]]：同为 xAI 的基础 LRU，按条目数限容，重点是 $O(1)$ 和并发分片，以及怎么接 KV 事务。

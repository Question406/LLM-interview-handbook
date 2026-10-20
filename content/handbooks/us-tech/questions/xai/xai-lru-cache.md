---
id: xai-lru-cache
section: xai
order: 9
level: A
title: xAI：手写 LRU / 并发缓存，和 KV 事务题怎么衔接
quick: >-
  哈希表加双向链表做到 $O(1)$ get/put，并发时按 key 分片加锁；接 KV 事务时，缓存只放已提交的版本，未提交写不能进共享缓存。
tags:
  - 完整编程练习
  - xAI
  - LRU
  - Concurrency
  - Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Get a Job at xAI — Interview Process and Top Questions
    url: https://www.tryexponent.com/blog/xai-interview-process
    type: secondary
  - title: xAI Software Engineer Interview Guide
    url: https://www.tryexponent.com/guides/xai-software-engineer-interview
    type: secondary
  - title: xAI Interview Questions from Candidate Reports
    url: https://aceoffer.app/interviews/xai
    type: secondary
  - title: Practice xAI Mock Interviews
    url: https://igotanoffer.com/en/mock-interviews/company/xai
    type: secondary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是原帖完整题面或官方测试。Python 3 标准库，CPU 上验证。

### 题面、接口与约束

- `LRUCache(capacity)`：带权重、线程安全的 LRU 缓存。`capacity` 是非负整数，表示总权重上限，否则抛 `ValueError`。
- `get(key)`：命中时返回值，并把这个 key 标成最近使用；未命中返回 `None`。
- `put(key, value, weight=1) -> bool`：写入或替换，然后从最久未使用的一端淘汰，直到总权重 ≤ `capacity`。单个条目的 `weight` 超过 `capacity` 时拒绝写入、返回 `False`，旧值保留。
- `weight` 必须是正整数，`value` 不能是 `None`（否则和未命中分不清），违反时抛 `ValueError`。
- 用哈希表加双向链表实现，不能用 `OrderedDict`；`get` 和 `put` 的整个状态变更都必须原子化。

### 输入输出示例

```text
cache = LRUCache(5)
put("a", "A", 3), put("b", "B", 2)   -> True, True     # 总权重 5
get("a")                             -> "A"            # a 变成最近使用
put("c", "C", 2)                     -> True           # 超出 2，淘汰最久未用的 b
get("b")                             -> None
put("a", "X", 6)                     -> False          # 单条超过容量，拒绝
get("a")                             -> "A"            # 旧值还在
```

### 解题思路与正确性

链表用头尾两个哨兵节点，中间只放存活的条目：靠近 `head` 的是最久未使用，靠近 `tail` 的是最近使用。哈希表 `nodes` 和链表节点一一对应，`used` 始终等于所有节点的权重之和。

命中或写入时，把节点摘下来再挂到 `tail` 前面，这两步各只改四根指针，O(1)。总权重超限时，从 `head` 后面开始摘节点，摘掉的正好是最久未使用的，符合 LRU 顺序。

所有公开操作持同一把锁。`get` 看起来只是读，但它也会移动链表节点，所以同样必须加锁。

### 完整参考实现（Python 3）

```python
from threading import RLock


class Node:
    def __init__(self, key=None, value=None, weight=0):
        self.key = key
        self.value = value
        self.weight = weight
        self.prev = None
        self.next = None


class LRUCache:
    """带权重的线程安全 LRU：head 一侧最久未使用，tail 一侧最近使用。"""

    def __init__(self, capacity):
        if type(capacity) is not int or capacity < 0:
            raise ValueError(f"capacity must be a non-negative int, got {capacity!r}")
        self.capacity = capacity
        self.used = 0                 # 存活条目的权重之和
        self.nodes = {}               # key -> Node
        self.head = Node()            # 哨兵：head.next 是最久未使用
        self.tail = Node()            # 哨兵：tail.prev 是最近使用
        self.head.next = self.tail
        self.tail.prev = self.head
        self.lock = RLock()

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_recent(self, node):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        """命中返回值并标成最近使用，未命中返回 None。"""
        with self.lock:
            node = self.nodes.get(key)
            if node is None:
                return None
            self._unlink(node)
            self._append_recent(node)
            return node.value

    def put(self, key, value, weight=1):
        """写入或替换并按 LRU 淘汰；单条权重超过容量时拒绝并返回 False。"""
        if type(weight) is not int or weight <= 0:
            raise ValueError(f"weight must be a positive int, got {weight!r}")
        if value is None:
            raise ValueError("value must not be None")
        with self.lock:
            if weight > self.capacity:
                return False
            old = self.nodes.get(key)
            if old is not None:
                self._unlink(old)
                self.used -= old.weight
            node = Node(key, value, weight)
            self.nodes[key] = node
            self._append_recent(node)
            self.used += weight
            while self.used > self.capacity:
                victim = self.head.next
                self._unlink(victim)
                del self.nodes[victim.key]
                self.used -= victim.weight
            return True
```

### 可执行测试

```python
import random
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def keys_in_order(cache):
    """从最久未使用到最近使用列出 key，同时检查双向指针一致。"""
    keys = []
    node = cache.head.next
    while node is not cache.tail:
        assert node.next.prev is node
        assert node.prev.next is node
        keys.append(node.key)
        node = node.next
    return keys


# 题面例子：get 刷新 a，于是淘汰 b
cache = LRUCache(5)
assert cache.put("a", "A", 3)
assert cache.put("b", "B", 2)
assert cache.get("a") == "A"
assert cache.put("c", "C", 2)
assert cache.get("b") is None

# 单条超过容量：拒绝，旧值保留
assert not cache.put("a", "X", 6)
assert cache.get("a") == "A"

# 替换会更新权重
assert cache.put("a", "new", 1)
assert cache.used == 3

# 容量 0：什么都放不进
assert not LRUCache(0).put("x", 1)

# 一个大条目可以挤掉多个小条目
cache = LRUCache(4)
for key in "wxyz":
    cache.put(key, key)
assert cache.put("big", "B", 3)
assert keys_in_order(cache) == ["z", "big"]

# 非法参数
expect_value_error(LRUCache, -1)
expect_value_error(cache.put, "k", "v", 0)
expect_value_error(cache.put, "k", None)

# 随机操作序列，和 OrderedDict 实现的参照模型逐步对比
rng = random.Random(3)
cache = LRUCache(7)
oracle = OrderedDict()  # key -> (value, weight)，从旧到新
for _ in range(500):
    key = rng.randrange(8)
    if rng.random() < 0.4:
        expected = oracle[key][0] if key in oracle else None
        if key in oracle:
            oracle.move_to_end(key)
        assert cache.get(key) == expected
    else:
        weight = rng.randrange(1, 10)
        value = rng.randrange(100)
        assert cache.put(key, value, weight) == (weight <= 7)
        if weight <= 7:
            oracle.pop(key, None)
            oracle[key] = (value, weight)
            while sum(w for _, w in oracle.values()) > 7:
                oracle.popitem(last=False)
    assert keys_in_order(cache) == list(oracle)
    assert cache.used == sum(w for _, w in oracle.values())

# 并发写入不丢条目
cache = LRUCache(100)
with ThreadPoolExecutor(8) as pool:
    assert all(pool.map(lambda i: cache.put(i, i), range(100)))
assert cache.used == 100
assert all(cache.get(i) == i for i in range(100))
```

### 复杂度与追问

设存活的 key 数为 n。`get` 是 O(1)；`put` 单次是 O(1 + 本次淘汰的条目数)，但每个插入的节点最多被淘汰一次，所以整个操作序列均摊 O(1)。空间 O(n)。

- 追问「全局锁够不够」：它只保证单机多线程安全，吞吐受限，也不能据此声称分布式一致性。分片的做法见下文。

## 题怎么来的

Exponent 和 AceOffer 把 LRU（包括加权变体）列为 xAI coding 的高频题，和 KV 事务、rate limiter 是一类：考的是一个能跑的类、边界和并发，而不是链表细节。这张卡 `realInterview: false`，是按公开题库准备的。和 `xai-kv-txn` 的衔接点在于：事务要快照隔离，缓存是快照的物化，淘汰策略不能破坏隔离。

## 先写对 $O(1)$，再加容量

结构是 `dict[key] -> node`，节点串在双向链表上，一端是最近使用，另一端是最久未使用。`get` 命中就把节点挪到最近使用那端；`put` 遇到已有的 key 就更新值并挪过去，满了从最久未使用那端删。上面的实现里 `tail` 一侧是最近使用，`head` 一侧是最久未使用。

常见错误有三个：用 `list` 当队列再调 `index`，那是 $O(n)$；满了之后删错了端，删掉的是最近使用的条目；`get` 命中后忘了更新顺序。

加权 LRU（AceOffer 提到过）给每个节点带一个 `weight`，容量是权重之和，淘汰时仍从最久未使用的开始，直到腾出足够的权重。一个最简单的单测：不加权、容量 2 时，依次 `put a, b, c` 后 `get a` 应该 miss。

## 并发：分片，不要和事务抢同一把锁

一把全局锁能写对，但吞吐难看。可以按 `hash(key) % N` 分片，每片有自己的 map、链表和锁，`get` 只锁一片。如果跨片没有事务需求，这样就够了。

如果能和 `xai-kv-txn` 衔接起来，这一轮会加分：

1. **缓存里只放已提交的版本。** 事务的写缓冲在 commit 成功之前不要 `put` 进共享的 LRU，否则别的读会看到脏数据，快照隔离就被破坏了。
2. **commit 之后按版本号 put。** 迟到的旧 commit 不能覆盖新版本：`if incoming.ver < cached.ver: ignore`。
3. **淘汰不等于 abort。** LRU 丢掉的只是副本，源 KV 还在。但如果你把 LRU 当成主存（面试里常这样简化），淘汰就等于删 key，这时要和事务的写集核对：未提交的 key 被淘汰后，commit 时还要能写回去；或者干脆禁止淘汰持有活跃写锁的节点。
4. **按快照读。** 事务 begin 时记下版本号。`get` 走缓存时，如果 `cached.ver > begin.ver`，要回源读旧版本，或者直接当作 miss 回主结构。缓存命中不代表「最新的就是对的」。

TTL 常作为 follow-up：过期和 LRU 是两个独立的维度，可以惰性删除（`get` 时检查 `expire_at`），再叠加容量淘汰。不要把它和 `xai-rate-limiter` 的时间窗混成一个桶，限流管的是配额，缓存管的是副本。

还有几个常见错误：用 `dict` 的插入顺序当 LRU，却讲不清它为什么成立；并发下 `get` 移动链表时不持锁；把缓存当成事务日志用。

## 追问

- **为什么不用单链表？** 删除和移动节点都需要 $O(1)$ 拿到前驱，双向链表最干净。
- **分片会不会让全局容量不准？** 每片容量是 `cap/N`，最坏情况一片很热、一片很空。这通常可以接受；要更准的话，用全局计数加近似 LRU（CLOCK）。先保证正确，再做近似。
- **和 KV 事务衔接时哪句话最重要？** 未提交的写不可见。LRU 是已提交状态的加速层，不是写缓冲。
- **加权变体怎么测？** 放进一个大对象，应该挤掉多个小对象；`get` 只更新访问顺序，不改权重，除非题目要求权重随值变化。

## 相关题

- [[p3a-xai-weighted-lru-cache]]：同为 xAI，本题追问里的加权变体单独成题，按总权重限容，一次插入可能连续淘汰多项。
- [[p3a-anthropic-coding-q2-lru-cache-durability]]：Anthropic 的 LRU 调试题，不考并发，考函数调用的缓存键怎么编码，以及崩溃后怎么从快照和日志恢复。
- [[xai-kv-txn]]：卡名里说的衔接对象：带快照和读写集版本校验的 KV 事务。
- [[p3a-xai-transactional-key-value-store]]：嵌套事务 KV，overlay 加 tombstone 的写法，同样只该把提交后的值放进缓存。

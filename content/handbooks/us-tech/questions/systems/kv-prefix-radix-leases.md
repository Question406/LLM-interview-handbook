---
id: kv-prefix-radix-leases
section: systems
order: 33
level: S
title: "KV Prefix ③：Radix Cache 的 pin/unpin、活跃分裂与叶子 LRU"
quick: "每个活跃请求用 lease 锁住命中点及整条祖先路径，释放时从稳定的终点 Node 沿当前 parent 链回退。边分裂时让新父节点继承锁计数，淘汰只挑未锁定的叶子，就能保护仍在使用的前缀。"
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "SGLang split-node, lock references and eviction"
    url: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
    type: primary
---

## 题目描述

实现带租约保护的压缩 token 前缀缓存。活跃请求命中的 KV 句柄不得被回收，而未被任何请求使用的路径可按最近使用顺序淘汰。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `PinnedRadix()` 在不同 namespace 下维护互相隔离的 token 前缀，token 为整数，每个 token 对应一个不可变、不透明 KV 句柄。
- `insert(tokens,values,namespace="default") -> int`：tokens 与 values 等长，保存尚未缓存的后缀，返回原已缓存的最长前缀长度。共有前缀保留原句柄，重复插入不重复占空间。
- `match(tokens,namespace="default") -> (length,values)` 返回最大命中 token 前缀长度及其句柄 tuple；命中可以在压缩边中间结束，空命中为 (0,())。
- `acquire(tokens,namespace="default") -> (lease,length,values)` 与 match 命中相同，并保护恰好命中的路径，未命中的后缀不受保护。lease 是唯一标识，允许多个活跃 lease 重叠；后续插入造成的结构变化不能解除已有保护。
- `release(lease)` 解除该 lease 的保护，调用方保证 lease 有效且只释放一次。
- `evict(target_tokens) -> tuple`：`target_tokens`>=0，每次只删除无任何 lease 保护的叶边，优先最近访问时间最早者；整边释放，可能超过目标。删除后父边成为叶边时可继续回收。资源均受保护时返回已释放的句柄，允许少于目标，0 目标返回 ()。
- 最近使用时间是递增逻辑时钟：insert 遍历或新建的边、acquire 命中的边都会更新，match 不更新。`validate() -> int` 返回结构中所有 namespace 的 token 总数并检查边/父子关系不变量。
- 边为非空 token tuple，句柄 tuple 与边等长；调用串行。句柄仅返回给调用方回收，不由缓存销毁。

### 输入输出示例

```text
insert([1,2,3,4],["a","b","c","d"]) -> 0
acquire([1,2,3,4]) -> (lease,4,("a","b","c","d"))
insert([1,2,9],["a","b","x"]) -> 2
evict(100) -> ("x",)
release(lease)
evict(100) -> 返回恰好含 "a","b","c","d" 的 tuple（顺序取决于整边回收顺序）
```

## 解题思路与参考答案

我会让 lease 保存命中终点的 Node，并锁住从终点到根的整条前缀路径。之后即使插入操作拆了边，只要新父节点继承原锁计数，释放时沿当前 parent 链回退，活跃前缀就不会被提前淘汰。

## 完整编程练习（手册原创实现版）

> 本题是为理解开源机制写的独立练习，不是某家公司确认过的原题，也不是 SGLang/vLLM 源码的逐字翻译。接口、简化条件和测试由手册定义。Python 3 标准库，在 CPU 上验证状态语义，不报告 GPU 吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

在上一题 `RadixCache`（按 token 粒度压缩边的前缀树，值是不透明的 KV 句柄）的基础上，实现 `PinnedRadix`：

- `acquire(tokens, namespace='default') -> (lease, length, values)`：命中到哪里就保护到哪里，命中点落在一条边中间时先把边拆开。返回唯一的 lease id、命中长度和命中的句柄。多个活跃 lease 可以重叠。
- `release(lease)`：释放一个 lease，沿路径把锁计数减回去。未知的或已经释放过的 lease 抛 `ValueError`。
- `evict(target_tokens) -> tuple`：只淘汰没有被锁住的叶子，按逻辑访问时钟做 LRU；移走一个叶子后，它的父节点可能变成新的候选。每次移走一整条边，所以释放的 token 数可以超过目标。所有节点都被锁住时，返回已经释放的句柄（可能少于目标），不会强拆活跃路径。`target_tokens` 为负抛 `ValueError`。
- 调用是串行的。`evict` 返回的句柄交还给调用方，由调用方做物理回收。

### 输入输出示例

```text
insert([1, 2, 3, 4], [a, b, c, d]);  lease = acquire([1, 2, 3, 4])
insert([1, 2, 9], [a, b, x])
# 边 [1,2,3,4] 被拆成 [1,2] -> [3,4]，新的公共父节点 [1,2] 继承 locks = 1
evict(100)  -> (x,)            # 只有未锁定的叶子 [9] 能被淘汰
release(lease)
# [1,2] 和 [3,4] 的锁计数都回到 0
evict(100)  -> {a, b, c, d}
```

### 解题思路与正确性

例如已经锁住 [1,2,3,4]，又插入 [1,2,9]，公共边会拆出 [1,2] 父节点。原 lease 保存的终点 `Node` 对象没有变，只是它到祖先之间多了一个节点，释放时应沿当前 parent 链走。

关键是让新的中间节点继承被拆节点的锁计数。被拆节点的锁计数等于经过它的活跃 lease 数，而这些 lease 释放时也都会经过新插入的中间节点，所以两者的计数一开始就该相同；否则释放时中间节点会被减成负数，或者在 lease 还活着时就被当成可淘汰。

`acquire` 把终点到根的整条路径都加锁。活跃请求依赖的是整段前缀，路径上每个节点的锁计数都不为 0，叶子淘汰就不会间接破坏这条前缀。

### 完整参考实现（Python 3）

```python
class Node:
    def __init__(self, edge=(), values=(), parent=None):
        self.edge = tuple(edge)      # 这条边上的 token
        self.values = tuple(values)  # 每个 token 一个 KV 句柄
        self.parent = parent
        self.children = {}           # 子边首 token -> Node
        self.locks = 0               # 经过该节点的活跃 lease 数
        self.used = 0                # 最近访问的逻辑时钟


class RadixCache:
    """按 token 粒度压缩边的前缀树。值是不透明、不可变的 KV 句柄。"""

    def __init__(self):
        self.roots = {}
        self.clock = 0

    def root(self, namespace):
        return self.roots.setdefault(namespace, Node())

    def touch(self, node):
        self.clock += 1
        node.used = self.clock

    @staticmethod
    def split(child, length):
        """把 child 的边在 length 处拆成 mid -> child，返回新的中间节点 mid。"""
        if not 0 < length < len(child.edge):
            raise ValueError(f"split point {length} must be inside an edge of length {len(child.edge)}")
        parent = child.parent
        mid = Node(child.edge[:length], child.values[:length], parent)
        # 现存 lease 的终点对象不变、释放时会经过 mid，所以 mid 继承 child 的锁计数
        mid.locks = child.locks
        mid.used = child.used
        parent.children[mid.edge[0]] = mid
        child.edge = child.edge[length:]
        child.values = child.values[length:]
        child.parent = mid
        mid.children[child.edge[0]] = child
        return mid

    def walk(self, tokens, namespace, split_boundary=False):
        """沿树匹配 tokens，返回 (命中长度, 命中句柄, 终点节点)。

        split_boundary=True 时，命中点落在边中间就先拆边，让终点恰好是一个节点。
        """
        tokens = tuple(tokens)
        node = self.root(namespace)
        offset = 0
        values = []
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                break
            count = 0
            while (count < len(child.edge) and offset + count < len(tokens)
                   and child.edge[count] == tokens[offset + count]):
                count += 1
            values.extend(child.values[:count])
            offset += count
            if count < len(child.edge):
                if count and split_boundary:
                    node = self.split(child, count)
                break
            node = child
        return offset, tuple(values), node

    def match(self, tokens, namespace="default"):
        length, values, _ = self.walk(tokens, namespace)
        return length, values

    def insert(self, tokens, values, namespace="default"):
        """插入 tokens 及其句柄，返回已经在树里的前缀长度（调用方可丢弃这部分重复句柄）。"""
        tokens = tuple(tokens)
        values = tuple(values)
        if len(tokens) != len(values):
            raise ValueError(f"need one KV handle per token, got {len(tokens)} tokens and {len(values)} handles")
        node = self.root(namespace)
        offset = 0
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                child = Node(tokens[offset:], values[offset:], node)
                node.children[child.edge[0]] = child
                self.touch(child)
                return offset
            count = 0
            while (count < len(child.edge) and offset + count < len(tokens)
                   and child.edge[count] == tokens[offset + count]):
                count += 1
            if count < len(child.edge):
                child = self.split(child, count)
            offset += count
            node = child
            self.touch(node)
        return offset

    def validate(self):
        """检查树结构不变量，返回树里的 token 总数。"""
        count = 0

        def visit(node):
            nonlocal count
            for first, child in node.children.items():
                assert child.parent is node and child.edge and first == child.edge[0]
                assert len(child.edge) == len(child.values)
                count += len(child.edge)
                visit(child)

        for root in self.roots.values():
            visit(root)
        return count


class PinnedRadix(RadixCache):
    """支持 lease 的 radix cache：活跃请求锁住整条祖先路径，淘汰只选未锁定的叶子。"""

    def __init__(self):
        super().__init__()
        self.leases = {}  # lease id -> 路径终点 Node
        self.next_lease = 0

    def acquire(self, tokens, namespace="default"):
        """锁住命中路径（必要时拆边），返回 (lease, 命中长度, 命中句柄)。"""
        length, values, node = self.walk(tokens, namespace, split_boundary=True)
        current = node
        while current.parent is not None:
            current.locks += 1
            self.touch(current)
            current = current.parent
        self.next_lease += 1
        self.leases[self.next_lease] = node
        return self.next_lease, length, values

    def release(self, lease):
        """沿终点当前的 parent 链把锁计数减回去。"""
        if lease not in self.leases:
            raise ValueError(f"unknown or already released lease: {lease!r}")
        current = self.leases.pop(lease)
        while current.parent is not None:
            assert current.locks > 0
            current.locks -= 1
            current = current.parent

    def evict(self, target_tokens):
        """按 LRU 移走未锁定的叶子，直到释放至少 target_tokens 个句柄或没有候选。"""
        if target_tokens < 0:
            raise ValueError(f"eviction target must be non-negative, got {target_tokens}")
        freed = []
        while len(freed) < target_tokens:
            candidates = []

            def visit(node):
                for child in node.children.values():
                    if not child.children and child.locks == 0:
                        candidates.append(child)
                    visit(child)

            for root in self.roots.values():
                visit(root)
            if not candidates:
                break
            victim = min(candidates, key=lambda candidate: candidate.used)
            del victim.parent.children[victim.edge[0]]
            freed.extend(victim.values)  # 一次移走整条边
        return tuple(freed)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert child.parent is node and child.edge and first == child.edge[0]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test():
    tree = PinnedRadix()
    tree.insert([1, 2, 3, 4], ["a", "b", "c", "d"])
    lease, length, values = tree.acquire([1, 2, 3, 4])
    assert length == 4
    assert values == ("a", "b", "c", "d")

    # 拆分一条已加锁的边：新的中间节点继承锁计数，受原 lease 保护
    tree.insert([1, 2, 9], ["a", "b", "x"])
    mid = tree.root("default").children[1]
    assert mid.locks == 1
    assert mid.children[3].locks == 1
    assert tree.evict(100) == ("x",)
    assert tree.match([1, 2, 3, 4])[0] == 4

    # 释放后锁计数归零，整条路径都可以被淘汰
    tree.release(lease)
    assert mid.locks == 0
    assert mid.children[3].locks == 0
    assert set(tree.evict(100)) == {"a", "b", "c", "d"}
    assert tree.validate() == 0

    # 重复释放报错
    expect_value_error(lambda: tree.release(lease))

    # 查询在边中间结束：只锁命中的前缀，不锁没用到的后缀
    tree.insert([5, 6, 7], ["e", "f", "g"])
    first, hit, _ = tree.acquire([5, 6])
    second, _, _ = tree.acquire([5, 6, 8])
    assert hit == 2
    assert tree.evict(100) == ("g",)

    # 重叠的 lease：释放一个后前缀仍被另一个保护
    tree.release(first)
    assert tree.evict(100) == ()
    tree.release(second)
    assert set(tree.evict(100)) == {"e", "f"}

    # LRU 由逻辑时钟决定：访问过 [1] 之后，先淘汰 [2]
    tree.insert([1], ["A"])
    tree.insert([2], ["B"])
    lease, _, _ = tree.acquire([1])
    tree.release(lease)
    assert tree.evict(1) == ("B",)

    # 目标为 0 不淘汰；目标为负、句柄数不对都报错
    assert tree.evict(0) == ()
    expect_value_error(lambda: tree.evict(-1))
    expect_value_error(lambda: tree.insert([3, 4], ["only-one"]))

    # 完全没命中的 acquire 不锁任何节点，释放也安全
    miss, hit, values = tree.acquire([42])
    assert hit == 0
    assert values == ()
    tree.release(miss)
    assert tree.evict(100) == ("A",)


if __name__ == "__main__":
    test()
```

### 复杂度与追问

设树的深度为 H、节点数为 N。`acquire` 和 `release` 都是沿路径走一遍，O(H)。这个简化版 `evict` 每轮都扫描全部节点，释放 K 条边最坏 O(K·N)，不能拿它当生产里基于堆的 LRU。树索引和句柄占的空间与 token 数成线性，lease 表的空间等于活跃请求数。

- 追问「生产实现还会多什么」：显式维护的候选堆、锁的 receipt、按页对齐，以及异步回收。本练习只验证串行 CPU 上的生命周期。
- 追问「树上的锁计数能不能直接当物理页的 refcount」：不能。模型计算期间，GPU 页本身也必须有物理引用，第④题单独实现这一层。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[kv-prefix-radix]]：第②题，本题就是在那棵树上加 pin/unpin 和淘汰。
- [[kv-prefix-paged-cow]]：第④题，物理页 refcount 那一层，和 lease 分开计数。
- [[sys-radix-tree]]：口述版，讲为什么从叶子 LRU 淘汰、根上的系统提示尽量留下。
- [[p3a-xai-radix-cache]]：xAI 的 radix tree 题，只做数据结构，不含引用和淘汰。

---
id: kv-prefix-radix
section: systems
order: 32
level: S
title: KV Prefix ②：手写 Radix Tree——插入、边分裂与任意前缀命中
quick: >-
  Radix Tree 的压缩边同时保存 token 段和对应 KV
  句柄，匹配时累加每条边的公共部分。查询即使在边中间结束或分歧，也要返回可复用前缀，插入重复前缀则保留原句柄。
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: SGLang radix cache implementation
    url: >-
      https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
    type: primary
---

## 题目描述

实现按 token 前缀共享 KV 句柄的压缩 radix 缓存，支持命中压缩边内部的前缀。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`RadixCache()` 创建空缓存。`insert(tokens,values,namespace="default")` 中 tokens 为非负整数序列，values 为一一对应的不可变不透明句柄；返回插入前已有的连续 token 前缀长度。已有前缀的句柄保留，不被新 values 覆盖。

`match(tokens,namespace="default")` 返回 `(最长命中token数,句柄tuple)`，即使查询在一条压缩边的内部结束也须返回对应长度和句柄。不同 namespace 完全隔离，空查询返回 `(0,())`。`validate()` 检查内部结构一致性：非根边非空、子节点索引与首 token 相符、父子关系及句柄长度正确；通过时返回所有非根边 token 长度之和（所有 namespace 合计）。每条序列不超过 256 token，节点不超过 10000，调用串行执行。

### 示例

```text
insert([1,2,3,4],["a","b","c","d"]) 返回 0。
match([1,2,9])=(2,("a","b"))。
insert([1,2,8],["u","v","x"]) 返回 2。
match([1,2,8])=(3,("a","b","x"))，已有 a、b 未被覆盖。
```

## 解题思路与参考答案

我会让压缩边同时保存 token 段与每个位置的 KV 句柄，查询返回沿路径累积的最长公共前缀。比如已缓存 [1,2,3,4]，查询 [1,2,9] 仍应返回前两个位置，没必要等到完整插入串的终点才算命中。

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，代码为手册独立实现。接口、简化条件和测试由手册定义。依赖 Python 3与 NumPy，使用 CPU 测试数值及状态语义，不报告 GPU throughput。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `RadixCache.insert(tokens,values,namespace)`、`match` 和结构校验。输入是非负整数 token 序列，每个 token 对应一个不可变的 opaque KV 句柄；调用串行，长度≤256，节点≤10000。压缩边不能为空，children 按边首 token 索引，不同 namespace 隔离。

插入重复前缀时沿用树中原句柄，返回输入里已存在的前缀长度，调用者负责丢弃重复计算的句柄。match 返回最长已缓存 token 数，以及沿路径累计的全部句柄，边中途也算命中，空查询返回 0。它的契约与只查“最长已插入完整字符串”的字典不同。

### 输入输出示例

先插 `[1,2,3,4]→[a,b,c,d]`；查 `[1,2,9]` 返回 `(2,(a,b))`。再插 `[1,2,8]` 时产生公共边 `[1,2]` 与后缀 `[3,4]`、`[8]`，重复前缀句柄不会被替换。

### 解题思路与正确性

每一步先比较压缩边与剩余查询，找出最长公共段。插入遇到分歧时，把边和 payload 在同一位置切开。查询无需终止标记，因为内部 token 位置也有已算好的 KV；返回时把经过的边片段累计起来，避免漏掉祖先的 payload。随机测试则把所有插入序列的全部前缀存成独立 oracle，核对每种命中。

### 完整参考实现（Python 3）

```python
class Node:
    def __init__(self, edge=(), values=(), parent=None):
        self.edge, self.values, self.parent = tuple(edge), tuple(values), parent
        self.children = {}
        self.locks = 0
        self.used = 0


class RadixCache:
    """Token-granularity compressed edges. Values are opaque immutable KV handles."""

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
        if not 0 < length < len(child.edge):
            raise ValueError('split must be inside a nonempty edge')
        parent = child.parent
        mid = Node(child.edge[:length], child.values[:length], parent)
        # Existing live leases finish at stable node objects and release via parents.
        mid.locks, mid.used = child.locks, child.used
        parent.children[mid.edge[0]] = mid
        child.edge = child.edge[length:]
        child.values = child.values[length:]
        child.parent = mid
        mid.children[child.edge[0]] = child
        return mid

    def walk(self, tokens, namespace, split_boundary=False):
        tokens = tuple(tokens)
        node = self.root(namespace)
        offset, values = 0, []
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                break
            count = 0
            while (
                count < len(child.edge)
                and offset + count < len(tokens)
                and child.edge[count] == tokens[offset + count]
            ):
                count += 1
            values.extend(child.values[:count])
            offset += count
            if count < len(child.edge):
                if count and split_boundary:
                    node = self.split(child, count)
                break
            node = child
        return offset, tuple(values), node

    def match(self, tokens, namespace='default'):
        length, values, _ = self.walk(tokens, namespace)
        return length, values

    def insert(self, tokens, values, namespace='default'):
        tokens, values = tuple(tokens), tuple(values)
        if len(tokens) != len(values):
            raise ValueError('one KV handle per token')
        node = self.root(namespace)
        offset = 0
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                child = Node(tokens[offset:], values[offset:], node)
                node.children[child.edge[0]] = child
                self.touch(child)
                return offset  # caller can discard duplicated input handles[:offset]
            count = 0
            while (
                count < len(child.edge)
                and offset + count < len(tokens)
                and child.edge[count] == tokens[offset + count]
            ):
                count += 1
            if count < len(child.edge):
                child = self.split(child, count)
            offset += count
            node = child
            self.touch(node)
        return offset

    def validate(self):
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
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert child.parent is node and child.edge and first == child.edge[0]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

把实现与以下测试放进同一文件执行；测试覆盖正确性，不是生产环境的性能基准。

```python
def test():
    tree = RadixCache()
    assert tree.insert([1, 2, 3, 4], ['a', 'b', 'c', 'd']) == 0
    # Unlike a dictionary of terminal strings, every computed interior prefix hits.
    assert tree.match([1, 2, 9]) == (2, ('a', 'b'))
    assert tree.match([1, 2]) == (2, ('a', 'b'))
    assert tree.insert([1, 2, 8], ['dup-a', 'dup-b', 'x']) == 2
    assert tree.match([1, 2, 8, 7]) == (3, ('a', 'b', 'x'))
    assert tree.insert([1], ['duplicate']) == 1
    assert tree.validate() == 5
    assert tree.match([1], 'other') == (0, ())
    assert tree.insert([], []) == 0
    # Randomized oracle: union of all inserted prefixes, first payload wins.
    import random

    rng = random.Random(3)
    tree = RadixCache()
    oracle = {}
    for step in range(300):
        seq = tuple(rng.randrange(5) for _ in range(rng.randrange(1, 10)))
        payload = tuple((step, i) for i in range(len(seq)))
        tree.insert(seq, payload)
        for i in range(1, len(seq) + 1):
            oracle.setdefault(seq[:i], payload[i - 1])
        for _ in range(3):
            query = tuple(rng.randrange(5) for _ in range(rng.randrange(11)))
            length = 0
            while length < len(query) and query[: length + 1] in oracle:
                length += 1
            expected = tuple(oracle[query[:i]] for i in range(1, length + 1))
            assert tree.match(query) == (length, expected)
        assert tree.validate() == len(oracle)


if __name__ == '__main__':
    test()
```

### 复杂度与追问

比较 token 的时间为 $O(T)$。本实现的 tuple 切片与 payload 累积会分配内存，返回句柄需要 $O(T)$ 空间，树的 payload 空间随不同缓存 token 前缀数量增长。这只是 CPU 索引，GPU 页分配、并发锁和淘汰要另外处理，下一题会加活跃引用。

Page size 大于 1 时，逻辑命中还需按物理页对齐，第⑦题会做这一步。重复句柄由调用者释放，索引本身不直接释放 GPU 资源。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[p3a-xai-radix-cache]]：同样写压缩边和分裂，但查询只认终结节点、停在边中间不算命中，契约和本题正好相反。
- [[kv-prefix-radix-leases]]：第③题，在这棵树上加活跃引用和叶子 LRU。
- [[sys-radix-tree]]：SGLang 口述版，讲树在 CPU、页在 GPU 怎么配合。
- [[kv-prefix-block-hash]]：第⑤题，按整块链式哈希做索引的另一种方案。
- [[kv-prefix-engine]]：第⑧题，把这棵树接进真实的 Transformer 推理循环。

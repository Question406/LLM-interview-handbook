---
id: kv-prefix-radix
section: systems
order: 32
level: S
title: "KV Prefix ②：手写 Radix Tree——插入、边分裂与任意前缀命中"
quick: "边存 token 段及对应 KV 句柄；查询即使在压缩边中途结束或分歧，也应返回已计算的公共部分，不能只匹配终止节点。"
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
  - title: "SGLang radix cache implementation"
    url: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
    type: primary
---

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，不是某家公司的已确认原题，也不是SGLang/vLLM源码逐字翻译。接口、简化条件和测试由手册定义。依赖Python 3与NumPy，使用CPU测试数值及状态语义，不报告GPU吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `RadixCache.insert(tokens,values,namespace)`、`match` 与结构校验。token为非负整数序列，一token对应一个不可变opaque KV句柄；所有调用串行，长度≤256，节点≤10000。压缩边不能为空，children按边首token索引；不同namespace隔离。插入重复前缀时保留树中原句柄，返回输入中已经存在的前缀长度，调用者负责丢弃重复计算的句柄。match返回最长已缓存token数及沿路径累计的全部句柄，边中途也算命中；空查询返回0。不是“最长已插入完整字符串”字典。

### 输入输出示例

先插 `[1,2,3,4]→[a,b,c,d]`；查 `[1,2,9]` 返回 `(2,(a,b))`。再插 `[1,2,8]` 时产生公共边 `[1,2]` 与后缀 `[3,4]`、`[8]`，重复前缀句柄不会被替换。

### 解题思路与正确性

每一步比较当前压缩边与剩余查询的最长公共段。插入在分歧处把边和payload同步切开；查询不需要终止标记，因为每个计算过的内部token位置都有可复用KV。返回值是所有经过的边片段拼接，不能只返回最后节点的局部payload。随机测试用“所有插入序列的全部前缀”构造独立oracle。

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
            while (count < len(child.edge) and offset+count < len(tokens)
                   and child.edge[count] == tokens[offset+count]):
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
            while (count < len(child.edge) and offset+count < len(tokens)
                   and child.edge[count] == tokens[offset+count]):
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
        for i in range(1, len(seq)+1):
            oracle.setdefault(seq[:i], payload[i-1])
        for _ in range(3):
            query = tuple(rng.randrange(5) for _ in range(rng.randrange(11)))
            length = 0
            while length < len(query) and query[:length+1] in oracle:
                length += 1
            expected = tuple(oracle[query[:i]] for i in range(1, length+1))
            assert tree.match(query) == (length, expected)
        assert tree.validate() == len(oracle)

if __name__ == '__main__':
    test()
```

### 复杂度与追问

比较token数为 $O(T)$；本参考实现tuple切片和payload累积也会分配内存，返回句柄空间 $O(T)$，树payload空间等于不同缓存token前缀数量。它是CPU索引，不包含GPU页分配、并发锁或淘汰；下一题补活跃引用。

当page size大于1时不能直接把任意token命中都当成整页可复用。第⑦题把逻辑命中转换为物理页对齐命中。句柄重复的释放归调用者，索引本身不擅自释放GPU资源。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[p3a-xai-radix-cache]]：同样写压缩边和分裂，但查询只认终结节点、停在边中间不算命中，契约和本题正好相反。
- [[kv-prefix-radix-leases]]：第③题，在这棵树上加活跃引用和叶子 LRU。
- [[sys-radix-tree]]：SGLang 口述版，讲树在 CPU、页在 GPU 怎么配合。
- [[kv-prefix-block-hash]]：第⑤题，按整块链式哈希做索引的另一种方案。
- [[kv-prefix-engine]]：第⑧题，把这棵树接进真实的 Transformer 推理循环。

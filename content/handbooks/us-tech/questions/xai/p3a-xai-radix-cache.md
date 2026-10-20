---
id: p3a-xai-radix-cache
section: xai
order: 608
level: A
title: "xAI：Radix Cache：压缩边、分裂与最长前缀"
quick: "插入时先求新序列与边标签的公共前缀，只重合一部分就拆出中间节点；精确查找和最长前缀都只认终结节点，停在边中间不算命中。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · radix-cache"
    url: https://www.1point3acres.com/interview/problems/company/xai/radix-cache
    type: secondary
---

## 题目

为整数 token 序列实现一棵压缩前缀树（radix tree）：支持插入、精确查找、查找最长的已存前缀，以及枚举所有键。这类结构常用来做 LLM 推理里的前缀 KV cache 索引。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

和普通 trie 不同，radix tree 的一条边上存的是一段序列，不是单个 token。插入时最关键的一步是分裂：沿着首 token 找到边，求新序列和边标签的公共前缀长度。

- 公共前缀覆盖了整条边：走到子节点，继续处理剩下的部分。
- 只覆盖了一部分：建一个中间节点，原来的边变成「公共前缀 → 中间节点」，旧后缀连同原来的子节点整体挂到中间节点下面，然后再插新后缀。
- 首 token 根本没有对应的边：直接挂一个叶子，边标签就是剩下的整段。

精确命中和最长前缀是两个不同的接口。分裂会产生不代表任何键的中间节点，所以每个节点要有终结标记，查询也必须记录匹配到了哪里：停在边中间或者停在非终结节点上，都不算命中。

如果真的拿它当 KV cache 用，缓存是否有效还依赖模型版本和上下文（例如系统提示、采样配置），键里要把这些也区分开。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Radix.insert(seq)`：插入一个整数序列。允许空序列作为键，重复插入是幂等的。
- `Radix.contains(seq) -> bool`：`seq` 是否正好是一个已存键。
- `Radix.longest(seq) -> tuple | None`：返回已存键中是 `seq` 前缀的最长那个，没有则返回 `None`。
- `Radix.keys() -> list[tuple]`：列出所有已存键，顺序不作要求。
- 边标签压缩为非空 tuple。只有终结节点代表完整键，查询落在边中间不能当作精确命中。最多 $10^{4}$ 个键，token 总数不超过 $10^{5}$。

### 输入输出示例

```text
insert([1, 2, 3]); insert([1, 2, 4]); insert([1])
contains([1, 2])         -> False    # [1, 2] 只是分裂出来的中间节点
longest([1, 2, 3, 9])    -> (1, 2, 3)
longest([1, 2])          -> (1,)
```

### 解题思路与正确性

插入每一步都沿公共前缀前进。分裂时旧边的后缀连同原来的子节点被完整挂回中间节点，子树内部一点没动，所以已有的键不会丢；新后缀随后从中间节点继续插入。

`longest` 每走完一整条边才前进，且只在到达终结节点时更新答案。这样边中间的位置、分裂出来的非终结节点都不会被误报成已存键。`contains` 就是判断最长已存前缀是否等于整个查询。

### 完整参考实现（Python 3）

```python
class Node:
    def __init__(self):
        self.is_key = False  # 只有终结节点代表一个完整的已存键
        self.edges = {}      # 首个 token -> (边标签 tuple, 子节点)


def common_prefix_length(a, b):
    length = 0
    while length < min(len(a), len(b)) and a[length] == b[length]:
        length += 1
    return length


class Radix:
    """整数序列的压缩前缀树：每条边的标签是一段非空 tuple。"""

    def __init__(self):
        self.root = Node()

    def insert(self, seq):
        rest = tuple(seq)
        node = self.root
        while rest:
            if rest[0] not in node.edges:
                leaf = Node()
                leaf.is_key = True
                node.edges[rest[0]] = (rest, leaf)
                return
            label, child = node.edges[rest[0]]
            shared = common_prefix_length(label, rest)
            if shared < len(label):
                # 只重合了一部分：拆成「公共前缀 -> 中间节点 -> 旧后缀」，旧键原样挂回
                middle = Node()
                middle.edges[label[shared]] = (label[shared:], child)
                node.edges[rest[0]] = (label[:shared], middle)
                child = middle
            node = child
            rest = rest[shared:]
        node.is_key = True  # 重复插入是幂等的

    def longest(self, seq):
        """返回 seq 的前缀中最长的已存键；一个都没有时返回 None。"""
        seq = tuple(seq)
        node = self.root
        pos = 0
        best = () if node.is_key else None
        while pos < len(seq) and seq[pos] in node.edges:
            label, child = node.edges[seq[pos]]
            if seq[pos:pos + len(label)] != label:
                break  # 停在边中间，不算命中
            pos += len(label)
            node = child
            if node.is_key:
                best = seq[:pos]
        return best

    def contains(self, seq):
        return self.longest(seq) == tuple(seq)

    def keys(self):
        """深度优先列出所有已存键。"""
        found = []

        def walk(node, prefix):
            if node.is_key:
                found.append(prefix)
            for label, child in node.edges.values():
                walk(child, prefix + label)

        walk(self.root, ())
        return found
```

### 可执行测试

```python
tree = Radix()
for seq in ([1, 2, 3], [1, 2, 4], [1], []):
    tree.insert(seq)

# [1, 2] 只是分裂出来的中间节点，不是已存键
assert not tree.contains([1, 2])
assert tree.contains([1])
assert tree.contains([])

# 最长前缀只在终结节点更新
assert tree.longest([1, 2, 3, 9]) == (1, 2, 3)
assert tree.longest([1, 2]) == (1,)
assert tree.longest([1, 5]) == (1,)
assert set(tree.keys()) == {(), (1,), (1, 2, 3), (1, 2, 4)}

# 中间节点被补成键；重复插入不产生重复
tree.insert([1, 2])
tree.insert([1, 2])
assert tree.contains([1, 2])
assert sorted(tree.keys()) == [(), (1,), (1, 2), (1, 2, 3), (1, 2, 4)]

# 没有空键时，无公共前缀返回 None
assert Radix().longest([7]) is None
```

### 复杂度与追问

设查询或插入的序列长度为 L。比较次数是 O(L)；不过 Python 的 tuple 切片会复制，最坏情况下（每条边都很短）总共是 O($L^{2}$)。空间和所有键的 token 总数成正比。

- 要严格线性：边标签和查询都用「原序列 + 起止下标」表示，不再切片。
- 这里只是前缀数据结构，不包含真正 KV cache 需要的部分：GPU 块的引用计数、正在被请求使用的节点不能被驱逐、按 LRU 回收叶子等。

## 相关题

- [[xai-prompt-cache]]：系统提示缓存与多租户前缀共享，那张卡讨论的是缓存系统层面的问题，这里只做前缀数据结构。
- [[kv-prefix-radix]]：同样的边分裂，但契约相反：查询停在压缩边中间也返回已算好的部分，不需要终结标记。
- [[kv-prefix-radix-leases]]：补上这里没做的部分：活跃引用、分裂时继承计数、叶子 LRU。
- [[sys-radix-tree]]：SGLang radix cache 的口述版，讲树和 GPU 页怎么配合。
- [[kv-prefix-implementation-index]]：前缀缓存 8 道实现题的入口。

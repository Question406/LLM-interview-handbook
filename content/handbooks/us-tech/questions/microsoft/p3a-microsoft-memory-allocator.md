---
id: p3a-microsoft-memory-allocator
section: microsoft
order: 603
level: A
title: "Microsoft AI / Copilot：MAI 连续内存分配与策略取舍"
quick: "显式维护空闲区间并在释放时合并相邻块，讲清 first-fit 和 best-fit 的区别；先保证接口正确，再用按地址的索引去掉线性扫描。"
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
  - title: "1Point3Acres · Microsoft AI / Copilot · memory-allocator"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/memory-allocator
    type: secondary
---

## 题目

在固定大小的内存池上实现按大小分配和释放，并讨论不同分配策略的取舍。

> 来源：一亩三分地 Microsoft AI / Copilot（MAI）题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

建议分两步走。先用一个有序的空闲区间列表把接口写对：`malloc` 找到块后切分，`free` 把块放回并和左右相邻的空闲块合并。然后再考虑性能，用按地址排序的树（附带子树最大空闲长度）代替线性扫描。

策略上要能讲清两种常见选择：

- first-fit：选地址最小的够用的块，实现简单，查找可以很快停下。
- best-fit：选长度最接近需求的块，剩余块最小，但需要按长度建索引，也容易留下大量很小的碎片。

需要验证的点包括：传入的指针是不是某个已分配块的起点、重复释放如何处理、释放后是否真的合并成了大块，以及碎片率。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Allocator(capacity)`：管理整数地址池 $[0, \text{capacity})$，初始全部空闲。`capacity < 1` 抛 `ValueError`。
- `malloc(size)`：first-fit，返回起点最小、且连续空闲长度至少为 `size` 的块的起点；找不到返回 `None`。`size < 1` 抛 `ValueError`。
- `free(ptr)`：释放 `malloc` 返回的整块，成功返回 `True`；`ptr` 不是某个已分配块的起点，或已经释放过，返回 `False`。释放后与左右相邻的空闲块合并。
- 空闲块用按地址排序的 treap 存，每个节点维护子树中的最大空闲长度，这样 first-fit 不用线性扫描。
- $\text{capacity} \le 10^9$，操作数不超过 $10^5$。treap 的随机优先级用固定 seed 生成，结果可复现。

### 输入输出示例

```text
allocator = Allocator(10)
allocator.malloc(3)   -> 0
allocator.malloc(4)   -> 3
allocator.malloc(4)   -> None   # 只剩 [7, 10) 三个单元
allocator.free(0)     -> True
allocator.free(3)     -> True   # 与 [0, 3) 和 [7, 10) 合并成 [0, 10)
allocator.free(3)     -> False  # 重复释放
allocator.malloc(10)  -> 0
```

### 解题思路与正确性

空闲块按起点地址组织成 BST（这里用 treap 保持期望平衡），每个节点额外记录 `max_size`：它所在子树里最大空闲块的长度。找 first-fit 时从根往下走：左子树的 `max_size` 够大就进左边，因为那里地址更小；否则看当前节点自己够不够；再不行才去右边。每一步都排除了所有地址更小的可行块，所以停下的节点就是起点最小的可行块。

分配时把这个块删掉，剩余部分作为新空闲块插回去。释放时找出地址上紧挨着的前一个和后一个空闲块，只在首尾相接时合并。这样空闲块之间始终互不重叠，而且不会有两个相邻的空闲块没合并，后面申请大块时才不会因为碎片误判失败。

测试用一个逐格记录占用状态的朴素实现做随机对照，1000 次混合操作中每次 `malloc` 的结果都必须一致。

### 完整参考实现（Python 3）

```python
import random


class Node:
    """treap 节点：一个空闲区间 [start, start + size)。按 start 排成 BST，按 priority 排成小根堆。"""

    def __init__(self, start, size, priority):
        self.start = start
        self.size = size
        self.priority = priority
        self.left = None
        self.right = None
        self.max_size = size  # 子树中最大的空闲区间长度


def max_size(node):
    return node.max_size if node else 0


def update(node):
    """子节点变化后重新计算 max_size。"""
    if node:
        node.max_size = max(node.size, max_size(node.left), max_size(node.right))
    return node


def split(node, key):
    """拆成 (start < key 的部分, start >= key 的部分)。"""
    if node is None:
        return None, None
    if node.start < key:
        node.right, right = split(node.right, key)
        return update(node), right
    left, node.left = split(node.left, key)
    return left, update(node)


def merge(left, right):
    """合并两棵 treap，要求 left 中所有 start 都小于 right 中的 start。"""
    if left is None:
        return right
    if right is None:
        return left
    if left.priority < right.priority:
        left.right = merge(left.right, right)
        return update(left)
    right.left = merge(left, right.left)
    return update(right)


def erase(node, key):
    """删除 start == key 的节点（调用方保证它存在）。"""
    if node.start == key:
        return merge(node.left, node.right)
    if key < node.start:
        node.left = erase(node.left, key)
    else:
        node.right = erase(node.right, key)
    return update(node)


class Allocator:
    """地址池 [0, capacity) 上的 first-fit 分配器。"""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.rng = random.Random(3)  # 固定 seed，便于复现
        self.root = None
        self.allocated = {}  # 已分配块：起点 -> 长度
        self._insert_free(0, capacity)

    def _insert_free(self, start, size):
        left, right = split(self.root, start)
        node = Node(start, size, self.rng.random())
        self.root = merge(merge(left, node), right)

    def _first_fit(self, size):
        """返回起点最小、长度 >= size 的空闲节点；调用前已确认存在。"""
        node = self.root
        while True:
            if max_size(node.left) >= size:
                node = node.left  # 左子树地址更小，且里面有足够大的块
            elif node.size >= size:
                return node
            else:
                node = node.right

    def malloc(self, size):
        """分配 size 个单元，返回起点；没有足够大的连续空闲块时返回 None。"""
        if size < 1:
            raise ValueError(f"size must be positive, got {size}")
        if max_size(self.root) < size:
            return None
        block = self._first_fit(size)
        start, total = block.start, block.size
        self.root = erase(self.root, start)
        if total > size:
            self._insert_free(start + size, total - size)
        self.allocated[start] = size
        return start

    def _neighbors(self, ptr):
        """返回起点在 ptr 之前的最后一个空闲块，以及之后的第一个空闲块。"""
        before = after = None
        node = self.root
        while node:
            if node.start < ptr:
                before = node
                node = node.right
            else:
                after = node
                node = node.left
        return before, after

    def free(self, ptr):
        """释放 malloc 返回的块；ptr 非法或重复释放时返回 False。"""
        if ptr not in self.allocated:
            return False
        start = ptr
        size = self.allocated.pop(ptr)
        before, after = self._neighbors(ptr)
        if before and before.start + before.size == start:
            start = before.start
            size += before.size
            self.root = erase(self.root, before.start)
        if after and start + size == after.start:
            size += after.size
            self.root = erase(self.root, after.start)
        self._insert_free(start, size)
        return True
```

### 可执行测试

```python
# 基本分配、空间不足、释放后合并成整块
allocator = Allocator(10)
assert allocator.malloc(3) == 0
assert allocator.malloc(4) == 3
assert allocator.malloc(4) is None
assert allocator.free(0)
assert allocator.free(3)
assert not allocator.free(3)  # 重复释放
assert allocator.malloc(10) == 0

# 和逐格扫描的 first-fit 朴素实现做随机对照
rng = random.Random(8)
capacity = 50
allocator = Allocator(capacity)
cells = [False] * capacity  # True 表示已占用
live = {}
for _ in range(1000):
    if live and rng.random() < 0.4:
        ptr = rng.choice(list(live))
        size = live.pop(ptr)
        assert allocator.free(ptr)
        cells[ptr:ptr + size] = [False] * size
    else:
        size = rng.randrange(1, 12)
        expected = next(
            (i for i in range(capacity - size + 1) if not any(cells[i:i + size])),
            None,
        )
        got = allocator.malloc(size)
        assert got == expected
        if got is not None:
            live[got] = size
            cells[got:got + size] = [True] * size
```

### 复杂度与追问

设空闲块数为 $B$、已分配块数为 $A$。treap 的期望高度是 $O(\log B)$，所以 `malloc` 和 `free` 期望 $O(\log B)$，最坏情况会退化到 $O(B)$。空间是 $O(B + A)$。

- 要 best-fit 怎么办？best-fit 要找长度最接近 `size` 的块，需要再建一个按 (长度, 地址) 排序的索引；每次拆分或合并空闲块时，地址索引和长度索引要同步更新。这份按地址的 first-fit 实现不能直接称作 best-fit。
- 要确定性的最坏界怎么办？把 treap 换成红黑树、AVL 等平衡树；如果地址空间不大，也可以用线段树维护每段区间的最长连续空闲长度。
- first-fit 和 best-fit 哪个碎片少？没有绝对答案。best-fit 留下的剩余块最小，但容易产生大量很小、用不上的碎片；first-fit 实现简单，倾向于把低地址切碎。可以用碎片率（最大空闲块 / 总空闲量）在实际负载上比较。

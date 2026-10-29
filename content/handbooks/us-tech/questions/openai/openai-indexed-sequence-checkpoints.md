---
id: openai-indexed-sequence-checkpoints
section: openai
order: 900
level: A
title: "OpenAI：Indexed sequence、插入与便宜的 checkpoints"
quick: "如果每次 checkpoint 都复制整个数组，保存版本会越来越贵。我会让 checkpoint 只保存一个不可变 root，插入时复制被修改的路径。"
companies:
  - openai
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人报告的二手转述：indexed sequence"
    url: "https://www.reddit.com/r/OfferEngineering/comments/1wzedra/openai_senior_software_engineer_interview_it_felt/"
    type: interview
  - title: "公开题目目录：indexed sequence with checkpoints"
    url: "https://landthelab.com/companies/openai"
    type: secondary
---

## 题目描述

来源：Chill Interview 的公开转述描述了 add(index,value)、get(index) 的 ordered sequence；Land the Lab 公开目录另提到 cheap snapshots。下面的 checkpoint API、索引规则和复杂度目标由手册明确。

### 输入、接口与规则

实现 `IndexedSequence(seed=0)`，初始为空。`add(index,value)` 在当前位置前插入字符串，合法 index 为 0..length；原位置及后续元素右移。`get(index, checkpoint=None)` 读取当前序列或指定历史 checkpoint 的值，合法 index 为 0..length-1；不使用 Python 的负数索引语义，越界抛 IndexError。

`checkpoint()` 返回从 0 递增的整数 ID，后续 add 不得改变已保存的序列。不存在的 checkpoint 抛 IndexError。目标是 checkpoint 时间和新增保存空间 `O(1)`，add/get expected `O(log N)`；可以使用随机平衡树，但需说明 expected 与 worst-case 的差别。不要求删除、覆盖或序列化。实现和测试均需可运行，不能仅列数据结构名称。

### 输入输出示例

```text
add(0,"A"); s=checkpoint(); add(0,"B")
当前 get(0)="B", get(1)="A"；get(0,s)="A"。
```

## 回答思路

> **输入与任务：** 序列索引是元素数量，不是 embedding；历史版本不能被后续插入改变。  
> **做法与原因：** Implicit treap 用 subtree size 定位，path copying 保留旧 root。  
> **正确性检查：** 与 Python list 对照随机插入，重复检查所有旧 checkpoint。

## 解题思路与参考答案

如果每次 checkpoint 都复制整个数组，保存版本会越来越贵。我会让 checkpoint 只保存一个不可变 root，插入时复制被修改的路径。

Implicit treap 不需要给元素永久分配数值 key：每个节点记录左子树大小，就能找到第几个元素。Split 按数量切开，插入新节点后再 merge，旧版本的节点保持不变。

### 完整参考实现

```python
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Node:
    value: str
    priority: float
    left: object = None
    right: object = None
    size: int = 1


def size(node):
    return 0 if node is None else node.size


def rebuild(node, left, right):
    return Node(node.value, node.priority, left, right, 1 + size(left) + size(right))


def split(node, count):
    if node is None:
        return None, None
    left_size = size(node.left)
    if count <= left_size:
        a, b = split(node.left, count)
        return a, rebuild(node, b, node.right)
    a, b = split(node.right, count - left_size - 1)
    return rebuild(node, node.left, a), b


def merge(left, right):
    if left is None:
        return right
    if right is None:
        return left
    if left.priority <= right.priority:
        return rebuild(left, left.left, merge(left.right, right))
    return rebuild(right, merge(left, right.left), right.right)


class IndexedSequence:
    def __init__(self, seed=0):
        self.root = None
        self.snapshots = []
        self.rng = random.Random(seed)

    def add(self, index, value):
        if not 0 <= index <= size(self.root):
            raise IndexError(index)
        left, right = split(self.root, index)
        node = Node(value, self.rng.random())
        self.root = merge(merge(left, node), right)

    def checkpoint(self):
        self.snapshots.append(self.root)
        return len(self.snapshots) - 1

    def get(self, index, checkpoint=None):
        if checkpoint is None:
            node = self.root
        else:
            if not 0 <= checkpoint < len(self.snapshots):
                raise IndexError(checkpoint)
            node = self.snapshots[checkpoint]
        if not 0 <= index < size(node):
            raise IndexError(index)
        while node is not None:
            left_size = size(node.left)
            if index < left_size:
                node = node.left
            elif index == left_size:
                return node.value
            else:
                index -= left_size + 1
                node = node.right
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
seq = IndexedSequence()
seq.add(0, "A")
snapshot = seq.checkpoint()
seq.add(0, "B")
assert [seq.get(i) for i in range(2)] == ["B", "A"]
assert seq.get(0, snapshot) == "A"
reference, saved = [], []
seq = IndexedSequence(seed=27)
rng = random.Random(19)
for turn in range(600):
    index = rng.randrange(len(reference) + 1)
    value = str(turn % 17)
    reference.insert(index, value)
    seq.add(index, value)
    if turn % 29 == 0:
        saved.append((seq.checkpoint(), reference.copy()))
    probe = rng.randrange(len(reference))
    assert seq.get(probe) == reference[probe]
assert [seq.get(i) for i in range(600)] == reference
for snapshot, values in saved:
    assert [seq.get(i, snapshot) for i in range(len(values))] == values
try:
    seq.get(-1)
except IndexError:
    pass
else:
    raise AssertionError("negative indices are outside this API")
print("OpenAI persistent indexed sequence: passed")
```

## 复杂度与追问

随机 priorities 下 add/get expected `O(log N)`，每次插入新增 expected `O(log N)` nodes；checkpoint 为 `O(1)`。最坏树高可达 N。长期保留所有版本会持续占用内存，删除 checkpoint 与并发读写是额外设计。

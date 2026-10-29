---
id: dt-buffer-shuffle-code
section: tech-screen
order: 43
level: S
title: CoderPad：无限数据流如何用固定缓冲区近似打乱？
quick: 维护固定容量缓冲区，新元素到达时随机交付一个旧元素并替换它，结束时随机清空。这样每条数据恰好交付一次且内存有界，但小缓冲区无法产生全局均匀排列。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Python random
    url: 'https://docs.python.org/3/library/random.html'
    type: primary
  - title: PyTorch Dataset and DataLoader
    url: 'https://docs.pytorch.org/docs/2.14/data.html'
    type: primary
---

## 题目描述

原创流式练习；建议限时 20 分钟。输入只能遍历一次，不能先全部读入内存。你要实现有界缓冲区的近似随机打乱，不是全局等概率 shuffle。

### 输入与接口

实现生成器 `buffer_shuffle(items, buffer_size, rng)`。items 为有限或无限 iterable，buffer_size 为正整数，rng 为注入的 `random.Random` 实例。元素是任意 Python 对象，允许重复。

### 输出与约束

先填满 buffer_size 个元素；之后每读到一个新元素，使用 `rng.randrange(len(buffer))` 选一个旧元素输出，再用新元素替换它。流结束后，重复随机选择并 `pop` 缓冲区元素输出，直到清空。流短于缓冲区时，直接进入清空阶段。相同输入与 RNG 初始状态给出同样输出；不得调用全局随机数，不得二次遍历，缓冲区最多保存 buffer_size 个元素，另允许常数个临时变量。

### 示例

```text
items=[1,2,3], buffer_size=1 -> [1,2,3]
空流 -> []
容量大于1时，具体输出由给定RNG决定，所有元素及重复次数均保留。
```

## 解题思路与参考答案

容量填满后，每次只随机交付当前缓冲区中的一个旧样本，再把新样本放进去。按约定清空尾部用 pop，最坏总搬移成本还与缓冲区大小有关。

```python
def buffer_shuffle(items, buffer_size, rng):
    buffer = []
    for item in items:
        if len(buffer) < buffer_size:
            buffer.append(item)
            continue
        index = rng.randrange(len(buffer))
        outgoing = buffer[index]
        buffer[index] = item
        yield outgoing
    while buffer:
        yield buffer.pop(rng.randrange(len(buffer)))
```

处理 N 个有限输入时，主循环为 $O(N)$，尾部随机 pop 因列表搬移最坏为 $O(\min(N,B)^2)$，空间为 $O(B)$。若允许改变题目约定，可用末项交换后 pop，把尾部清空改成线性时间；固定 seed 的具体排列会改变。

## 简单测试怎么写

将实现与以下测试保存为 `solution.py`，运行 `python3 solution.py`。用 Counter 检查重复次数；计数生成器检查第一次交付之前没有读完整条流。

```python
import random
from collections import Counter

assert list(buffer_shuffle([1, 2, 3], 1, random.Random(0))) == [1, 2, 3]
assert list(buffer_shuffle([], 4, random.Random(0))) == []
values = [1, 1, 2, 3, 4]
a = list(buffer_shuffle(iter(values), 3, random.Random(9)))
b = list(buffer_shuffle(iter(values), 3, random.Random(9)))
assert a == b
assert Counter(a) == Counter(values)
seen = []


def source():
    for i in range(100):
        seen.append(i)
        yield i


stream = buffer_shuffle(source(), 4, random.Random(0))
first = next(stream)
assert len(seen) == 5
assert first in range(4)
assert sorted([first, *stream]) == list(range(100))
```

## 面试追问

**这是全局均匀打乱吗？** 不是。前几个输出不可能包含很远之后才到达的元素。若源按语言或站点长段排列，小缓冲区会保留局部相关性，需要分片级打乱和跨来源交织。

**与水库 sampling 有什么不同？** 水库 sampling 保留全流的固定数量样本；这里要最终输出每一条数据，不是只留下一个随机子集。

**精确恢复需要什么？** 源位置、缓冲区内容、RNG 状态与数据版本。只恢复源 offset 会丢掉尚未输出的旧元素。

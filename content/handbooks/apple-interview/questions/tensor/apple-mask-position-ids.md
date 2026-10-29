---
id: apple-mask-position-ids
section: tensor
order: 1
level: S
title: cumsum 入门：从 padding mask 生成 position IDs
quick: >-
  对每行有效位置做 cumsum 后减一，再把无效位置设为 -1。按位置是否有效计数，不根据 token ID 猜 padding；同一实现支持左
  padding、右 padding 及中间空位。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - Cumsum 矩阵 Mask
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: PyTorch cumsum
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.cumsum.html'
    type: primary
---

## 题目描述

本题是 Apple 面试备考的原创 tensor 练习。建议限时 15 分钟。

### 输入与接口

实现 `position_ids_from_mask(valid)`。valid 是形状 `[B,T]` 的 bool PyTorch tensor，True 表示真实 token，False 表示 padding。B、T 可以为 0；允许左 padding、右 padding、中间空位和整行无有效 token。

### 输出与约束

返回同设备 long tensor `[B,T]`。每行有效 token 按出现顺序从 0 编号，无效位置为 -1。不修改输入，不写逐行或逐 token 的 Python 循环，不通过 NumPy 转换。编号表示有效 token 的顺序，不是原始列下标。

### 示例

```text
valid=[[False,False,True,True], [True,False,True,False], [False,False,False,False]]
返回 =[[-1,-1,0,1], [0,-1,1,-1], [-1,-1,-1,-1]]
```

## 解题思路与参考答案

布尔值转整数后，每经过一个有效 token，累计值增加一。减一变成从零开始，再覆盖无效位置。只减一不覆盖 padding，会让右侧 padding 继承最后一个有效编号。

```python
import torch


def position_ids_from_mask(valid):
    positions = valid.to(torch.long).cumsum(dim=-1) - 1
    return positions.masked_fill(~valid, -1)
```

时间与输出空间为 $O(BT)$。-1 是本题无效位置的标记，不能直接作为 embedding 索引使用；接入模型时需按接口约定替换占位值，并继续使用 attention mask。

## 简单测试怎么写

将实现和测试保存为 `solution.py`，使用含 PyTorch 的 Python 运行。先手算包含空位的例子，再检查全空行、零宽度和零 batch。

```python
valid = torch.tensor(
    [
        [False, False, True, True],
        [True, False, True, False],
        [False, False, False, False],
    ]
)
original = valid.clone()
actual = position_ids_from_mask(valid)
assert actual.tolist() == [[-1, -1, 0, 1], [0, -1, 1, -1], [-1, -1, -1, -1]]
assert actual.dtype == torch.long and actual.device == valid.device
assert torch.equal(valid, original)
assert position_ids_from_mask(torch.ones(2, 3, dtype=torch.bool)).tolist() == [
    [0, 1, 2],
    [0, 1, 2],
]
assert position_ids_from_mask(torch.empty(2, 0, dtype=torch.bool)).shape == (2, 0)
assert position_ids_from_mask(torch.empty(0, 3, dtype=torch.bool)).shape == (0, 3)
```

## 面试追问

**valid 是 token_id!=0 可以吗？** 只有数据契约保证 0 专门表示 padding 时才成立。真实 token 也可能使用同一 ID，应优先使用显式长度或 mask。

**连续 decode 怎么编号？** 要接上每条序列此前有效 token 数，不能每个新块都从零开始；还应区分缓存物理位置和逻辑 position ID。

**packed 多文档呢？** 本题只在每行重置，不在 document boundaries 重置。见 `apple-starts-doc-mask`，需要加入文档起始信息。

---
id: apple-starts-doc-mask
section: tensor
order: 2
level: S
title: cumsum 与 cummax：从文档起始标记构造 doc IDs、段内位置和 mask
quick: >-
  对 starts 做 cumsum 得到文档编号，用 cummax 传播最近起点下标，再相减得到段内位置。可见性是同文档、key 不晚于
  query、两端有效三个条件同时成立。
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
  - title: PyTorch cummax
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.cummax.html'
    type: primary
---

## 题目描述

原创练习。建议限时 25 分钟。若干独立文档打包在一行，你只知道有效 token 和文档起点，要生成三种训练元信息。

### 输入与接口

实现 `layout_from_starts(starts, valid)`。两项都是同设备 `[B,T]` bool tensor，B、T 可以为 0。每行有效 token 组成一个连续区间，可带左或右 padding，也允许全空。starts 只会在有效位置为 True，且非空行的第一个有效位置一定为 True；后续 True 表示新文档开始。

### 输出与约束

返回 `(doc_ids, positions, keep)`。前两项是同设备 long tensor `[B,T]`：doc_ids 按每行文档从 0 编号，positions 在每个文档内从 0 编号，padding 均为 -1。keep 为 bool `[B,T,T]`，行是 query、列是 key；仅同文档的真实位置可见，且 key 不晚于 query。padding query 整行 False。本函数只生成 mask，不执行 softmax。不修改输入，禁止逐行/逐 token 循环，使用 tensor 运算。

### 示例

```text
starts=[[False,True,False,True,False,False]]
valid =[[False,True,True,True,True,False]]
doc_ids=[[-1,0,0,1,1,-1]]
positions=[[-1,0,1,0,1,-1]]
keep仅在(1,1),(2,1),(2,2),(3,3),(4,3),(4,4)为True。
```

## 解题思路与参考答案

起点累计数减一就是文档 ID。段内位置需要知道最近起点所在的原始列：让起点位置写自己的列下标，其他位置写 0，再用 cummax 把最近起点向右传播。因为起点下标递增，累计最大值等于最近起点。

```python
import torch


def layout_from_starts(starts, valid):
    length = starts.shape[-1]
    columns = torch.arange(length, device=starts.device)
    docs = (starts.long().cumsum(-1) - 1).masked_fill(~valid, -1)
    anchors = torch.where(starts, columns, torch.zeros_like(columns))
    latest_start = anchors.cummax(dim=-1).values
    positions = (columns - latest_start).masked_fill(~valid, -1)
    same_doc = docs[:, :, None] == docs[:, None, :]
    causal = columns[:, None] >= columns[None, :]
    keep = same_doc & valid[:, :, None] & valid[:, None, :] & causal
    return docs, positions, keep
```

编号成本为 $O(BT)$，稠密 keep 的时间和输出空间为 $O(BT^2)$。大型训练应考虑 varlen 内核或分块表示。只有 doc ID 相等还不够，因为 padding 都标成 -1，会被错误地判断为同文档。

## 简单测试怎么写

实现和测试放入 `solution.py`，运行 `python3 solution.py`。从题面列出可见坐标，再测试单 token 文档、全 padding 与空形状。

```python
starts = torch.tensor([[False, True, False, True, False, False]])
valid = torch.tensor([[False, True, True, True, True, False]])
docs, pos, keep = layout_from_starts(starts, valid)
assert docs.tolist() == [[-1, 0, 0, 1, 1, -1]]
assert pos.tolist() == [[-1, 0, 1, 0, 1, -1]]
expected = torch.zeros(1, 6, 6, dtype=torch.bool)
expected[0, [1, 2, 2, 3, 4, 4], [1, 1, 2, 3, 3, 4]] = True
assert torch.equal(keep, expected)
s = torch.tensor([[True, True, True], [False, False, False]])
v = torch.tensor([[True, True, True], [False, False, False]])
d, p, k = layout_from_starts(s, v)
assert d.tolist() == [[0, 1, 2], [-1, -1, -1]]
assert p.tolist() == [[0, 0, 0], [-1, -1, -1]]
assert torch.equal(k[0], torch.eye(3, dtype=torch.bool))
assert not k[1].any()
empty = torch.empty(2, 0, dtype=torch.bool)
assert layout_from_starts(empty, empty)[2].shape == (2, 0, 0)
empty_batch = torch.empty(0, 3, dtype=torch.bool)
assert layout_from_starts(empty_batch, empty_batch)[0].shape == (0, 3)
assert torch.equal(starts, torch.tensor([[False, True, False, True, False, False]]))
```

## 面试追问

**全 False 的 query 行怎么做 attention？** 不能直接对全负无穷 logits 用普通 softmax，会得到 NaN。调用方需使用可靠的安全处理，并丢弃无效 query 输出。本题与 `dt-packed-attention-code` 的 padding 对角占位规则不同，接入时必须选定同一契约。

**valid 中间有空位会怎样？** 题目保证连续有效区间；若放宽，positions 应明确计实际列距离还是有效 token 顺序，不能直接外推本实现。

**loss mask 能代替 keep 吗？** 不能。loss mask 只决定哪些输出受监督，keep 决定每个输出看见哪些上下文，跨文档读取会改变条件分布。

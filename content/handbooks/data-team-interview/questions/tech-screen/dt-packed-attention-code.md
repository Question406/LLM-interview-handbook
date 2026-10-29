---
id: dt-packed-attention-code
section: tech-screen
order: 47
level: S
title: CoderPad：构造 packed causal attention mask，padding query 怎么处理？
quick: >-
  真实 query 只能看到同文档、不晚于自己的真实 key。padding query 本题只允许看自身以避免全屏蔽行，且其输出与 loss
  必须丢弃；注意不同 PyTorch attention 接口的 bool mask 语义可能相反。
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
  - title: PyTorch scaled_dot_product_attention
    url: >-
      https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题目描述

原创 tensor 编程练习；建议限时 20 分钟。多个文档打包到同一行，你要构造阻止跨文档信息 leakage 的 attention mask。

### 输入与接口

实现 `packed_allow_mask(doc_ids)`。doc_ids 为 `[B,T]` long tensor，B、T 为正。非负 ID 表示真实文档，同一行同一 ID 对应一个连续区间，不会在别处复用；-1 表示右侧 padding，允许某行全为 padding。不同 batch 行可以复用 ID。

### 输出与约束

返回同设备 bool tensor `[B,T,T]`，第二维是 query 位置，第三维是 key 位置，True 表示允许注意。真实 query i 只允许关注真实 key j，且 doc_ids 相同并满足 j<=i。padding query 只允许关注自己的对角位置，这是数值占位规则，调用方必须丢弃 padding 输出并屏蔽对应 loss。不修改输入。不要调用循环逐元素填充。

### 示例

```text
doc_ids=[[2,2,5,-1]]
allow=[[[True,False,False,False],
        [True,True,False,False],
        [False,False,True,False],
        [False,False,False,True]]]
```

## 解题思路与参考答案

分别构造同文档关系、真实位置关系和下三角 causal 关系，再合并 padding query 的对角占位。mask 只管能看谁，position_ids 与 loss mask 需要另行构造。

```python
import torch


def packed_allow_mask(doc_ids):
    length = doc_ids.shape[1]
    real = doc_ids >= 0
    same = doc_ids[:, :, None] == doc_ids[:, None, :]
    causal = torch.ones(length, length, dtype=torch.bool, device=doc_ids.device).tril()
    allowed = same & real[:, :, None] & real[:, None, :] & causal
    diagonal = torch.eye(length, dtype=torch.bool, device=doc_ids.device)
    return allowed | ((~real)[:, :, None] & diagonal)
```

时间与输出空间为 $O(BT^2)$，大规模训练不应默认生成这种稠密 mask，可以采用支持变长序列的 attention 内核或分块表示。对多头 SDPA 通常需变成 `[B,1,T,T]` 以正确广播。

## 简单测试怎么写

实现与测试放入 `solution.py`，运行 `python3 solution.py`。先检查题面 matrix，再用均匀 attention 的实际输出确认跨文档隔离。此处 SDPA 的 bool mask 中 True 表示允许。

```python
import torch.nn.functional as F

ids = torch.tensor([[2, 2, 5, -1]])
allow = packed_allow_mask(ids)
expected = torch.tensor(
    [
        [
            [True, False, False, False],
            [True, True, False, False],
            [False, False, True, False],
            [False, False, False, True],
        ]
    ]
)
assert torch.equal(allow, expected)
assert allow.shape == (1, 4, 4) and allow.dtype == torch.bool
q = torch.zeros(1, 1, 4, 1)
k = torch.zeros_like(q)
v = torch.tensor([[[[2.0], [4.0], [100.0], [999.0]]]])
out = F.scaled_dot_product_attention(q, k, v, attn_mask=allow[:, None], dropout_p=0.0)
assert torch.allclose(out.flatten(), torch.tensor([2.0, 3.0, 100.0, 999.0]))
assert torch.equal(
    packed_allow_mask(torch.tensor([[-1, -1]])), torch.eye(2, dtype=torch.bool)[None]
)
assert torch.equal(ids, torch.tensor([[2, 2, 5, -1]]))
```

## 面试追问

**loss mask 正确就不会 leakage 了吗？** 不够。后一个文档仍可能通过 attention 看到前一个文档，改变输入条件；需要同时处理可见性和监督位置。

**所有 attention API 都是 True 表示允许吗？** 不是。例如部分 MultiheadAttention mask 采用 True 表示屏蔽。接入前必须核对具体接口并做最小数值验证。

**padding 自 attention 不算 leakage 吗？** 这是本题对无效 query 的占位，不允许真实 query 看到 padding。只有丢弃 padding 输出且不计入 loss 才满足约定；其他内核也可采用不同的安全处理。

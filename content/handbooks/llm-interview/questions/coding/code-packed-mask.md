---
id: code-packed-mask
section: coding
order: 46
level: A
title: 手写 packed sequence 的文档边界 mask：`cu_seqlens` 怎么变成 keep 矩阵
quick: "用前缀和 `cu_seqlens` 给每个位置算出 doc id，keep 条件是同一文档且 $j\\le i$。跨文档位置设为 $-\\infty$，否则后一条样本能看到前一条。"
tags:
  - Packing
  - Attention
  - Mask
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
---

packing 将多条样本拼接起来，以减少 padding。计算损失时也要按文档划分，将 padding 和文档衔接处的 label 设为 `ignore_index`。如果只加因果 mask，不检查文档边界，后面的输入提示（prompt）就能访问前一条样本，造成信息泄漏。

## 从 `cu_seqlens` 到 doc id

`cu = [0, 3, 7]` 表示两段，长度 3 和 4。`repeat_interleave` 得到 `[0,0,0,1,1,1,1]`。

$$
\mathrm{keep}(i,j)=\big[\mathrm{doc}(i)=\mathrm{doc}(j)\big]\land[j\le i].
$$

```python
import torch

def cu_seqlens_to_doc(cu):
    lens = cu[1:] - cu[:-1]
    return torch.repeat_interleave(torch.arange(len(lens), device=cu.device), lens)

def packed_keep(cu):
    doc = cu_seqlens_to_doc(cu)
    T = doc.numel()
    q = torch.arange(T, device=cu.device)
    return (doc[:, None] == doc[None, :]) & (q[:, None] >= q[None, :])
```

生产实现不需要创建完整的 $[T,T]$ 矩阵，FlashAttention 的 varlen kernel 会根据 `cu_seqlens` 分段计算。白板上可以先写出 dense mask，再解释实际 kernel 如何避免创建它。RoPE 的 position 必须按段内从 0 重数，或用每条样本自己的 position id，不能用拼接后的列下标。

## 追问

- **loss 怎么 shift？** 每段自己 `logits[:-1]` 对 `idx[1:]`。不能让段尾预测下一段的第一个 token，这个 label 应被屏蔽。
- **和 left padding batch？** padding 是按 batch 维对齐；packing 是沿时间维拼接。两者都能去 pad，packing 的有效 token 比例更高。
- **逐 token 生成（decode） 还 packing 吗？** 一般不。推理走 continuous batching + paged KV，见 `code-paged-kv-cow`。

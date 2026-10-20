---
id: code-alibi
section: coding
order: 45
level: A
title: 手写 ALiBi：斜率怎么排，bias 加在 scores 上，decode 用绝对距离
quick: "ALiBi 不改 $Q,K$，只在 softmax 前给 scores 加 $-m_h(q-k)$，第 $h$ 头斜率 $m_h=2^{-8h/H}$。decode 时 query 位置用当前绝对位置，不能当成 0。"
tags:
  - ALiBi
  - Position
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Train Short, Test Long: Attention with Linear Biases"
    url: https://arxiv.org/abs/2108.12409
    type: primary
---

和 RoPE 对比着考：RoPE 转 $Q,K$；ALiBi 只改 logits。BLOOM / MPT 用 ALiBi。常见误区是：把距离写成 $|q-k|$ 却在 causal 里让未来位置也有限（未来应先被 $-\infty$ 打掉）；或在 decode 时把 query 位置当成 0，bias 全变成 $0,-m,-2m,\ldots$ 的反序。

## 斜率与 bias

$H$ 是 2 的幂时：

$$
m_h=2^{-8h/H},\quad h=1,\ldots,H.
$$

$H=8$ 就是 $1/2,1/4,\ldots,1/256$。非 2 的幂按论文附录从 $2H$ 那组里抽奇数项补齐，白板提一句即可。

$$
b_{h,q,k}=-m_h\cdot(q-k).
$$

causal 下 $q\ge k$，距离非负，越远越负。加在 $QK^\top/\sqrt{d}$ 之后、softmax 之前。

```python
import math
import torch

def alibi_slopes(n_heads):
    n = 2 ** int(math.floor(math.log2(n_heads)))
    step = 2 ** (-8 / n)
    slopes = [step ** (i + 1) for i in range(n)]
    if n < n_heads:
        extra = alibi_slopes(2 * n)[1::2][: n_heads - n]
        slopes = slopes + extra
    return torch.tensor(slopes[:n_heads])

def alibi_bias(q_pos, k_pos, slopes):
    # slopes: [H]；q_pos: [Tq], k_pos: [Tk] → [H, Tq, Tk]
    dist = q_pos[:, None] - k_pos[None, :]
    return -slopes[:, None, None] * dist.to(slopes.dtype)
```

Prefill 处理输入并建立缓存时：`q_pos = k_pos = arange(T)`。decode：`q_pos = [S-1]`，`k_pos = arange(S)`。KV cache 里的 K 不用重新乘斜率，因为 bias 是现场算的。

## 追问

- **为什么能外推？** 距离是相对的，训练 1k、推理 8k 时只是距离更大、惩罚更重，没有没见过的绝对位置 id。
- **和 RoPE 能一起用吗？** 一般二选一。再叠一层会重复编码距离。
- **head 0 斜率最大？** 是，近距离头更尖。斜率小的头看得更远。

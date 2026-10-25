---
id: code-flash-decode
section: coding
order: 52
level: S
title: 手写 FlashDecoding 的 split-K：各片本地 softmax，再用 lse 合并
quick: "decode 时只有 1 个 query，就把长 KV 沿 $S$ 切成几片，各片算本地 softmax，得到输出 $O_g$ 和 $\\mathrm{lse}_g$。合并时按 $e^{\\mathrm{lse}_g}$ 加权（先减掉最大的 lse），各片 $O_g$ 直接平均是错的。"
tags:
  - FlashDecoding
  - Online Softmax
  - Decode
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Flash-Decoding for long-context inference
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding.html
    type: primary
---

## 题目描述

实现单个新 query 对较长历史 K/V 的 attention，并支持把 key/value 序列拆成若干片独立处理后合成结果。分片个数不能改变数学上的注意力输出。

### 接口与张量

- `splitk_attn(q,k,v,n_split)`：q 为 `[B,H,1,D]`，k、v 为 `[B,H,S,D]`，S 与 `n_split` 均为正整数；返回 `[B,H,1,D]`。输出定义为按 `QK^T/sqrt(D)` 在全部 S 个 key 上归一化后，对 V 的加权结果，不额外加入 mask。
- `online_merge(o1,lse1,o2,lse2)`：输入两组互不重叠 key 分片各自的局部输出 `[B,H,1,D]` 与该组分数的 log-sum-exp `[B,H,1]`，返回两组合并后的输出和 log-sum-exp。

分片大小不整除 S，以及 `n_split` 大于 S 都是合法情况；没有数据的片不能改变结果。本卡仅需 CPU 数值正确性，不要求编写实际 Flash-Decoding GPU kernel。

### 示例

```text
B=H=D=1，q=[0]，k的5个序列值均为0，v=[1,2,3,4,5]
splitk_attn(q,k,v,1) -> 序列输出[3]
splitk_attn(q,k,v,2) -> 序列输出[3]
splitk_attn(q,k,v,8) -> 序列输出[3]
```

返回完整的加权平均，不返回某一片的单独结果。

## 解题思路与参考答案

FlashDecoding 的 split-K 是把长 KV cache 沿序列维 $S$ 切成几片，每片各自算一个局部 softmax 的输出 $O_g$ 和它的 $\mathrm{lse}_g$，最后按 $e^{\mathrm{lse}_g}$ 加权合并。之所以要切，是因为 decode 时只有一个 query：普通 decode 每步拿 $q$ 和整段 cache 算注意力（见 `code-kv-cache-step`），$S$ 很大时一个 query 吃不满 GPU，$S$ 这一维又没有并行。切开之后多个 CTA 各算一片，再做一次归约。训练用的 tiled FA 见 `code-flash-attn-fwd`，这张卡只写 decode 的合并。

比如一片的 key 恰好都和 query 很相关，另一片几乎无关。直接把两片的 $O_g$ 平均，无关那片会拿到一半的权重；按 $e^{\mathrm{lse}_g}$ 加权，它的贡献就接近 0，和一次性算完整个 $S$ 的结果一致。

## 两片怎么合并

片 $g$ 已经得到归一化的输出 $O_g$ 和 $\mathrm{lse}_g=\log\sum_j e^{s_{gj}}$。

$$
m=\max(\mathrm{lse}_1,\mathrm{lse}_2),\quad
O=\frac{O_1 e^{\mathrm{lse}_1-m}+O_2 e^{\mathrm{lse}_2-m}}{e^{\mathrm{lse}_1-m}+e^{\mathrm{lse}_2-m}}.
$$

$$
\mathrm{lse}\leftarrow m+\log\big(e^{\mathrm{lse}_1-m}+e^{\mathrm{lse}_2-m}\big).
$$

多片的话，从左到右逐片 fold 就行。权重必须是 $e^{\mathrm{lse}_g}$。

```python
import math
import torch

def softmax_stable(x, dim=-1):
    z = x.float() - x.float().amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    return (p / p.sum(dim=dim, keepdim=True)).to(x.dtype)

def online_merge(o1, lse1, o2, lse2):
    m = torch.maximum(lse1, lse2)
    a1, a2 = (lse1 - m).exp(), (lse2 - m).exp()
    o = (o1 * a1.unsqueeze(-1) + o2 * a2.unsqueeze(-1)) / (a1 + a2).unsqueeze(-1)
    return o, m + (a1 + a2).log()

def splitk_attn(q, k, v, n_split):
    # q: [B,H,1,D]；沿 S 切开
    S, scale = k.size(2), 1.0 / math.sqrt(q.size(-1))
    width = (S + n_split - 1) // n_split
    o = lse = None
    for i in range(n_split):
        sl = slice(i * width, min((i + 1) * width, S))
        if sl.start >= S:
            break
        scores = (q @ k[:, :, sl].transpose(-1, -2)) * scale
        block_lse = torch.logsumexp(scores.float(), dim=-1)
        block_o = softmax_stable(scores, dim=-1) @ v[:, :, sl]
        o, lse = (block_o, block_lse) if o is None else online_merge(o, lse, block_o, block_lse)
    return o
```

默写完的自检是：切成 $G$ 片的结果必须和一次算完整个 $S$ 一致。$S$ 不能整除时出现的空片直接跳过。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

Q/K 全零时输出就是 V 的均值。历史长度 5 分成 1、2、8 份，覆盖整段、尾块不满与分片数大于长度三种情况，结果都应为 3。

```python
q = torch.zeros(1, 1, 1, 1)
k = torch.zeros(1, 1, 5, 1)
v = torch.arange(1., 6.).view(1, 1, 5, 1)
for splits in (1, 2, 8):
    torch.testing.assert_close(splitk_attn(q, k, v, splits), torch.tensor([[[[3.]]]]))
print("simple tests passed")
```

## 追问

**为什么只有 decode 才需要 split-K？**
prefill 处理整段输入时，$T$ 足够大，按 $Q$ 的行切就能吃满 SM。decode 时 $T=1$，只能切 $S$。

**为什么要保留 lse？**
backward 和跨片合并都要用它。只存 $O$ 是合并不了的。

**和 paged KV 怎么配合？**
每个 physical block 就是一片，gather 之后再 merge。手写时用连续的 slice 就够了。

---
id: code-linear-attn
section: coding
order: 26
level: A
title: 手写 causal linear attention：并行形式和 O(1) 状态递推要对上
quick: "把 softmax 换成非负核 $\\phi(q)^\\top\\phi(k)$。decode 时只维护 $S_t=\\sum\\phi(k)v^\\top$ 和 $z_t=\\sum\\phi(k)$，输出 $\\phi(q)^\\top S_t/\\phi(q)^\\top z_t$，状态大小与长度无关。"
tags:
  - Linear Attention
  - RNN
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention"
    url: https://arxiv.org/abs/2006.16236
    type: primary
---

常见错法有两个。一是 $\phi(Q)\phi(K)^\top$ 算完又套一层 softmax，那就回到了普通 attention；二是只写分子 $\sum\phi(q)^\top\phi(k)v$，漏了分母归一化 $\sum\phi(q)^\top\phi(k)$，输出尺度会随序列长度变化。面试官要看的是：同一个模型能写成并行（训练用）和递推（用于逐 token 生成 decode）两种形式，而且数值一致。softmax 版本见 `code-attention`。

## 公式

第 $t$ 个位置的输出：

$$
o_t=\frac{\phi(q_t)^\top\sum_{j\le t}\phi(k_j)v_j^\top}{\phi(q_t)^\top\sum_{j\le t}\phi(k_j)}
=\frac{\phi(q_t)^\top S_t}{\phi(q_t)^\top z_t},\quad
S_t=S_{t-1}+\phi(k_t)v_t^\top,\ z_t=z_{t-1}+\phi(k_t)
$$

关键在结合律：先算 $\phi(K)^\top V$ 这个 $[d_k,d_v]$ 的小矩阵，就不用算 $[T,T]$。因果注意力只能累加当前位置及之前的项，因此需要前缀和，也就能写成逐步更新状态的递推。

```python
import torch
import torch.nn.functional as F

def phi(x):
    return F.elu(x) + 1                                          # > 0, keeps denominator positive

def linear_attn_masked(q, k, v, eps=1e-6):
    # q,k: [B,H,T,Dk], v: [B,H,T,Dv]; O(T^2), for checking only
    q, k = phi(q), phi(k)
    T = q.shape[2]
    a = q @ k.transpose(-2, -1)                                  # [B,H,T,T], no softmax
    a = a.masked_fill(~torch.tril(torch.ones(T, T, dtype=torch.bool, device=q.device)), 0.0)
    return (a @ v) / (a.sum(-1, keepdim=True) + eps)

def linear_attn_cumsum(q, k, v, eps=1e-6):
    q, k = phi(q), phi(k)
    S = torch.einsum("bhtd,bhte->bhtde", k, v).cumsum(2)         # [B,H,T,Dk,Dv]
    z = k.cumsum(2)                                              # [B,H,T,Dk]
    num = torch.einsum("bhtd,bhtde->bhte", q, S)
    den = (q * z).sum(-1, keepdim=True)
    return num / (den + eps)

def linear_attn_step(q_t, k_t, v_t, S, z, eps=1e-6):
    # q_t,k_t: [B,H,Dk], v_t: [B,H,Dv], S: [B,H,Dk,Dv], z: [B,H,Dk]
    q_t, k_t = phi(q_t), phi(k_t)
    S = S + k_t[..., :, None] * v_t[..., None, :]
    z = z + k_t
    num = torch.einsum("bhd,bhde->bhe", q_t, S)
    den = (q_t * z).sum(-1, keepdim=True)
    return num / (den + eps), S, z
```

decode 时从 `S = zeros(B,H,Dk,Dv)`、`z = zeros(B,H,Dk)` 开始，每来一个 token 就调用一次 `linear_attn_step`。

## 和 KV cache 对比

softmax attention 的 decode 要保存所有历史 $k,v$（见 `arch-kv-cache`），第 $t$ 步读 $O(td)$ 的 cache，显存随长度线性增长。linear attention 把全部历史压进 $S_t$ 和 $z_t$，每层每头只有 $d_k d_v+d_k$ 个数，和 $t$ 无关，每步计算也是常数。代价是表达力：固定大小的状态没法像 softmax 那样精确回看任意一个旧 token，长上下文检索类任务通常更弱。

`linear_attn_cumsum` 把 $[B,H,T,D_k,D_v]$ 整个物化了，T 长时显存吃不消，实际训练用 chunk 形式：块内用 masked 矩阵乘，块间传递状态 $S$。Mamba、RetNet 这类模型也是"训练可并行、推理是固定大小状态的递推"这一思路，只是状态的更新规则不同（比如 RetNet 给状态乘衰减因子），细节不在本题展开。

## 追问

- **为什么 $\phi$ 要非负？** 分母 $\phi(q)^\top z$ 是注意力权重之和，权重必须非负，否则分母可能接近 0 或变号，导致数值不稳定。$\mathrm{elu}+1$ 恒大于 0，梯度也不会像 ReLU 那样在负半轴变成 0。
- **复杂度？** 并行 masked 形式 $O(T^2d)$；递推/chunk 形式 $O(Td_kd_v)$。$T\gg d$ 时才划算。
- **为什么不能直接去掉 softmax 不加 $\phi$？** $q^\top k$ 可以为负，权重和可能为 0，归一化没有意义。
- **训练时用递推形式行不行？** 能算对，但要按时间步串行，GPU 利用率很低。训练用并行或 chunk 形式，推理用递推，两者数学上等价。
- **能和 KV cache 共存吗？** 有些混合架构部分层用 softmax attention（带 KV cache），部分层用线性/状态空间层，用来在显存和长程检索能力之间折中。

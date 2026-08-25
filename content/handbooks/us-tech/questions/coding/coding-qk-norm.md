---
id: coding-qk-norm
section: coding
order: 30
level: A
title: 白板：QK RMSNorm 再 RoPE，Qwen / 部分 Llama 变体怎么写
quick: >-
  对每个 head 的 $q,k$ 沿 $D$ 做 RMSNorm（通常有 $\gamma$，无 $\beta$），**然后**再 RoPE。不 norm $v$。GQA 时
  $k$ 只有 $H_{\mathrm{kv}}$ 头，用自己的 `k_norm`。顺序反了会对不齐公开 checkpoint。
tags:
  - Coding
  - QK-Norm
  - RMSNorm
  - Qwen
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Qwen3 Technical Report
    url: https://arxiv.org/abs/2505.09388
    type: primary
  - title: Gemma 2 Technical Report
    url: https://arxiv.org/abs/2408.00118
    type: primary
  - title: Query-Key Normalization for Transformers
    url: https://arxiv.org/abs/2010.04245
    type: primary
---

## 题怎么来的

Henry et al. 把 QK 归一化当训练稳定手段；Gemma 2 / Qwen3 写进了公开架构。Qwen3 明确：**去掉 QKV bias，加上
QK-Norm**，并且 HuggingFace 实现是 RMSNorm 后再 RoPE。部分 Llama 变体（社区里常提到 Llama 4 一类）可能把
norm 放在 RoPE **之后**，和 Qwen 不是同一张计算图。Meta / 跨境 Qwen 岗白板要你写出顺序、轴、以及 $H_q\ne H_{\mathrm{kv}}$ 时有几份 $\gamma$。层输入那份 RMSNorm 仍在，见
`coding-rmsnorm`；本题是注意力内部多出来的两份。

## 沿 head dim 归一，再旋转

$Q$ 形状 `[B, H_q, T, D]`，$K$ 形状 `[B, H_kv, S, D]`。QK-Norm 的 reduction 是最后一维 $D$，每个 head 自己的 RMS，不在 head 之间混：

$$
\mathrm{RMS}(x)=\sqrt{\frac{1}{D}\sum_{i=1}^{D}x_i^2+\varepsilon},\qquad
\hat q=\gamma_q\odot\frac{q}{\mathrm{RMS}(q)},\quad
\hat k=\gamma_k\odot\frac{k}{\mathrm{RMS}(k)}.
$$

$\gamma_q\in\mathbb{R}^{D}$ 广播到所有 query head（有的实现做成 `[H_q, D]` per-head
参数，Qwen3 常用一份 $D$）。**没有** bias $\beta$。$V$ 不做。然后

$$
q',k'=\mathrm{RoPE}(\hat q,\hat k).
$$

先旋再 norm 会把已经编进角度的分量再拉回单位 RMS，位置几何变了。公开 Qwen3 权重按「norm → RoPE」存；对不齐就是 silent
错，和 RoPE 偶奇对 / half-rotate 搞混是同一类。Decode 时 $T=1$，RMS 仍沿 $D$，不沿 cache 长度。

```python
import torch

def rmsnorm_last(x, weight, eps=1e-6):
    # x: [B, H, T, D]
    z = x.float()
    inv = torch.rsqrt(z.pow(2).mean(dim=-1, keepdim=True) + eps)
    y = (z * inv).to(x.dtype)
    return y * weight if weight is not None else y


def apply_rope(x, cos, sin):
    xe, xo = x[..., 0::2], x[..., 1::2]
    c, s = cos[None, None, :, :], sin[None, None, :, :]
    ye = xe * c - xo * s
    yo = xe * s + xo * c
    return torch.stack((ye, yo), dim=-1).flatten(-2)


def qk_norm_then_rope(q, k, w_q, w_k, cos, sin):
    q = rmsnorm_last(q, w_q)
    k = rmsnorm_last(k, w_k)
    return apply_rope(q, cos, sin), apply_rope(k, cos, sin)
```

GQA：`k` 不要先 `repeat_kv` 再 norm，否则 $H_{\mathrm{kv}}$ 份参数被复制成 $H_q$ 份，和训练时的
`k_norm` 对不上。正确顺序是 norm $K$（$H_{\mathrm{kv}}$）→ RoPE → 需要时再 repeat，见
`coding-gqa-repeat`。Cache 里写 **已经 norm+RoPE** 的 $K$，decode 不要对历史 $K$ 再 norm
一遍。

## 为什么要它，和层 RMSNorm 别并成一个

QK 点积没有自己的归一化时，logit 尺度随 $\|W_Q\|,\|W_K\|$ 涨，softmax 变尖，训练容易炸。QK-Norm 把每个 head
的 $q,k$ 钉在相近 RMS 上，相当于给注意力温度加了锚。层上的 RMSNorm 管的是残差流 `[B, T,
D_{\mathrm{model}}]`，轴和对象都不同，不能删掉其中一个冒充另一个。

$\varepsilon$ 与层 norm 可以不同；实现里常 $10^{-6}$。统计在 fp32 做。Apple 端侧会问多两次 reduction
值不值：相对 GEMM 可忽略，换来的是能训更大 LR / 更深的注意力。MLA 一类不物化完整 $q,k$ 的结构不一定套得上，面试说到「这是
MHA/GQA 的补丁」即可。

## 追问

- **一定要在 RoPE 前吗？** Qwen3 / 常见 Gemma 路径是前。Llama 4 一类公开讨论是后。读权重前看 `q_norm` 插在哪，不要赌。
- **$V$ 要不要 norm？** 标准 QK-Norm 不要。$V$ 是被加权的内容，不是点积的两边。
- **和 QK 的 $1/\sqrt{D}$ 重复吗？** 不重复。Scale 是常数；RMSNorm 按样本、按 head 变。两者都留。
- **decode 历史 $K$ 还 norm 吗？** 写入时做过就不要再做。对 cache 再 norm 等于用「当前 $\gamma$」去改旧向量，逐步生成和满量 prefill 会对不齐。

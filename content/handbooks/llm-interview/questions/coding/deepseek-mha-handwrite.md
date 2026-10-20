---
id: deepseek-mha-handwrite
section: coding
order: 200
level: S
title: DeepSeek 向算法笔试/面试：手写完整 Multi-Head Attention（含形状与 Mask）
quick: >-
  讲清 $Q,K,V$ 投影、拆头、缩放点积、因果/ padding mask、softmax 数值稳定、拼头与输出投影。代码要写
  contiguous/view 边界，并说明 GQA 只是改变 K/V 头数组织。
tags:
  - DeepSeek
  - Attention
  - Coding
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek 大模型算法岗笔试面经分享（练习向整理）
    url: https://www.nowcoder.com/discuss/913482312753418240
    type: secondary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 题目说明

来源为公开练习向整理帖（非严格候选人逐字实录），按 DeepSeek 系算法岗高频手撕准备；`realInterview: false`。

常见误区是：公式能背、形状写错，或把 GQA/MLA 说成改了 softmax。数学骨架不变：缩放点积 + mask + 加权 $V$。MLA 是另一压缩轴，见 `arch-mla`；本题先把 MHA 写完。对照真题手撕见 `baichuan-mha-handwrite`、`pdd-attention-handwrite`。

## 公式与白板检查清单

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

检查：$d_{\mathrm{model}}$ 整除 $H$；$M$ 能 broadcast 到 $[B,H,T_q,T_k]$；因果是下三角可见，padding 的 bool 语义不要反；fp16 softmax 先 float；cross-attn 时 $T_q\neq T_k$。`view` 前 `contiguous`，避免错误处理 stride 导致输出不正确。

```python
import torch

def mha(x, wq, wk, wv, wo, n_heads, mask=None):
    b, t, c = x.shape
    dh = c // n_heads
    q = (x @ wq).view(b, t, n_heads, dh).transpose(1, 2)
    k = (x @ wk).view(b, t, n_heads, dh).transpose(1, 2)
    v = (x @ wv).view(b, t, n_heads, dh).transpose(1, 2)
    scores = (q @ k.transpose(-2, -1)) * dh**-0.5
    if mask is not None:
        scores = scores.masked_fill(mask, float("-inf"))
    attn = torch.softmax(scores.float(), dim=-1).type_as(v)
    out = (attn @ v).transpose(1, 2).contiguous().view(b, t, c)
    return out @ wo
```

形状口播：$x[B,T,C]$ → 投影仍 $[B,T,C]$ → `view` $[B,T,H,d_h]$ → `transpose` $[B,H,T,d_h]$ → scores $[B,H,T,T]$ → 加权 $V$ 后拼回 $[B,T,C]$。

## GQA / MLA：压缩轴不同，softmax 不变

GQA：$H_{\mathrm{kv}}\lt H$，K/V 少头，Q 做 `repeat_interleave`。KV cache 从 $O(H d_h)$ 降到 $O(H_{\mathrm{kv}} d_h)$。MLA：沿表示维压 latent，RoPE 拆开，推理吸收矩阵，见 `arch-mla`。面试一句话：二者都为 逐 token 生成（decode） 带宽，压缩轴不同。不要在 MHA 代码里假装写了 MLA。

数值：mask 后若一整行全 `-inf`，softmax 变 NaN，应对该行单独保护（padding 全 mask 的 query）。Dropout 若写，打在 attn 权重上且训练态才开。

## 追问

- **为何除 $\sqrt{d_h}$？** 点积方差 $\propto d_h$，不缩放则 softmax 饱和。
- **mask 加在 softmax 前还是后？** 前。后加无法改变 softmax 已经分配的注意力权重。
- **GQA 要改 $d_h$ 吗？** 不要。头维仍是 $d_{\mathrm{model}}/H_{\mathrm{q}}$，只是 K/V 头更少。
- **`reshape` 代替 `transpose`？** 不能。`view` 不交换 $H$ 与 $T$ 的内存含义，必须 transpose 再 contiguous。
- **和 FlashAttention？** 同一数学，分块在线 softmax。白板仍写显式 scores，并声明生产用融合核。

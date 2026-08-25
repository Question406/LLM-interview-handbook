---
id: coding-fused-ce
section: coding
order: 29
level: S
title: 白板：融合 linear 和 cross entropy，不要物化 `[B, T, V]` logits
quick: >-
  $\ell=-h^\top w_y+\mathrm{logsumexp}(hW^\top)$。沿词表分块做 GEMM，维护 running $(m,\ell)$，目标 logit
  用 $w_y$ 点积取出。峰值显存跟 $V$ 的 chunk 走，不跟整表走。先 `linear` 再 `softmax` 再 `log` 会炸显存和数值。
tags:
  - Coding
  - Cross Entropy
  - Fused Kernel
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: The Liger Kernel — Efficient Triton Kernels for LLM Training
    url: https://arxiv.org/abs/2410.10989
    type: primary
  - title: torch.nn.functional.cross_entropy
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: Online normalizer calculation for softmax
    url: https://arxiv.org/abs/1805.02867
    type: primary
---

## 题怎么来的

词表 $V$ 到十万量级时，logits `[B, T, V]` 往往比隐状态还大。NVIDIA 训练 kernel 和 OpenAI debug
都会问：CE 真的需要这张表吗？不需要。损失只依赖目标列和整行 logsumexp。Liger / Apex / Megatron 的 fused
linear-cross-entropy 沿 $V$ 分块做 $hW^\top$，用 online 归约攒分母，反向再扫一遍块，不把 `[N, V]` 留在
HBM。公式底盘见 `coding-cross-entropy`、`coding-logsumexp`。

## 只留 $z_y$ 和 $(m,\ell)$

把 `[B, T, D]` 收成 $h\in\mathbb{R}^{N\times D}$，$W\in\mathbb{R}^{V\times D}$（`nn.Linear` 的 weight）。目标 $y\in\{0,\ldots,V-1\}^N$。

$$
z=hW^\top,\qquad
\ell=-z_y+\mathrm{logsumexp}(z).
$$

$z_y=h^\top W_{y}$，一次 gather 行就能算，复杂度 $O(ND)$。$\mathrm{logsumexp}$ 沿 $V$ 切成宽
$C$ 的块：第 $c$ 块 $z^{(c)}=h W^{(c)\top}$ 形状 `[N, C]`，用和 FlashAttention 相同的
running max / sumexp 更新全局 $(m,\ell)$，块用完即丢。最终

$$
\mathrm{logsumexp}(z)=m+\log\ell,\qquad
\ell_{\mathrm{CE}}=-z_y+m+\log\ell.
$$

Pad / ignore 下标不进均值，分母是有效 token 数，和 `coding-cross-entropy` 同一契约。Shift 仍是 `h[:,
:-1]` 对 `labels[:, 1:]`，在 flatten 之前做。

```python
import torch

def fused_linear_ce(h, weight, target, ignore_index=-100, chunk=4096):
    # h: [N, D]; weight: [V, D]；不分配 [N, V]
    n, v = h.size(0), weight.size(0)
    h32, w32 = h.float(), weight.float()
    m = h32.new_full((n,), float("-inf"))
    ell = h32.new_zeros(n)
    for v0 in range(0, v, chunk):
        z = h32 @ w32[v0 : v0 + chunk].T
        m2 = torch.maximum(m, z.amax(dim=-1))
        ell = ell * torch.exp(m - m2) + torch.exp(z - m2[:, None]).sum(-1)
        m = m2
    safe = target.clamp(min=0)
    z_y = (h32 * w32[safe]).sum(-1)
    nll = -z_y + m + ell.clamp_min(1e-20).log()
    keep = target != ignore_index
    if keep.any():
        return nll[keep].mean()
    return h.new_zeros(())
```

单测：小 $V$ 对上 `F.cross_entropy(h @ W.T, y)`。对不上就是 ignore 进了分母，或 $z_y$ 取错行。第一块时
$m=-\infty$，$\exp(m-m_2)=0$，和 `coding-online-softmax` 的空起点一样。

## 显存、反向、绑权重

峰值激活大约 $O(NC)$ 而不是 $O(NV)$。$V=128256$，$N=B\cdot T=8192$，$C=4096$ 时，一块 bf16
logits 大约 $64\,\mathrm{MiB}$，整表则是 $2\,\mathrm{GiB}$ 量级。反向需要 $\partial L/\partial z=p-e_y$，可以再扫 $V$ 块重算 $p$，不存整表；这就是 fused kernel 换计算换显存。评委若只让写前向，先把「不物化」说清楚。

Weight tying 时 $W$ 就是 embedding 矩阵，见 `coding-weight-tying`。Fused
路径仍用同一份存储，不要为了 chunk 再 clone 一份 $W$。z-loss 要的 $\mathrm{logsumexp}$ 正是这里的
$m+\log\ell$，可以同一趟加 $10^{-4}(m+\log\ell)^2$，见 `coding-z-loss`。Tensor parallel
沿 $V$ 切开时，每卡先做局部 logsumexp，再跨卡 all-reduce max 和 rescale 后的 $\ell$，和 split-K
注意力同一类归约，见 `coding-flash-decode`。

Shift 在 flatten 之前做：`h[:, :-1]` 对 `labels[:, 1:]`。不要对整段 $T$ 算完再靠 ignore 把最后一位丢掉却仍除以 $T$。

## 追问

- **为什么禁止先 softmax 再 log？** 和未融合 CE 相同：下溢成 $0$。融合不改变这条数值契约。
- **chunk 是不是越小越好？** 太小 GEMM 变瘦、占用率差。选能塞进 SRAM / L2 的 $C$，不是 $C=1$。
- **label smoothing？** 目标不再是单列，$z_y$ 一条不够，要对整表做 $-q\log\pi$。还能分块，但每块都要累加 $q_c\log\pi_c$，实现明显更胖。
- **fp16 的 $(m,\ell)$？** 升 fp32。词表 CE 的 sumexp 和注意力一样怕溢出。

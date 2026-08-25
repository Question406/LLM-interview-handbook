---
id: coding-z-loss
section: coding
order: 23
level: A
title: 白板：PaLM z-loss，为什么往 logits 上加这一项
quick: >-
  $z=\mathrm{logsumexp}(\mathrm{logits})$，辅损 $10^{-4} z^2$。softmax / CE 对 logits 加常数不变，$z$
  却跟着漂；绝对值大会在 bf16 里打满、训练不稳。z-loss 把 partition 钉在 $0$ 附近，不改分类决策。
tags:
  - Coding
  - Z-loss
  - PaLM
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
---

## 题怎么来的

PaLM 540B 的训练报告写了这条辅损，系数 $10^{-4}$。Google 研究岗 / 大模型训练白板会问「CE 已经平移不变了，为什么还要管 logits 的绝对大小」。Pathways 规模背景见 `google-palm-pathways`。公式上它就是钉住 `coding-logsumexp` 的输出。OpenAI debug 不一定点名 z-loss，但 bf16 下一会儿 NaN 时，logits 漂移是同一类故事。

## 钉住 partition，不改 softmax

对每个 token 的 logits $x\in\mathbb{R}^{V}$：

$$
z=\mathrm{logsumexp}(x)=\log\sum_i e^{x_i},\qquad
\mathcal{L}_z=\lambda z^2,\quad \lambda=10^{-4}.
$$

PaLM 把 $\mathcal{L}_z$ 加到 token CE 上。softmax$(x)=$softmax$(x+c)$，CE 也不变，因为 $x_y$ 和 $z$ 一起加 $c$。所以优化 CE 时 $x\leftarrow x+c$ 是零空间，$z$ 可以涨到几百。bf16 的有效精度在大绝对值上变粗，`exp` 和 GEMM 都更容易 inf / 变成同一个数。$z^2$ 的梯度把 $z$ 往 $0$ 推：等价于希望 $\sum e^{x_i}\approx 1$，logits 落在不太离谱的范围。分类 argmax 仍然由相对差决定。

不要把 z-loss 写成 $\lambda\|x\|_2^2$。那会压相对差、伤 CE。正则的是 **标量 $z$**，不是整行 logits。

```python
import torch
import torch.nn.functional as F

Z_COEF = 1e-4

def ce_with_z_loss(logits, target, ignore_index=-100, z_coef=Z_COEF):
    # logits: [B, T, V], target: [B, T]
    x = logits.float()
    z = torch.logsumexp(x, dim=-1)  # [B, T]
    logp = x - z.unsqueeze(-1)
    safe = target.clamp(min=0)
    nll = -logp.gather(-1, safe.unsqueeze(-1)).squeeze(-1)
    mask = target != ignore_index
    denom = mask.sum().clamp_min(1)
    ce = nll[mask].sum() / denom
    z_loss = (z.square() * mask).sum() / denom
    return ce + z_coef * z_loss, ce, z_loss


def shift_invariance_demo(logits, y):
    ce0 = F.cross_entropy(logits, y)
    ce1 = F.cross_entropy(logits + 50.0, y)
    z0 = torch.logsumexp(logits, dim=-1).mean()
    z1 = torch.logsumexp(logits + 50.0, dim=-1).mean()
    return ce0, ce1, z0, z1  # ce 接近，z1 ≈ z0+50
```

pad 必须和 CE 共用 mask：对 ignore 位置加 $z^2$ 会让 padding 多的 batch 辅损变大。分母是有效 token，不是 $B\cdot T$。

## 系数和什么时候需要

$\lambda=10^{-4}$ 是 PaLM 公开值。太大则强迫 $z\approx 0$ 过猛，和 CE 抢；太小钉不住漂移。小模型、fp32 往往感觉不到；词表大、$V$ 到 $10^5$、bf16 / fp8 时这条开始值钱。它 **不是** label smoothing，也不是 entropy bonus：不鼓励均匀分布，只鼓励 log-partition 别爆。和 MoE 的 load-balancing aux 也不是一类，别往路由损失上套。

## 追问

- **为什么不直接 clip logits？** clip 不可微边界、伤相对差。$z^2$ 平滑，且只约束平移自由度。
- **$z$ 用 `log(sum(exp))` 行吗？** 不行。大 $x$ 时 inf，辅损本身 NaN。必须 log-sum-exp trick，见 `coding-logsumexp`。
- **推理还加吗？** 不加。它只在训练图里。推理的 softmax 不需要 $z\approx 0$。
- **和 weight decay？** WD 管参数范数。z-loss 管激活 / logits 的绝对标尺。两件套可以同时在。

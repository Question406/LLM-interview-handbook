---
id: coding-logsumexp
section: coding
order: 20
level: S
title: 白板：log-sum-exp trick，和 cross entropy 的关系
quick: >-
  $\mathrm{logsumexp}(z)=m+\log\sum e^{z-m}$，$m=\max z$。它是 softmax 分母的对数。CE 是
  $-z_y+\mathrm{logsumexp}(z)$，log-softmax 是 $z-\mathrm{logsumexp}(z)$。不要先
  $\exp$ 再 $\log\sum$，大 logit 会 inf。
tags:
  - Coding
  - LogSumExp
  - Cross Entropy
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
  - title: torch.nn.functional.cross_entropy
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: torch.nn.functional.log_softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html
    type: primary
---

## 题怎么来的

OpenAI 数值题和 CE 白板是同一块肌肉。评委让你写 `logsumexp`，再问「交叉熵还要不要过 softmax」。答案是不要：CE 就是在 log 域用这条归约。稳定 softmax 见 `coding-softmax-stable`，完整 CE 见 `coding-cross-entropy`。PaLM 的 z-loss 直接正则这条 $z=\mathrm{logsumexp}$，见 `coding-z-loss`。

## Trick：先减 max

对向量 $z$（分类时最后一维 $V$）：

$$
\mathrm{logsumexp}(z)=\log\sum_j e^{z_j}=m+\log\sum_j e^{z_j-m},\quad m=\max_j z_j.
$$

$e^{z-m}\in(0,1]$，求和在 $(0,V]$。不减 $m$ 时 $z_j=80$ 在 fp32 里 `exp` 已经 inf，`log(inf)` 把整行毒掉。减 $m$ 不改变函数值：$\log(e^{m} \sum e^{z-m})=m+\log\sum e^{z-m}$。轴必须和 softmax 一致，`keepdim` 要能广播回 `[B, T, V]`。

和 softmax 的关系：

$$
\log\mathrm{softmax}(z)_i=z_i-\mathrm{logsumexp}(z),\qquad
\mathrm{softmax}(z)_i=\exp(\log\mathrm{softmax}(z)_i).
$$

交叉熵（one-hot $y$）直接是

$$
\ell=-z_y+\mathrm{logsumexp}(z)=-\log\mathrm{softmax}(z)_y.
$$

从不需要物化 $p$。先 softmax 再 `log(p[y])`：$p_y$ 下溢成 $0$ 就得到 $-\infty$。熵 $H(\pi)=-\sum\pi\log\pi$ 也可以全程用 log-softmax，见 `openai-entropy-l1`。

```python
import torch

def logsumexp(z, dim=-1, keepdim=False):
    z = z.float()
    m = z.amax(dim=dim, keepdim=True)
    out = m + (z - m).exp().sum(dim=dim, keepdim=True).log()
    return out if keepdim else out.squeeze(dim)


def log_softmax(z, dim=-1):
    return z.float() - logsumexp(z, dim=dim, keepdim=True)


def nll_from_logits(logits, target):
    # logits: [N, V], target: [N]
    logp = log_softmax(logits, dim=-1)
    return -logp.gather(1, target.unsqueeze(1)).squeeze(1)


def check():
    z = torch.tensor([[1.0, 2.0, 3.0], [1000.0, 1000.0, 1001.0]])
    lse = logsumexp(z, dim=-1)
    assert torch.allclose(lse, torch.logsumexp(z, dim=-1))
    assert torch.isfinite(lse).all()
    p = log_softmax(z).exp().sum(dim=-1)
    assert torch.allclose(p, torch.ones(2))
```

`torch.logsumexp` 就是这个。自己写漏 `keepdim` 时 `[B, T]` 减不成 `[B, T, V]`。

## 平移不变和 z-loss

softmax 对 $z\leftarrow z+c$ 不变，但 $\mathrm{logsumexp}(z+c)=\mathrm{logsumexp}(z)+c$。CE 也不变（$z_y$ 和 logsumexp 一起加 $c$）。所以 logits 可以整体漂，bf16 上绝对值大会丢精度。z-loss 把 $\mathrm{logsumexp}^2$ 拉回零附近，正是钉住这个自由度。FlashAttention 的 online 归约维护的 $(m,\ell)$ 满足 $\mathrm{logsumexp}=m+\log\ell$，见 `coding-online-softmax`。

## 追问

- **`log(sum(exp(z)))` 什么时候看起来还行？** 小 logits、fp64。词表 CE 和注意力 scores 不要赌。
- **和 `log_softmax` 谁先谁后？** 先 logsumexp（或 fused log-softmax），CE gather 一列。不要 softmax → log。
- **全 $-\infty$ 的一行？** max 是 $-\infty$，$\exp$ 和 $\log$ 都是 NaN。mask 必须保证至少有一个有限值，或跳过该行。
- **温度 $T$？** $\mathrm{logsumexp}(z/T)$。除 $T$ 在 trick 之前，顺序和 `coding-topk-nucleus` 一样。

---
id: coding-dpo-weighted
section: coding
order: 43
level: A
title: 白板：DPO 的梯度写成加权 logprob，权重是什么，什么时候大
quick: >-
  $z=\beta(\Delta_w-\Delta_l)$，$\Delta=\log\pi_\theta(y\mid x)-\log\pi_{\mathrm{ref}}(y\mid x)$，序列 logprob 是 token 求和。
  $\nabla\mathcal{L}=-\beta\sigma(-z)(\nabla\log\pi_w-\nabla\log\pi_l)$，等价 loss 是 $-\mathrm{sg}(\beta\sigma(-z))(\log\pi_w-\log\pi_l)$。
  模型排反了（$z<0$）权重大，排对了权重趋于 0。
tags:
  - Coding
  - DPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

## 题怎么来的

`fireworks-grpo-sft-loss` 把 GRPO 写成了加权 logprob。同样的问题换成 DPO：训练端只支持「带权重的 logprob 之和」时，DPO 能不能跑，权重是什么。DPO loss 本身怎么推见 `openai-dpo-loss`。

给你的代码：

```python
def dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    # pol_* / ref_*: [B, T] token logprob；mask_*: [B, T] response mask
    lw = (pol_w * mask_w).sum(-1) / mask_w.sum(-1)
    ll = (pol_l * mask_l).sum(-1) / mask_l.sum(-1)
    rw = (ref_w * mask_w).sum(-1) / mask_w.sum(-1)
    rl = (ref_l * mask_l).sum(-1) / mask_l.sum(-1)
    z = beta * ((lw - rw) - (ll - rl))
    return -torch.log(torch.sigmoid(z)).mean()
```

## 错在哪

**序列 logprob 被除以了长度。** DPO 里的 $\log\pi(y\mid x)$ 是 token logprob 之和。按长度平均得到的是另一个目标，接近 SimPO 的长度归一化，$\beta$ 的尺度也不同。要这么做可以，但要说清楚这已经不是 DPO。

**`log(sigmoid(z))` 数值不稳。** $z$ 很负时 `sigmoid` 下溢到 0，`log` 得到 `-inf`。用 `F.logsigmoid(z)`。

参考模型的 logprob 要在 `no_grad` 下算，这段代码看不出来，面试时要问一句。

```python
import torch.nn.functional as F

def seq_logprob(tok_logp, mask):
    return (tok_logp * mask).sum(-1)

def dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    z = beta * ((seq_logprob(pol_w, mask_w) - seq_logprob(ref_w, mask_w))
                - (seq_logprob(pol_l, mask_l) - seq_logprob(ref_l, mask_l)))
    return -F.logsigmoid(z).mean()
```

## 梯度

$\frac{d}{dz}\big(-\log\sigma(z)\big) = -\sigma(-z)$，$z$ 对 $\theta$ 的梯度是 $\beta(\nabla\log\pi_w - \nabla\log\pi_l)$，参考模型不贡献梯度：

$$
\nabla_\theta\mathcal{L} = -\beta\,\sigma(-z)\,\big(\nabla_\theta\log\pi_\theta(y_w\mid x) - \nabla_\theta\log\pi_\theta(y_l\mid x)\big)
$$

所以等价的加权 logprob loss 是：chosen 的每个 token 权重 $+c$，rejected 的每个 token 权重 $-c$，$c = \mathrm{sg}(\beta\sigma(-z))$。

```python
def dpo_loss_weighted(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    with torch.no_grad():
        z = beta * ((seq_logprob(pol_w, mask_w) - seq_logprob(ref_w, mask_w))
                    - (seq_logprob(pol_l, mask_l) - seq_logprob(ref_l, mask_l)))
        c = beta * torch.sigmoid(-z)                       # [B]
    B = pol_w.shape[0]
    return -(c * (seq_logprob(pol_w, mask_w) - seq_logprob(pol_l, mask_l))).sum() / B
```

```python
B, T = 4, 6
pol_w = torch.randn(B, T, requires_grad=True)
pol_l = torch.randn(B, T, requires_grad=True)
ref_w, ref_l = torch.randn(B, T), torch.randn(B, T)
mask_w = (torch.rand(B, T) > 0.3).float()
mask_l = (torch.rand(B, T) > 0.3).float()
args = (pol_w, pol_l, ref_w, ref_l, mask_w, mask_l)
g1 = torch.autograd.grad(dpo_loss(*args), (pol_w, pol_l))
g2 = torch.autograd.grad(dpo_loss_weighted(*args), (pol_w, pol_l))
assert all(torch.allclose(a, b, atol=1e-6) for a, b in zip(g1, g2))
```

## 权重怎么读

$\sigma(-z)$ 是模型当前「把这对排反了」的概率。$z \ll 0$，模型更偏 rejected，权重接近 $\beta$；$z \gg 0$，已经排对了，权重趋于 0。DPO 自带难例挖掘，不需要另外按 loss 采样。

和 GRPO 对比：GRPO 的权重来自奖励（advantage），在一步内固定；DPO 的权重来自模型自己当前的隐式奖励差，训练过程中一直在变。

## 追问

**chosen 的 logprob 为什么也会下降？** 梯度只约束 $\log\pi_w - \log\pi_l$ 这个差，没有约束 $\log\pi_w$ 本身。两者一起降、rejected 降得更快，loss 照样下降。常见的补救是加一项 chosen 上的 SFT loss，在这个形式里就是给 chosen 的 token 权重再加一个正常数。

**$\beta$ 大小的影响？** $\beta$ 同时出现在 $z$ 里和权重前面。$\beta$ 大，$z$ 很快饱和，权重很快掉到 0，模型离参考模型不远就停了；$\beta$ 小，要走很远才饱和。

**IPO 呢？** 记 $h = \Delta_w - \Delta_l$，IPO 的 loss 是 $\big(h - \frac{1}{2\tau}\big)^2$。梯度系数是 $-2\big(h - \frac{1}{2\tau}\big)$，对 $h$ 是线性的：间隔不够时为正，把 chosen 往上推；间隔超过 $\frac{1}{2\tau}$ 时变成负的，往回拉。DPO 的系数永远为正，只是趋于 0。见 `align-ipo`。

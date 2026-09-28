---
id: sys-kl-place
section: systems
order: 60
level: A
title: 系统：KL 写进奖励，还是写进 loss？
quick: >-
  写进奖励时，KL 先算完并 detach，再减出优势，梯度不穿过 KL 那一项。写进 loss 时，KL 对当前策略可导。
  GRPO 常用后者。两种不要叠在同一条更新里。
tags:
  - Post-train
  - KL
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl GRPO，KL 在 loss 里就不进奖励
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
  - title: Schulman, Approximating KL Divergence
    url: http://joschu.net/blog/kl-approx.html
    type: primary
---

## 题怎么来的

verl 的 GRPO 说明写了：`use_kl_loss` 为真时，不再把 KL 放进奖励。Hugging Face 的后训练笔记把两件事分开：奖励里的 KL 要停梯度，loss 里的 KL 会进反向。这道按这个开关拟的。参考模型占多少显存见 `sys-ref-model`。

## 两种接法

PPO 常见的是每个 token 的奖励先减去 $\beta$ 乘以对参考模型的 KL，标量的任务奖励加在最后一个有效 token 上，再算优势。这里的 KL 是已经算完的数。它改变优势的大小，不直接对 $\log\pi_{\mathrm{ref}}$ 反传。

GRPO 常见的是优势只用任务奖励在组内标准化，KL 作为 loss 里的另一项加进去。该项对当前策略可导，把概率往参考模型拉。verl 默认这条，并提供 $k_1$、$k_2$、$k_3$ 几种估计。$k_3$ 的值非负，但它对策略的梯度并不自动等于反向 KL 的梯度，估计式和反传式要一起说。

两套同时开：优势里已经罚过一次，loss 里再罚一次，$\beta$ 的含义变了，调参对不上论文。

## 代码

```python
import torch

def kl_in_reward(task_reward, policy_logp, ref_logp, beta):
    kl = (policy_logp - ref_logp).detach()
    return task_reward - beta * kl.sum(-1)

def kl_in_loss(pg_loss, policy_logp, ref_logp, beta, mask):
    delta = ref_logp.detach() - policy_logp
    k3 = torch.exp(delta) - delta - 1
    return pg_loss + beta * (k3 * mask).sum() / mask.sum().clamp(min=1)
```

## 追问

**优势已经含 KL 时，还要不要 clip？** 要。clip 限制的是相对采样策略的步长。KL 限制的是相对参考模型的漂移。不是同一个锚。

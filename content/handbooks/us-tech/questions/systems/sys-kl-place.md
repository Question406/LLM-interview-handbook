---
id: sys-kl-place
section: systems
order: 60
level: A
title: 系统：KL 写进奖励，还是写进 loss？
quick: "KL 写进奖励时，先算好并 detach，再用它调整奖励和优势；写进 loss 时，它作为对当前策略可导的正则项。GRPO 常用后者，优势只按任务奖励在组内算。两种路径要明确选择，同时打开会重复惩罚，改变 beta 的含义。"
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

KL 可以先进入奖励、影响优势，也可以直接作为 loss 的可导正则项；两种接法的梯度路径不同。比如 verl 打开 `use_kl_loss` 后，就不再往奖励里加 KL，避免同一次更新罚两次。Hugging Face 的后训练笔记也区分了奖励中停梯度和 loss 中 backpropagation 这两条路径，reference model 显存见 `sys-ref-model`。

PPO 常见的是每个 token 的奖励先减去 $\beta$ 乘以对 reference model 的 KL，标量的任务奖励加在最后一个有效 token 上，再算优势。这里的 KL 是已经算完的数。它改变优势的大小，不直接对 $\log\pi_{\mathrm{ref}}$ backpropagation。

GRPO 常见的是优势只用任务奖励在组内 standardization，KL 作为 loss 里的另一项加进去。该项对当前策略可导，把概率往 reference model 拉。verl 默认这条，并提供 $k_1$、$k_2$、$k_3$ 几种估计。$k_3$ 的值非负，但它对策略的梯度并不自动等于 reverse KL 的梯度，估计式和 backpropagation 式要一起说。

如果两套同时开，优势里已经罚过一次，loss 里再罚一次，$\beta$ 的含义变了，调参对不上论文。

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

**优势已经含 KL 时，还要不要 clip？**
要。clip 限制的是相对 sampling 策略的步长。KL 限制的是相对 reference model 的漂移。不是同一个锚。

## 相关题

- [[align-grpo]]：口述 GRPO 时要讲清 KL 护栏还在，这张回答它具体接在哪。
- [[openai-ppo-clip]]：从 clip 这一侧讲「两个锚」，clip 管 $\pi_{\mathrm{old}}$，KL 管 $\pi_{\mathrm{ref}}$。
- [[coding-rloo-advantage]]：RLOO 论文把 KL 并进序列奖励再做 leave-one-out，是「写进奖励」的具体例子。
- [[fireworks-grpo-sft-loss]]：把 GRPO 写成加权 logprob 时，KL 要么折进权重、要么单独一项 loss，对应这里的两种接法。
- [[p3a-anthropic-rl-fundamentals-grpo-debug]]：调试题的追问会问 ref KL 和 old ratio 为什么不能合成一项。

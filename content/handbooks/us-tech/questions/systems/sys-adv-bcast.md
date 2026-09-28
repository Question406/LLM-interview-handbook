---
id: sys-adv-bcast
section: systems
order: 57
level: A
title: 系统：序列级优势怎么铺到 token 上，哪些位置必须是 0？
quick: >-
  GRPO 的优势是一整条回答一个数。乘到每个 response token 上，prompt、pad、工具返回的原文不乘。
  优势要 detach。把 prompt 也算进 loss，模型会去改写题目。
tags:
  - Post-train
  - GRPO
  - Mask
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

这是后训练 loss 里最基础的形状题，按 GRPO 的序列级奖励拟的。组内标准化见现有的 GRPO 卡。logprob 对不上见 `sys-rollout-logprob`。

## 形状

奖励是 `[B]`，回答长度不同。优势先在同一条 prompt 的 $G$ 条上算完，得到 `[B]`，再变成 `[B, 1]`，和 token logprob `[B, T]` 相乘。mask 在 prompt 和 pad 上是 0，在模型生成的 token 上是 1。

工具调用若把环境返回的文本拼回序列，那段不是策略采样的，mask 也是 0。只对模型写出的工具名和参数做损失。环境文字进了 loss，梯度会去拟合一个模型控制不了的字符串。

求和时除以 mask 的总和，不要除以填充后的 $T$。否则短回答的每个 token 权重被 pad 稀释，长回答占便宜。

## detach

优势来自这批样本的奖励，不是 $\pi_\theta$ 的函数。放进图里，会多一条没有推导的梯度，奖励模型或测试分数的数值噪声也会流进参数。

## 代码

```python
import torch

def token_loss(new_logp, old_logp, adv, response_mask, eps=0.2):
    adv = adv.detach()[:, None]
    rho = torch.exp(new_logp - old_logp.detach())
    unclipped = rho * adv
    clipped = torch.clamp(rho, 1.0 - eps, 1.0 + eps) * adv
    per_tok = -torch.minimum(unclipped, clipped)
    return (per_tok * response_mask).sum() / response_mask.sum().clamp(min=1)
```

## 追问

**过程奖励每个 token 一个分呢？** 那就不要再广播成一个标量。每个位置用自己的优势，mask 仍然去掉 prompt 和垫片。序列级和 token 级混加之前，先把尺度对齐。

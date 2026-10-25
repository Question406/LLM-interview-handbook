---
id: sys-adv-bcast
section: systems
order: 57
level: A
title: 系统：序列级优势怎么铺到 token 上，哪些位置必须是 0？
quick: "GRPO 每条回答先得到一个优势标量，detach 后广播到模型生成的 token。Prompt、pad 和工具返回原文的 mask 为 0，聚合损失时除以有效 token 数，避免 padding 改变权重。"
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

序列级 GRPO 的优势是一条回答一个数，先 detach，再广播到这条回答里由模型生成的 token。Prompt、pad 和环境返回原文都不参与这部分损失，否则梯度会去拟合模型没有控制的内容。

这题按 GRPO 的序列级奖励整理，组内标准化先算每条回答的标量优势，再处理 token 维度。Logprob 对齐见 `sys-rollout-logprob`。

奖励形状是 `[B]`，同一 prompt 的 $G$ 条回答先完成组内优势计算，结果仍为 `[B]`。再扩成 `[B, 1]`，与 `[B, T]` 的 token logprob 相乘。Prompt 和 pad 的 mask 是 0，模型生成位置是 1，长度不同也能用同一套计算。

工具调用若把环境返回的文本拼回序列，那段不是策略采样的，mask 也是 0。只对模型写出的工具名和参数做损失。环境文字进了 loss，梯度会去拟合一个模型控制不了的字符串。

求和时除以 mask 的总和，不要除以填充后的 $T$。否则短回答的每个 token 权重被 pad 稀释，长回答占便宜。

这批样本的优势在策略更新里应当视为固定目标，不对 $\pi_\theta$ 求导。若把优势计算也接入图，会额外引入推导之外的梯度，让奖励模型或测试分数的数值噪声流入参数。

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

**过程奖励每个 token 一个分呢？**
每个位置直接使用自己的优势，无需再广播成同一个标量。每个位置用自己的优势，mask 仍然去掉 prompt 和 padding。序列级和 token 级混加之前，先把尺度对齐。

## 相关题

- [[sys-eos-mask]]：同一条 mask 的另一端，专问 EOS 本身和 EOS 之后的 token 进不进 loss。
- [[coding-rloo-advantage]]：本题广播之前那一步，按 leave-one-out 算出每条回答的标量优势，并和 GRPO 的组内标准化对比。
- [[p3a-openai-masked-cross-entropy-loss]]：SFT 版的 masked loss，同样要除以有效 token 数而不是填充后的长度。
- [[align-grpo]]：口述 GRPO 的组内 baseline 为什么不要 critic，这张是它的优势落到 token 上的那一步。
- [[p3a-anthropic-rl-fundamentals-grpo-debug]]：Anthropic 调试题里 response mask 也是一个检查点，那里还要找采样和零方差组的 bug。
- [[coding-grpo-loss-agg]]：优势乘到 token 之后，token loss 怎么聚合成一个数，三种写法的长度偏置。

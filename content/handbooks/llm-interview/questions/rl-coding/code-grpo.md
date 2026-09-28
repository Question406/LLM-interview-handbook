---
id: code-grpo
section: rl-coding
order: 6
level: S
title: 手写 GRPO group advantage：$\mathrm{std}\approx 0$ 怎么处理？
quick: >-
  Reward 按 prompt 分组，在 group 维求 mean/std；$A=(r-\mathrm{mean})/(\mathrm{std}+\mathrm{eps})$。$\mathrm{std}\approx 0$
  表示一组没有 relative signal，应记录/过滤或改 sampling；`eps` 只防除零，不制造学习信号。
tags:
  - GRPO
  - PyTorch
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

错法：只在分母加 `eps` 假装有信号。$\mathrm{std}\approx 0$ 表示整组没有相对差别（全对或全错），优势应为 0，这步更新无效。`eps` 只防 NaN，不能制造学习信号。组大小 $n\gt 1$ 的定义见 `sys-rl-group-n`；手撕完整 surrogate 见 `stepfun-grpo-loss-handwrite`。PPO / GRPO / GSPO 放在同一次更新里、并对照 TRL 与 verl 的开关，见 `code-ppo-grpo-gspo`。
## 组内标准化：维要对，unbiased 要和论文一致

同一 prompt 采 $G$ 条，奖励 $r\in\mathbb{R}^{N\times G}$：

$$
A_{i}=\frac{r_{i}-\mathrm{mean}_{G}(r)}{\mathrm{std}_{G}(r)+\varepsilon}.
$$

必须在 group 维上求 mean/std，不能把不同题混在一个 batch 里减全局均值（题难度会泄漏进优势）。

```python
import torch

def group_advantage(rewards, eps=1e-6):
    # rewards: [N_prompts, G]
    mean = rewards.mean(dim=1, keepdim=True)
    std = rewards.std(dim=1, keepdim=True, unbiased=False)
    adv = (rewards - mean) / (std + eps)
    informative = std.squeeze(1) > eps
    return adv, informative
```

`torch.std` 默认 `unbiased=True`（除 $G-1$）。小 $G$ 时样本标准差与总体标准差数值不同；$G=1$ 时 unbiased std 不可定义。实现必须和 DeepSeekMath / 框架约定一致，通常 population std（`unbiased=False`）。$G=1$ 根本不是 GRPO，见 `pt-grpo`。

## $\mathrm{std}\approx 0$：过滤或改采样，不要靠 eps 救命

binary reward 下全 0 或全 1，中心化后全 0，`std=0`。加上 `eps` 后 $A$ 仍约 0（分子也是 0），看起来「能跑」，但 informative 标志必须记下来：零方差组占用了 rollout 预算。工程上监控 zero-variance group rate；DAPO Dynamic Sampling 就是少让这些组进训练 batch，见 `slime-dynamic-partial`、`byte-grpo-all-same-zero-adv`。

Dr.GRPO 类 objective 可能去掉 std 除法，只减均值，见 `pt-drgrpo`。多路奖励（正确性 + 格式 + 长度）要先决定：先合成标量再 group-norm，还是每条 component 单独 norm 再加权。两种不可混着调系数。token 级往往广播同一 $A_i$；不要对每个 token 再减一次均值。
## 追问

- **`unbiased=True` 有什么影响？** 小 $G$ 时数值偏大；$G=1$ 直接 NaN。必须和论文/veRL 定义对齐。
- **eps 能不能改成 $10^{-2}$ 制造信号？** 不能。分子已是 0，放大分母只是更接近 0。要换题或加温度把组采散。
- **先组合 reward 还是先分别 norm？** 尺度不同的分量先分别 norm 更稳；先加权再 norm 会让大尺度分量主导组内排序。
- **和 PPO critic？** GRPO 不训 $V(s)$，baseline 就是组均值。PPO 可以 $n=1$，见 `code-ppo-clip`。
- **全对是不是已经学会了？** 对这题是零信息。降温难度或动态重采，不要加学习率。

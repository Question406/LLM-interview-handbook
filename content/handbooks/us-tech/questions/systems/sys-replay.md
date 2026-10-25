---
id: sys-replay
section: systems
order: 70
level: B
title: 系统：旧的 rollout 能不能留到下一步再训？
quick: "旧 rollout 可以继续训练，但必须保留采样时的 token logprob、权重版本和 mask，用它们计算重要性采样比。策略偏离太远、clip 比例过高就丢弃；GRPO 要整组保留或丢弃，不能用新权重补算旧 logprob。"
tags:
  - Post-train
  - Replay
  - Off-policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl issue 1524
    url: https://github.com/verl-project/verl/issues/1524
    type: primary
---

旧 rollout 可以留到下一步训练，前提是采样时就存好 token logprob 和权重版本，再用重要性采样比修正策略变化。生成很贵，复用能省开销；代价是数据会越来越偏离当前策略。verl issue 1524 讨论的多次更新就是这个问题，异步落后几步的情况见 `sys-async-stale`。

一次采样完成时，文本、奖励、采样 logprob、权重版本和 mask 都固定下来。下一步用新策略算新的 logprob，旧值作为 $\pi_{\mathrm{old}}$。如果当时没存，现在拿更新后的模型重跑，算出来的是 $\pi_{\theta}$，重要性采样比会被伪装成 1，而优势仍来自旧轨迹，更新方向就可能出错。

我会按版本差和比值方差决定何时丢弃。版本差超过预算，或 clip 比例接近 1，很多 token 已经没有有效梯度，继续训练价值很小。旧样本奖励高也不能无限保留，那可能是旧策略才会走出的路径。GRPO 必须整组保留或整组丢弃，只留高奖励样本会改变原来的组均值。

下面强制检查旧 logprob 是否存在：

```python
import torch

def replay_ratio(new_logp, sample):
    if sample.old_logp is None:
        raise RuntimeError("cannot recompute old logprob with the new weights")
    return torch.exp(new_logp - sample.old_logp.detach())
```

## 追问

**DPO 的旧偏好对能一直用吗？**
它是离线数据，但参考 logprob 仍要保存在数据中，或用冻结的参考模型重算。这里重算的是 $\pi_{\mathrm{ref}}$，与 rollout 回放中采样时的旧策略不同。

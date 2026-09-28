---
id: sys-replay
section: systems
order: 70
level: B
title: 系统：旧的 rollout 能不能留到下一步再训？
quick: >-
  能留，但每条要带着采样时的 logprob 和权重版本。当前策略离那一版越远，重要性采样比越散，clip 掉的 token 越多。
  没有旧 logprob 的轨迹不能补训。奖励可以复用，对数概率不能事后用新权重重算来冒充旧的。
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

## 题怎么来的

生成贵，就会把轨迹存下来多更新几次。issue 1524 写了多次更新如何离开 on-policy。这道把「存到下一步」单独拿出来。异步落后几步见 `sys-async-stale`。

## 能复用的

文本、奖励、采样时的 token logprob、权重版本、mask。这些在采样结束时就固定了。下一步用新策略算新的 logprob，比用旧的那份当 $\pi_{\mathrm{old}}$。

不能复用的是「当时没存 logprob，现在用当前模型再跑一遍当作旧的」。当前模型已经 step 过，算出来的是 $\pi_{\theta}$，比变成 1，off-policy 被藏掉，优势却还是旧奖励。更新方向是错的。

## 何时丢掉

版本差超过预算，或者比的方差大到 clip 比例接近 1，这批旧轨迹不再提供梯度。继续训只是在重复 clip 之后的零梯度。奖励特别高的旧样本更不能无限留：策略已经变了，那条高奖励可能是旧政策才会走出的路径。

GRPO 的组要整组留或整组丢。只留下组里奖励高的几条，均值就不是当时的组均值。

## 代码

```python
import torch

def replay_ratio(new_logp, sample):
    if sample.old_logp is None:
        raise RuntimeError("cannot recompute old logprob with the new weights")
    return torch.exp(new_logp - sample.old_logp.detach())
```

## 追问

**DPO 的旧偏好对能一直用吗？** 那是离线数据，参考模型的 logprob 要在数据里，或者用冻结的参考模型重算。重算用的是 $\pi_{\mathrm{ref}}$，不是最新策略。和 rollout 回放不是同一个指针。

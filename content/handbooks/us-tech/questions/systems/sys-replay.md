---
id: sys-replay
section: systems
order: 70
level: B
title: 系统：旧的 rollout 能不能留到下一步再训？
quick: >-
  假设生成服务还在用版本 10，而训练已经到了版本 15。这些回答来自旧策略，不能因为刚刚送到 trainer 就称它们是当前策略的 on-policy
  数据。
tags:
  - Post-train
  - Replay
  - Off-policy
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: verl issue 1524
    url: 'https://github.com/verl-project/verl/issues/1524'
    type: primary
---

## 回答思路

> **问题与场景：** 假设生成服务还在用版本 10，而训练已经到了版本 15。
>
> **做法与原因：** 我会给每条 rollout 记录生成权重版本、时间和行为 log-probability，并限制训练可接受的滞后。
>
> **检查与取舍：** throughput 之外，还要看滞后分布、ratio、有效样本和独立成功率。

## 可以这样回答

假设生成服务还在用版本 10，而训练已经到了版本 15。这些回答来自旧策略，不能因为刚刚送到 trainer 就称它们是当前策略的 on-policy 数据。

我会给每条 rollout 记录生成权重版本、时间和行为 log-probability，并限制训练可接受的滞后。Importance correction 可以处理某些分布差异，但策略相差太大时会很不稳定。

throughput 之外，还要看滞后分布、ratio、有效样本和独立成功率。若奖励涨而任务变差，需要检查陈旧数据与评分偏差，而不是只继续加生成并发。

## 技术备查

旧 rollout 可以留到下一步训练，前提是 sampling 时就存好 token logprob 和权重版本，再用 importance sampling 比修正策略变化。生成很贵，复用能省开销；代价是数据会越来越偏离当前策略。verl issue 1524 讨论的多次更新就是这个问题，异步落后几步的情况见 `sys-async-stale`。

一次 sampling 完成时，文本、奖励、sampling logprob、权重版本和 mask 都固定下来。下一步用新策略算新的 logprob，旧值作为 $\pi_{\mathrm{old}}$。如果当时没存，现在拿更新后的模型重跑，算出来的是 $\pi_{\theta}$，importance sampling 比会被伪装成 1，而优势仍来自旧轨迹，更新方向就可能出错。

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
它是离线数据，但参考 logprob 仍要保存在数据中，或用冻结的 reference model 重算。这里重算的是 $\pi_{\mathrm{ref}}$，与 rollout 回放中 sampling 时的旧策略不同。

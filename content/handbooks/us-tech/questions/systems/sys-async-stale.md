---
id: sys-async-stale
section: systems
order: 56
level: A
title: 系统：异步 rollout 的权重比训练旧几步，loss 里要带什么？
quick: >-
  生成可以比优化器落后几步，用来把卡占满。落后的样本不是当前策略抽的。
  重要性采样的分母用采样当时的 logprob，并记下那一步的版本。落后太多就丢掉，不要无限堆旧轨迹。
tags:
  - Post-train
  - Async
  - Off-policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl issue 1524, mini-batch 更新几次就离开 on-policy
    url: https://github.com/verl-project/verl/issues/1524
    type: primary
---

## 题怎么来的

卡不要在「等生成」和「等训练」之间空转，就会把 采样轨迹（rollout） 做成异步。issue 1524 已经写了：一个 rollout batch 里更新多次，后面的更新就不是 on-policy。异步是把这个差距拉到跨步。这道按这个机制拟的。

## 要记下的

每条轨迹带一个权重版本号，和采样时的 token logprob。训练用现在的策略再算 logprob，比是 $\exp(\log\pi_{\theta}-\log\pi_{\mathrm{old}})$，$\pi_{\mathrm{old}}$ 是采样那一版，不是上一次优化器 step 的便利近似。版本差 0 才是严格同策。

差 1 到 2 步通常还用重要性采样比修。差得更大，比的方差上去，clip 会把大多数 token 卡死，更新名存实亡。设一个最大落后步数，超过的轨迹丢掉，生成侧用新权重重采。

## 不要省的同步

版本号和 logprob 必须跟轨迹走，不能事后用「当前推理引擎里的权重」补算。引擎可能已经换过权重。补算出来的分母是另一份策略。

共置时如果生成和训练在同一组卡上轮流，异步的重叠有限。真正把等待藏掉，是拆成两组卡，见 `sys-rollout-place`。

## 代码

```python
import torch

def ratio_or_drop(new_logp, old_logp, version, train_step, max_lag, mask):
    if train_step - version > max_lag:
        return None
    ratio = torch.exp(new_logp - old_logp.detach())
    return ratio * mask
```

## 追问

**KL 的参考模型用哪一版？** 参考模型是阶段初冻结的那份，不随这几步落后变化。不要把 $\pi_{\mathrm{old}}$ 和 $\pi_{\mathrm{ref}}$ 写成同一个指针。

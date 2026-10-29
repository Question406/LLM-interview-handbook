---
id: sys-async-stale
section: systems
order: 56
level: A
title: 系统：异步 rollout 的权重比训练旧几步，loss 里要带什么？
quick: >-
  异步轨迹携带 sampling 版本和当时的 token logprob，训练用当前 logprob 与它计算 importance sampling
  比。超过最大版本落后的轨迹直接丢弃并重采，避免旧数据堆积让比率方差和 clipping 失控。
tags:
  - Post-train
  - Async
  - Off-policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: 'verl issue 1524, mini-batch 更新几次就离开 on-policy'
    url: 'https://github.com/verl-project/verl/issues/1524'
    type: primary
---

异步 rollout 的每条轨迹都要带 sampling 权重版本与当时的 token logprob，loss 的 importance sampling 分母用那一版策略。比如生成比训练落后几步，就不能拿“上一次优化器 step”的概率代替真正生成它的概率。

异步 rollout 用 sampling 与训练重叠来减少等待。veRL issue 1524 指出，同一 rollout batch 多次更新后，后续更新已偏离 on-policy；跨步异步会把这种策略差距进一步扩大，这题按该机制整理。

每条轨迹带一个权重版本号，和 sampling 时的 token logprob。训练用现在的策略再算 logprob，比是 $\exp(\log\pi_{\theta}-\log\pi_{\mathrm{old}})$，$\pi_{\mathrm{old}}$ 是 sampling 那一版，不是上一次优化器 step 的便利近似。版本差 0 才是严格同策。

差 1 到 2 步通常还用 importance sampling 比修。差距更大时，比率方差可能上升，大量 token 被 clip，实际更新信号变弱。设一个最大落后步数，超过的轨迹丢掉，生成侧用新权重重采。

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

**KL 的 reference model 用哪一版？**
用阶段初冻结的 reference model，不随 sampling 落后这几步变化。不要把 $\pi_{\mathrm{old}}$ 和 $\pi_{\mathrm{ref}}$ 写成同一个指针。

---
id: sys-rollout-logprob
section: systems
order: 45
level: S
title: 系统：on-policy 时 rollout 的 logprob 和训练前向对不上，先查什么？
quick: >-
  同一份权重、同一次采样，旧 logprob 和新 logprob 应该一致，重要性采样比是 1。
  对不上时先看 micro batch 是否相同、temperature 和 logprob 的归约方式是否相同，再看是不是用了上一版权重。
tags:
  - Post-train
  - GRPO
  - Logprob
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl issue 2996, on-policy 下 old_log_prob 与 log_prob 不一致
    url: https://github.com/verl-project/verl/issues/2996
    type: primary
  - title: verl 配置，calculate_log_probs 与 micro batch
    url: https://verl.readthedocs.io/en/latest/examples/config.html
    type: primary
---

## 题怎么来的

verl issue 2996 报的是：GRPO 把 `train_batch_size` 设成等于 `ppo_mini_batch_size`，本该 on-policy，`old_log_prob` 和训练前向再算的 `log_prob` 仍然不一样。后续讨论把它收成一类一致性问题，不是单次面经。面试问「比为什么不是 1」时，按这个清单答。Anthropic 那道 GRPO 脚本见 `anthropic-grpo-debug`，那里的比偏离 1 还有 mini-epoch 这一个原因。

## 先排除的三件事

采样时的 temperature、top-p 必须和重算 logprob 时相同。采样用了 temperature，重算用裸 logits，每个 token 的对数概率都会偏，而且偏的方向随 token 变，不是一个全局常数。

两边的 micro batch 要一样。issue 的临时办法是让 采样轨迹（rollout） 算 logprob 的 `log_prob_micro_batch_size_per_gpu` 等于训练的 `ppo_micro_batch_size_per_gpu`。batch 形状不同，padding 和变长序列的归约会差一截。

`logprobs_mode` 要一致。有的实现存的是被 temperature 除过、再经过 top-p 截断后的分布，有的是训练前向的完整词表 log_softmax。用错一份，clip 的区间仍然围着 1，但比值已经不在 1 附近。

## 然后才是算法

确认上面三件之前，不要把偏差解释成 off-policy。真的 off-policy 是：这一批在更新之前又 step 了一次，或者采样用的是上一版权重。这时比可以离开 1，要用采样时存下来的 logprob 做分母，并且 `detach`。

全对全错的 GRPO 组优势是 0，比是不是 1 都不会产生更新。先把这种组滤掉，再看剩下的组里比的均值。

## 代码

```python
import torch

def importance_ratio(new_logp, old_logp, mask):
    ratio = torch.exp(new_logp - old_logp.detach())
    denom = mask.sum().clamp(min=1)
    mean = (ratio * mask).sum() / denom
    return ratio, mean  # mean should be near 1 on the first on-policy update
```

## 追问

**能不能直接用 rollout 引擎吐出的 logprob，不再重算？** 可以，verl 用 `calculate_log_probs` 打开这条路。前提是那份 logprob 的定义和 损失（loss） 里的一致。省一次前向，少一次对账的机会。

**差在 1e-3，要不要停？** bf16 上最后几位可以差。差到比值均值明显离开 1，或随序列位置变大，就是 mask、shift 或权重版本错了，不是舍入。

## 相关题

- [[anthropic-grpo-debug]]：Anthropic 调试题修完 bug 后会问 ratio 为什么不是 1，这张就是那个追问的排查顺序。
- [[p3a-anthropic-rl-fundamentals-grpo-debug]]：同一道 Anthropic 题的另一份整理，追问 on-policy 和 off-policy 时 ratio 为什么偏离 1。
- [[coding-tis-mismatch]]：排除了 bug 之后剩下的真实 mismatch，用截断重要性权重 $\min(\pi_{\mathrm{old}}/\mu, C)$ 修正。
- [[coding-token-logprob]]：训练端重算 logprob 的白板题，shift 和温度正是这里要先排除的两项。

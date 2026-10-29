---
id: sys-rollout-logprob
section: systems
order: 45
level: S
title: 系统：on-policy 时 rollout 的 logprob 和训练前向对不上，先查什么？
quick: >-
  第一次 on-policy 更新前，同权重、同概率定义下的新旧 logprob 应接近一致，importance sampling 比应接近 1。先核对
  temperature、top-p、micro batch 和 logprobs_mode，再查 mask、shift 与权重版本，避免把实现差异误当成
  off-policy。
tags:
  - Post-train
  - GRPO
  - Logprob
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: 'verl issue 2996, on-policy 下 old_log_prob 与 log_prob 不一致'
    url: 'https://github.com/verl-project/verl/issues/2996'
    type: primary
  - title: verl 配置，calculate_log_probs 与 micro batch
    url: 'https://verl.readthedocs.io/en/latest/examples/config.html'
    type: primary
---

第一次 on-policy 更新前，如果权重和 logprob 定义一致，新旧 logprob 应接近相等，importance sampling 比也应接近 1。对不上时先核对 sampling 与训练实现，再判断是否真的用了旧策略。

verl issue 2996 就报告过这个现象：`train_batch_size` 等于 `ppo_mini_batch_size`，GRPO 本该 on-policy，`old_log_prob` 与训练重算的 `log_prob` 仍不同。这是一类一致性问题的公开案例。

我会先对齐 temperature 和 top-p。sampling 经过 temperature、重算却用裸 logits，每个 token 的 logprob 都可能偏，偏差也不是全局常数。再核对 `logprobs_mode`：一边记录 temperature 与 top-p 截断后的概率，另一边用完整 vocabulary log_softmax，二者定义不同，clip 仍围绕 1，却在使用失配的比值。

接着核对 micro batch。issue 中的临时办法是让 rollout 的 `log_prob_micro_batch_size_per_gpu` 与训练的 `ppo_micro_batch_size_per_gpu` 相同。batch 形状、padding 和变长序列归约不一致，都可能造成差异。

这些检查过后，再查是否额外 step 过，或 rollout 用上一版权重。那才是真实 off-policy，应保留 sampling logprob 作分母并 `detach`。全对或全错的 GRPO 组优势为 0，无论比值是否为 1 都不更新，可以先滤掉这些组再看其余组的均值。Anthropic 的 `anthropic-grpo-debug` 还会因为 mini-epoch 让比值偏离 1。

下面计算响应 mask 内的平均 importance sampling 比：

```python
import torch


def importance_ratio(new_logp, old_logp, mask):
    ratio = torch.exp(new_logp - old_logp.detach())
    denom = mask.sum().clamp(min=1)
    mean = (ratio * mask).sum() / denom
    return ratio, mean  # mean should be near 1 on the first on-policy update
```

## 追问

**能直接用 rollout 引擎返回的 logprob 吗？**
可以，verl 的 `calculate_log_probs` 支持这条路径，前提是概率定义与损失（loss）一致。这样省一次前向，也少了一次重新核对两边结果的机会。

**差 1e-3 要停吗？**
bf16 最后几位可能有误差。若均值明显偏离 1，或偏差随序列位置变大，要查 mask、shift 或权重版本，不能归因于舍入。

## 相关题

- [[anthropic-grpo-debug]]：修完 bug 后解释 ratio 为什么仍不等于 1。
- [[p3a-anthropic-rl-fundamentals-grpo-debug]]：同一 Anthropic 题的另一份整理。
- [[coding-tis-mismatch]]：排除 bug 后的真实 mismatch，用 $\min(\pi_{\mathrm{old}}/\mu, C)$ 截断重要性权重。
- [[coding-token-logprob]]：训练端重算 logprob，核对 shift 与温度。

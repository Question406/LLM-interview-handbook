---
id: coding-token-logprob
section: coding
order: 42
level: S
title: 白板：从 logits 取 response 的 token logprob，shift、temperature 和显存
quick: >-
  位置 $t$ 的 logits 预测的是 $t+1$ 的 token，先 `logits[:, :-1]` 对 `ids[:, 1:]`。
  采样时用了 temperature，训练端重算也要除以同一个 $T$，否则第一步 ratio 就不是 1。
  `gather` 取目标 logit 再减 `logsumexp`，不必物化一份 fp32 的完整 log_softmax。
tags:
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: torch.gather
    url: https://pytorch.org/docs/stable/generated/torch.gather.html
    type: primary
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
---

## 题怎么来的

所有 RL loss 的输入都是 `policy_logprobs`，它从这一步来。这几行错了，后面的 ratio、KL、clip 全是错的，而且 loss 看起来照样在降。常和 `coding-tis-mismatch`、`sys-rollout-logprob` 一起问。

给你的代码：

```python
def token_logprobs(logits, input_ids, temperature):
    # logits: [B, L, V]；input_ids: [B, L] = prompt + response
    logp = torch.log_softmax(logits, dim=-1)
    return logp.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)
```

## 错在哪

**没有 shift。** causal LM 在位置 $t$ 输出的是 $p(x_{t+1}\mid x_{\le t})$。这段代码取的是 $p(x_t\mid x_{\le t})$ 位置上 $x_t$ 的概率，每个 token 都错开一位。

**temperature 没用上。** 采样时的分布是 $\mathrm{softmax}(z/T)$，rollout 存下的 logprob 也是这个分布下的。训练端用 $\mathrm{softmax}(z)$ 重算，同样的权重算出来的 ratio 也不是 1，clip 被无意义地触发。$T$ 要和采样时完全一致。

**精度和显存。** logits 往往是 bf16，直接 `log_softmax` 精度不够。先 `.float()` 又会复制一份 `[B, L, V]`。$V$ 在 15 万左右、$L$ 一万时，一条序列的 fp32 logits 就是 6 GB，batch 稍大就是几十 GB。

## 改法

```python
def token_logprobs(logits, input_ids, temperature=1.0):
    logits = logits[:, :-1].float() / temperature        # [B, L-1, V]
    targets = input_ids[:, 1:]                            # [B, L-1]
    picked = logits.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return picked - torch.logsumexp(logits, dim=-1)       # [B, L-1]
```

$\log p(y) = z_y - \log\sum_v e^{z_v}$。`logsumexp` 内部减最大值，数值稳定，结果只是 `[B, L-1]`。返回的第 $t$ 个位置对应 `input_ids[:, t+1]`，response mask 也要同样左移一位：`mask[:, 1:]`。

`.float()` 仍然复制了一份 logits。显存吃紧时沿序列切块算：

```python
def token_logprobs_chunked(logits, input_ids, temperature=1.0, chunk=1024):
    out = []
    targets = input_ids[:, 1:]
    for s in range(0, logits.shape[1] - 1, chunk):
        z = logits[:, s:s + chunk].float() / temperature
        z = z[:, : targets.shape[1] - s]
        y = targets[:, s:s + chunk]
        out.append(z.gather(-1, y.unsqueeze(-1)).squeeze(-1) - torch.logsumexp(z, dim=-1))
    return torch.cat(out, dim=1)
```

更进一步是不物化完整 logits，把 lm_head 和这一步融合在一起，见 `coding-fused-ce`。

## 验证

```python
B, L, V = 2, 6, 11
logits = torch.randn(B, L, V)
ids = torch.randint(0, V, (B, L))
ref = torch.log_softmax(logits[:, :-1] / 0.7, -1).gather(-1, ids[:, 1:, None]).squeeze(-1)
assert torch.allclose(token_logprobs(logits, ids, 0.7), ref, atol=1e-6)
assert torch.allclose(token_logprobs_chunked(logits, ids, 0.7, chunk=2), ref, atol=1e-6)
```

## 追问

**采样时还用了 top-p / top-k 呢？** 采样分布是截断后重新归一化的，训练端用完整 softmax 算的 logprob 和它不一致。要么让推理引擎返回完整分布下的 logprob，要么两端用同一套截断规则。先确认你的推理引擎返回的是哪一个。

**只要 response 的 logprob，prompt 部分能不能不算？** lm_head 和 logsumexp 都可以只在 response 位置上做，prompt 长的时候省很多。前向的 hidden state 仍然要算全序列。

**熵要不要顺便算？** 同样一份 `z`，$H = \mathrm{logsumexp}(z) - \sum_v \mathrm{softmax}(z)_v z_v$。又要一次 softmax，显存和上面一样要切块。见 `openai-entropy-l1`。

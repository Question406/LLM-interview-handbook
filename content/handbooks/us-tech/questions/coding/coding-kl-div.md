---
id: coding-kl-div
section: coding
order: 19
level: S
title: 白板：token 级 KL（策略 vs 参考策略），reduction 和 ignore pad
quick: >-
  $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})=\sum_v\pi(v)(\log\pi(v)-\log\pi_{\mathrm{ref}}(v))$。沿词表求和，再对
  非 pad token 做均值。PyTorch `kl_div` 的 `input` 是 log $q$，`target` 是 $p$，算的是
  $\mathrm{KL}(p\|q)$。`reduction='mean'` 会再除以 $V$，要用 `batchmean` 或自己 mask。
tags:
  - Coding
  - KL
  - RLHF
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.functional.kl_div
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.kl_div.html
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

## 题怎么来的

InstructGPT / PPO 式 RLHF 在奖励里减 $\beta\,\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$。OpenAI / Anthropic 白板要写清：token 级怎么落、pad 进不进分母、方向哪边是 $\pi$。方向和为什么用反向 KL 见 `align-rlhf-kl`、`openai-instructgpt-kl`。本题把公式写成可跑的 reduction。常见植入：`F.kl_div` 参数对调、`mean` 除掉词表维、pad 当有效 token。

## 全词表 KL 和采样路径

对每个位置的分布：

$$
\mathrm{KL}\big(\pi(\cdot\mid x_{1:t-1})\|\pi_{\mathrm{ref}}(\cdot\mid x_{1:t-1})\big)
=\sum_{v=1}^{V}\pi_t(v)\big(\log\pi_t(v)-\log\pi_{\mathrm{ref},t}(v)\big).
$$

这是非负标量，形状从 `[B, T, V]` 收到 `[B, T]`。序列级再对 mask 平均：分母是有效 token 数，不是 $B\cdot T$。one-hot 标签时这条 KL 不是 CE；CE 是 $-\log\pi(y)$，关系见 `coding-cross-entropy`、`coding-logsumexp`。

PPO 里更常见的是沿采样 token 的 MC：$\log\pi_\theta(y_t)-\log\pi_{\mathrm{ref}}(y_t)$。$y\sim\pi_\theta$ 时，它对词表 KL 无偏。不要把 MC 项再乘一遍 $\pi(y_t)$。teacher-forcing 的全词表 KL 和 rollout 的 MC 不是同一个数，监控时别混着画。

```python
import torch
import torch.nn.functional as F

def token_kl_full(logits, logits_ref, mask):
    # logits*: [B, T, V]; mask: [B, T] True=keep
    log_pi = F.log_softmax(logits.float(), dim=-1)
    log_ref = F.log_softmax(logits_ref.float(), dim=-1)
    kl = (log_pi.exp() * (log_pi - log_ref)).sum(dim=-1)
    return kl[mask].mean()

def token_kl_sampled(logp, logp_ref, mask):
    # 采样路径；logp*: [B, T]
    return ((logp - logp_ref).float())[mask].mean()

def kl_div_footgun(log_pi, log_ref):
    # [N, V]；要对 KL(pi || ref) 用 batchmean，且 input 是 log ref
    pi = log_pi.exp()
    wrong_mean = F.kl_div(log_ref, pi, reduction="mean")
    ok = F.kl_div(log_ref, pi, reduction="batchmean", log_target=False)
    return ok, wrong_mean
```

`F.kl_div(input, target)` 算 $\mathrm{KL}(\mathrm{target}\|\mathrm{input})$。要 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$：`input=log_ref`，`target=pi`。`log_target=True` 时 target 也是 log 域。`mean` 把所有元素（含 $V$）平均进去，比真 KL 小约 $V$ 倍。

## pad、shift、$\beta$

Causal LM 仍只对 `logits[:, :-1]` 对 `labels[:, 1:]`。pad / ignore 下标不进 `mask.sum()`。不要 `kl * mask` 之后仍除以 $T$。fp16 下 softmax 再 log 会下溢，全程 `log_softmax`。$\beta$ 乘在序列均值 KL 上，和 PPO clip 相对 $\pi_{\mathrm{old}}$ 不是同一项。

## 追问

- **为什么 `reduction='mean'` 是错的？** 文档写得很清楚：`mean` 除的是全体元素个数。分布之间的 KL 应对 batch（或 token）平均，所以是 `batchmean`。
- **正向 KL 能直接换 input 吗？** $\mathrm{KL}(\pi_{\mathrm{ref}}\|\pi)$ 是 `input=log_pi`、`target=pi_ref`。RLHF 默认不要这条，见 `align-rlhf-kl`。
- **只对采样 token 做差还要 sum 词表吗？** 不要。MC 已经在 $y_t$ 上取值。再 sum $V$ 是把另一条估计叠上去。
- **mask 全假怎么办？** 分母 clamp 到 $1$ 或直接返回 $0$。空 batch 上 `mean` 是 NaN。

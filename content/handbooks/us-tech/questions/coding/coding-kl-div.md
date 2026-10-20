---
id: coding-kl-div
section: coding
order: 19
level: S
title: 白板：token 级 KL（策略 vs 参考策略），reduction 和 ignore pad
quick: "每个位置沿词表算 $\\mathrm{KL}(\\pi\\|\\pi_{\\mathrm{ref}})$，再对非 pad token 取均值；`F.kl_div(log_ref, pi)` 才是这个方向，且要用 `batchmean`。"
tags:
  - 完整编程练习
  - Coding
  - KL
  - RLHF
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: torch.nn.functional.kl_div
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.kl_div.html
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `token_kl_full(logits, logits_ref, mask) -> 标量`：`logits*` 形状 `[B, T, V]`，`mask` 形状 `[B, T]`（True 表示有效 token）。每个位置沿完整词表算 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$，再对有效 token 取平均。
- `token_kl_sampled(logp, logp_ref, mask) -> 标量`：`logp*` 形状 `[B, T]`，是采样 token 在两边的 log 概率。返回 log-ratio 在有效 token 上的平均，作为 KL 的采样估计；单个样本可以是负数。
- `kl_div_footgun(log_pi, log_ref) -> (正确值, 错误值)`：演示 `F.kl_div` 的正确用法（`batchmean`）和 `reduction="mean"` 的错误结果，输入形状 `[N, V]`。
- `mask` 全为 False 时返回 0，并且仍然可以反传（梯度为 0）。reference 固定，不接梯度。

### 输入输出示例

```text
π = ref                       -> token_kl_full = 0
π = [0.75, 0.25], ref = [0.5, 0.5] -> token_kl_full ≈ 0.130812
logp = -2, logp_ref = -1      -> token_kl_sampled = -1   # 单样本估计可以为负
```

### 解题思路与正确性

全词表 KL 是 $\pi$ 加权下的期望，所以要用 $\pi$ 的概率去乘 $\log\pi-\log\pi_{\mathrm{ref}}$，再沿词表求和。全程用 `log_softmax`，避免先 softmax 再取 log 时下溢。

采样版只看实际采到的 token，$\log\pi(y_t)-\log\pi_{\mathrm{ref}}(y_t)$ 在 $y_t\sim\pi$ 时期望等于 KL。单个样本出现负值并不说明 KL 可以为负，只说明这是有方差的估计。

用 `F.kl_div` 时，`input` 要传 `log_ref`、`target` 传 `pi`，得到的才是 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def token_kl_full(logits, logits_ref, mask):
    """全词表 KL(π || π_ref) 在有效 token 上的平均。logits*: [B, T, V]；mask: [B, T]，True 为有效。"""
    log_pi = F.log_softmax(logits.float(), dim=-1)
    log_ref = F.log_softmax(logits_ref.float(), dim=-1)
    kl = (log_pi.exp() * (log_pi - log_ref)).sum(dim=-1)  # [B, T]
    if not bool(mask.any()):
        return logits.sum() * 0.0  # 空 mask：返回可反传的 0，不是 NaN
    return kl[mask].mean()


def token_kl_sampled(logp, logp_ref, mask):
    """采样 token 的 log-ratio 平均，是 KL 的蒙特卡洛估计。logp*: [B, T]。"""
    if not bool(mask.any()):
        return logp.sum() * 0.0
    return (logp - logp_ref).float()[mask].mean()


def kl_div_footgun(log_pi, log_ref):
    """[N, V]。返回 (batchmean 的正确 KL, reduction='mean' 的错误值)。"""
    pi = log_pi.exp()
    correct = F.kl_div(log_ref, pi, reduction="batchmean", log_target=False)
    wrong_mean = F.kl_div(log_ref, pi, reduction="mean")  # 多除了一个 V
    return correct, wrong_mean
```

### 可执行测试

```python
torch.set_num_threads(1)

pi = torch.tensor([[[0.75, 0.25]]])
ref = torch.tensor([[[0.5, 0.5]]])
mask = torch.ones(1, 1, dtype=torch.bool)

# 全词表 KL 等于按定义手算的值
kl = token_kl_full(pi.log(), ref.log(), mask)
expected = (pi * (pi.log() - ref.log())).sum()
assert torch.allclose(kl, expected)
assert abs(kl.item() - 0.130812) < 1e-5

# 两个分布相同时 KL 为 0
assert token_kl_full(pi.log(), pi.log(), mask) == 0

# 空 mask 返回 0，且梯度为 0
logits = pi.log().requires_grad_()
empty = token_kl_full(logits, ref.log(), torch.zeros_like(mask))
assert empty == 0
assert torch.all(torch.autograd.grad(empty, logits)[0] == 0)

# pad token 不进分母
logits2 = torch.cat([pi.log(), ref.log()], dim=1)  # 第 2 个位置 KL = 0
ref2 = torch.cat([ref.log(), ref.log()], dim=1)
keep_first = torch.tensor([[True, False]])
assert torch.allclose(token_kl_full(logits2, ref2, keep_first), expected)

# 采样估计的单样本值可以为负
assert token_kl_sampled(torch.tensor([[-2.0]]), torch.tensor([[-1.0]]), mask) == -1

# batchmean 等于真实 KL，mean 恰好小 V 倍
correct, wrong = kl_div_footgun(pi.log()[0], ref.log()[0])
assert torch.allclose(correct, expected)
assert torch.allclose(wrong * 2, correct)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$、词表大小 $V$。`token_kl_full` 的时间和空间都是 $O(BTV)$，`token_kl_sampled` 是 $O(BT)$。

- 追问「采样估计一定无偏吗」：只有 token 确实采自当前 $\pi$ 时才无偏。如果数据来自旧策略或别的分布，需要做重要性校正，不能无条件说它无偏。

## 题怎么来的

InstructGPT / PPO 式的基于人类反馈的强化学习（RLHF）会在奖励里减去 $\beta\,\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$。OpenAI / Anthropic 的白板题要求写清楚：token 级 KL 怎么算，pad 进不进分母，KL 的哪一边是 $\pi$。KL 方向以及为什么用反向 KL 见 `align-rlhf-kl`、`openai-instructgpt-kl`。这道题要求把公式落成能跑的 reduction。常见的植入 bug 有三种：`F.kl_div` 参数对调、`mean` 把词表维也平均掉、pad 被当成有效 token。

## 全词表 KL 和采样路径

每个位置的分布之间的 KL 是：

$$
\mathrm{KL}\big(\pi(\cdot\mid x_{1:t-1})\|\pi_{\mathrm{ref}}(\cdot\mid x_{1:t-1})\big)
=\sum_{v=1}^{V}\pi_t(v)\big(\log\pi_t(v)-\log\pi_{\mathrm{ref},t}(v)\big).
$$

它是一个非负标量，张量形状从 `[B, T, V]` 缩减到 `[B, T]`。到序列级再按 mask 平均，分母是有效 token 数，不是 $B\cdot T$。注意这不是交叉熵损失（CE）：用 one-hot 标签时 CE 是 $-\log\pi(y)$，两者关系见 `coding-cross-entropy`、`coding-logsumexp`。

PPO 里更常见的是只在采样 token 上做蒙特卡洛估计：$\log\pi_\theta(y_t)-\log\pi_{\mathrm{ref}}(y_t)$。$y\sim\pi_\theta$ 时它对全词表 KL 是无偏的。不要再给这一项乘一遍 $\pi(y_t)$。teacher forcing 下的全词表 KL 和采样轨迹（rollout）上的估计不是同一个数，监控时不要画在同一条曲线上。

`F.kl_div(input, target)` 算的是 $\mathrm{KL}(\mathrm{target}\|\mathrm{input})$，其中 `input` 是 log 概率。要得到 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$，就传 `input=log_ref`、`target=pi`。`log_target=True` 时 target 也要传 log 概率。`reduction="mean"` 会对所有元素（包括 $V$ 这一维）取平均，结果恰好比真实 KL 小 $V$ 倍。

## pad、shift、$\beta$

Causal LM 仍然是 `logits[:, :-1]` 对齐 `labels[:, 1:]`。pad 和 ignore 的位置不计入 `mask.sum()`，也不要算完 `kl * mask` 之后仍然除以 $T$。fp16 下先 softmax 再 log 会下溢，所以全程用 `log_softmax`。$\beta$ 乘在序列平均 KL 上；它和 PPO 里相对 $\pi_{\mathrm{old}}$ 的 clip 不是同一项。

## 追问

- **为什么 `reduction='mean'` 是错的？** 文档写得很清楚：`mean` 除以的是全体元素个数。分布之间的 KL 应该按 batch（或 token）平均，所以要用 `batchmean`。
- **正向 KL 能直接换 input 吗？** 能。$\mathrm{KL}(\pi_{\mathrm{ref}}\|\pi)$ 就是 `input=log_pi`、`target=pi_ref`。但 RLHF 默认不用这个方向，见 `align-rlhf-kl`。
- **只对采样 token 做差，还要沿词表求和吗？** 不要。蒙特卡洛估计已经在 $y_t$ 上取了值，再对 $V$ 求和等于叠加了另一种估计。
- **mask 全为 False 怎么办？** 把分母 clamp 到 $1$，或者直接返回 $0$。在空张量上 `mean` 会得到 NaN。

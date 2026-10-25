---
id: coding-cispo
section: coding
order: 39
level: A
title: 白板：CISPO 和 PPO clip 的区别，clip 的是权重还是梯度
quick: "PPO 在触发 clip 的方向让 token 不再提供梯度，CISPO 则把 IS 权重截到边界并 detach，再乘 logprob，token 仍可学习。比如正优势、ratio 为 2 时，示例 PPO 权重为 0，CISPO 截成 1.28；空 mask 还要返回可反传的 0。"
tags:
  - 完整编程练习
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention (CISPO)"
    url: https://arxiv.org/abs/2506.13585
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题目描述

实现 CISPO 的逐 token 加权 log-prob 损失，并提供 CISPO 与 PPO 对应的梯度权重接口。题目关心前向数值和对当前策略 log-prob 的梯度：重要性权重只作为常量使用，不能反向传播进旧策略或优势。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28) -> 标量`：按 CISPO 计算损失，对 mask 里的有效 token 取平均。
- `ppo_weight(ratio, adv, eps=0.2)`：把 PPO clip 目标写成加权 logprob 时，每个 token 的权重。
- `cispo_weight(ratio, adv, eps_low=1.0, eps_high=0.28)`：CISPO 对应的权重。
- 约束：`policy_logprobs`、`old_logprobs`、`mask` 都是 `[B, T]`，`advantages` 能广播到 `[B, T]`。`old_logprobs` 和 `advantages` 视为常量；ratio 截断后要 detach。mask 全为 0 时返回可反传的 0。
- 令 `r = exp(policy_logprobs - old_logprobs)`，`c = clamp(r, 1-eps_low, 1+eps_high)`。`cispo_loss = -sum(mask * stop_gradient(c) * advantages * policy_logprobs) / sum(mask)`。mask 为 0/1，非空时分母为有效 token 数，空时按上述零损失约定。
- `cispo_weight = stop_gradient(clamp(ratio,1-eps_low,1+eps_high)*adv)`。`ppo_weight` 在 `(adv>=0 且 ratio<=1+eps)` 或 `(adv<0 且 ratio>=1-eps)` 时为 `stop_gradient(ratio*adv)`，其他位置为 0。两个权重函数接受可广播张量，返回广播后的形状。

### 示例

```text
ratio = 2, A = 1
cispo_weight(eps_high=0.28)  -> 1.28   # 截到上界，仍有梯度
ppo_weight(eps=0.2)          -> 0      # 出界，PPO 不再更新这个 token
ratio = 1.1, A = 2           -> 两者都是 2.2
```

## 解题思路与参考答案

我会把两者都写成常数权重乘 logprob，再看权重和梯度。PPO 在满足 clip 条件时让对应 token 停止更新，CISPO 只截断 IS 权重并 detach，仍保留 token 的梯度。比如正优势、ratio 为 2 的示例，PPO 权重变成 0，CISPO 保留 1.28。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28) -> 标量`：按 CISPO 计算损失，对 mask 里的有效 token 取平均。
- `ppo_weight(ratio, adv, eps=0.2)`：把 PPO clip 目标写成加权 logprob 时，每个 token 的权重。
- `cispo_weight(ratio, adv, eps_low=1.0, eps_high=0.28)`：CISPO 对应的权重。
- 约束：`policy_logprobs`、`old_logprobs`、`mask` 都是 `[B, T]`，`advantages` 能广播到 `[B, T]`。`old_logprobs` 和 `advantages` 视为常量；ratio 截断后要 detach。mask 全为 0 时返回可反传的 0。
- 测试要证明：ratio 出界的 token 在 CISPO 下仍有梯度，而 PPO 会把它置零。

### 输入输出示例

```text
ratio = 2, A = 1
cispo_weight(eps_high=0.28)  -> 1.28   # 截到上界，仍有梯度
ppo_weight(eps=0.2)          -> 0      # 出界，PPO 不再更新这个 token
ratio = 1.1, A = 2           -> 两者都是 2.2
```

### 解题思路与正确性

两种方法都能写成「常数权重 × logprob」的形式，差别只在权重怎么算。PPO 的 clip 出界时整个 token 失活，权重是 0。CISPO 截断的是 IS 权重 $r$ 本身，截完以后乘上优势 $A$，token 仍然参与更新。

截断后的权重必须 detach。否则 $\mathrm{clip}(r)$ 在界内仍是 $\theta$ 的函数，反传时会多出一项 $-A\log\pi\,\nabla\hat r$，得到的就不是 CISPO 的梯度了（推导见下面「错在哪」）。

分母用有效 token 数，并 clamp 到至少 1，这样空 mask 不会除以 0，返回的 0 也还连着计算图。

### 完整参考实现（Python 3）

```python
import math

import torch


def cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28):
    """CISPO 损失：对有效 token 取平均。

    policy_logprobs, old_logprobs, mask: [B, T]；advantages 可广播到 [B, T]。
    IS 权重 r 截断到 [1 - eps_low, 1 + eps_high] 后 detach，只作为 logprob 前的常数系数。
    mask 全为 0 时返回 0（仍可反传，梯度为 0）。
    """
    ratio = torch.exp(policy_logprobs - old_logprobs).detach()
    weight = ratio.clamp(1 - eps_low, 1 + eps_high)
    per_token = -weight * advantages * policy_logprobs
    return (per_token * mask).sum() / mask.sum().clamp(min=1)


def ppo_weight(ratio, adv, eps=0.2):
    """PPO clip 目标写成加权 logprob 时的权重 sg(r * A * active)；出界 token 权重为 0。"""
    active = torch.where(adv >= 0, ratio <= 1 + eps, ratio >= 1 - eps)
    return (ratio * adv * active).detach()


def cispo_weight(ratio, adv, eps_low=1.0, eps_high=0.28):
    """CISPO 的权重 sg(clip(r)) * A；出界 token 仍有权重，只是被截到边界。"""
    return (ratio.clamp(1 - eps_low, 1 + eps_high) * adv).detach()
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(grad, torch.tensor([[-1.28]]))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
torch.set_num_threads(1)

# ratio = 2 超出上界：CISPO 的梯度系数被截到 1.28，仍不为 0
logprobs = torch.tensor([[math.log(2.0)]], requires_grad=True)
old = torch.zeros_like(logprobs)
adv = torch.ones_like(logprobs)
mask = torch.ones_like(logprobs)
loss = cispo_loss(logprobs, old, adv, mask)
(grad,) = torch.autograd.grad(loss, logprobs)
assert torch.allclose(grad, torch.tensor([[-1.28]]))

# 同一个 token，PPO 权重为 0，CISPO 权重为 1.28
ratio = torch.tensor([[2.0]])
assert ppo_weight(ratio, adv).item() == 0
assert torch.allclose(cispo_weight(ratio, adv), torch.tensor([[1.28]]))

# 界内两者相同，都是 r * A
inside = torch.tensor([1.1])
assert torch.allclose(ppo_weight(inside, torch.tensor([2.0])), torch.tensor([2.2]))
assert torch.allclose(cispo_weight(inside, torch.tensor([2.0])), torch.tensor([2.2]))

# A < 0 且 r < 1 - eps：PPO 置零；eps_low = 1 时 CISPO 不设下界，权重是 r * A
low_ratio = torch.tensor([0.5])
negative = torch.tensor([-1.0])
assert ppo_weight(low_ratio, negative).item() == 0
assert torch.allclose(cispo_weight(low_ratio, negative), torch.tensor([-0.5]))

# mask 只取一部分 token：分母是有效 token 数
two_logprobs = torch.tensor([[-1.0, -3.0]], requires_grad=True)
partial = cispo_loss(two_logprobs, two_logprobs.detach(), torch.ones(1, 2), torch.tensor([[1.0, 0.0]]))
assert torch.allclose(partial, torch.tensor(1.0))

# 空 mask：返回 0，且可以反传、梯度为 0
empty = cispo_loss(logprobs, old, adv, torch.zeros_like(mask))
assert empty == 0
assert torch.all(torch.autograd.grad(empty, logprobs)[0] == 0)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$。时间和中间张量都是 $O(BT)$。

- 追问「能不能用 loss 数值相同来验证和 PPO 等价」：不能。这种加权 logprob 写法的 surrogate 标量值和原始 PPO 损失不相等，只有梯度相同；要比较梯度，不比较 loss 值。
- 追问「为什么默认 `eps_low=1.0`」：下界变成 $1-1=0$，等于不截下界，只限制上界。

## 题怎么来的

`fireworks-grpo-sft-loss` 里推导过：PPO / GRPO 的 clipped objective 等价于权重为 $\mathrm{sg}(r A\cdot\mathrm{active})$ 的加权 logprob，active 为假的 token 梯度是 0。MiniMax-M1 观察到，被 clip 掉的往往是 "However"、"Wait" 这类概率低、决定推理走向的分叉 token：第一次更新后它们的 ratio 就出界了，之后几个 off-policy step 里再也拿不到梯度。CISPO 的改法是只截断 IS 权重，不丢弃 token。

目标函数按 token 级平均：

$$
\mathcal{J}_{\mathrm{CISPO}} = \frac{1}{\sum_i|o_i|}\sum_i\sum_t \mathrm{sg}\big(\hat r_{i,t}\big)\,\hat A_{i,t}\,\log\pi_\theta(o_{i,t}),
\qquad
\hat r_{i,t} = \mathrm{clip}\big(r_{i,t},\,1-\varepsilon_{\mathrm{low}},\,1+\varepsilon_{\mathrm{high}}\big)
$$

$\varepsilon_{\mathrm{low}} = 1$ 表示下界是 0，等于不设下界。论文只调上界，具体数值按任务定，这里的 0.28 只是占位。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修复的错误片段，不是参考答案。对照上面的题面，找出它偏离接口或梯度约定的地方；正确实现和测试在前面的练习部分。

```python
def cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28):
    ratio = torch.exp(policy_logprobs - old_logprobs)
    w = ratio.clamp(1 - eps_low, 1 + eps_high)
    per_tok = -w * advantages * policy_logprobs
    return (per_tok * mask).sum() / mask.sum()
```

## 错在哪

主要问题是 `w` 没有 detach。$\hat r$ 本身是 $\theta$ 的函数，损失（loss）的梯度于是变成两项：

$$
\nabla(-\hat r A\log\pi) = -\hat r A\,\nabla\log\pi \;-\; A\log\pi\,\nabla\hat r
$$

第二项在界内等于 $-A\log\pi\cdot r\,\nabla\log\pi$，出界时为 0。$\log\pi$ 是负数，量级也不小，这一项会让界内和界外的 token 表现完全不同，而且它不是任何合理目标函数的梯度。detach 之后只剩第一项，才是 CISPO。

另一个问题是分母直接用 `mask.sum()`，mask 全为 0 时会除以 0 得到 NaN；参考实现用 `clamp(min=1)` 处理。

## 和 PPO 并排

两者都写成 `-(w * logprobs)` 的形式，区别全在 `w`，也就是上面的 `ppo_weight` 和 `cispo_weight`：

| 情况 | PPO | CISPO |
|---|---|---|
| $A>0$，$r > 1+\varepsilon$ | 0 | $(1+\varepsilon_{\mathrm{high}})A$ |
| $A<0$，$r < 1-\varepsilon$ | 0 | $\max(r, 1-\varepsilon_{\mathrm{low}})\cdot A$ |
| $A>0$，$r < 1-\varepsilon$ | $rA$ | $\max(r, 1-\varepsilon_{\mathrm{low}})\cdot A$ |
| $A<0$，$r > 1+\varepsilon$ | $rA$ | $(1+\varepsilon_{\mathrm{high}})A$ |
| 界内 | $rA$ | $rA$ |

PPO 的 clip 相当于信任域：往有利方向走得太远就停下。CISPO 没有这种停止机制，它靠权重有上界来控制单步更新的幅度。

## 追问

**CISPO 还算 policy gradient 吗？**
$r$ 不被截断时，$\mathrm{sg}(r)A\nabla\log\pi$ 就是 off-policy 的重要性采样梯度。截断引入了偏差，换来更小的方差，和 V-trace 截断 IS 权重是同一个思路。

**想要 PPO 的行为怎么办？**
论文给了一个带 token mask 的一般形式，mask 按 PPO 的规则取，就退回 PPO 的梯度。

**为什么用 token 级平均而不是序列平均？**
论文沿用 DAPO 的 token-level loss，长回答里的 token 不会被稀释。见 `coding-grpo-loss-agg`。

## 相关题

- [[coding-loss-atlas]]：总览题，把 PPO、GRPO、CISPO、GSPO 都写成「权重 × logprob」，适合做完这题后对照。
- [[fireworks-grpo-sft-loss]]：同样把 clip 写进 detach 的权重，但那里出界 token 的 mask 置 0，正是 CISPO 要改掉的行为。
- [[openai-ppo-clip]]：概念题，讲 PPO clip 在 RLHF 里限制什么，是这里「PPO 把出界 token 置 0」的背景。
- [[coding-gspo-seq-ratio]]：另一种改 ratio 的方案，把 clip 挪到整条序列上，而不是像 CISPO 那样截 token 权重。
- [[coding-grpo-loss-agg]]：这里沿用 token-level 平均，那张讲三种聚合方式各自带来的长度偏置。
- [[coding-tis-mismatch]]：同样是截断后 detach 的重要性权重，那张截的是推理引擎和训练端的 logprob 差，不是新旧策略的 ratio。

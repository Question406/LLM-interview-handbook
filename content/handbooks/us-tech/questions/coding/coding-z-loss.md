---
id: coding-z-loss
section: coding
order: 23
level: A
title: 白板：PaLM z-loss，为什么往 logits 上加这一项
quick: "z-loss 在 CE 上加 $10^{-4}(\\log Z)^2$：CE 对 logits 平移不变，$\\log Z$ 却会漂移，bf16 下数值变差；z-loss 把它拉回 0 附近，不改分类结果。"
tags:
  - 完整编程练习
  - Coding
  - Z-loss
  - PaLM
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `ce_with_z_loss(logits, target, ignore_index=-100, z_coef=1e-4) -> (total, ce, z_loss)`：返回总 loss、交叉熵和未乘系数的 $\mathrm{mean}(\log Z^2)$，三者都只对有效 token 平均。
- 约束：`logits` 是 `[B, T, V]`，`target` 是 `[B, T]`，取值是合法下标或 `ignore_index`；`z_coef >= 0`，否则抛 `ValueError`。所有 token 都被忽略时返回可以反传的 0。

### 输入输出示例

```text
logits = [0, 0], target = 0     -> ce = ln 2 ≈ 0.693，z_loss = (ln 2)^2 ≈ 0.480
logits 整体加 50                 -> ce 不变，z_loss 变大
target 全是 -100                 -> (0, 0, 0)，梯度为 0
```

### 解题思路与正确性

交叉熵里 $-\log p_y = \log Z - x_y$，logits 整体加常数时两项一起变，CE 不变；z-loss 直接约束 $\log Z$ 本身，所以会随平移变化。实现时 $\log Z$ 只用 `logsumexp` 算一次，CE 和 z-loss 共用。

先算出有效 token 的 mask 和分母，CE 和 z-loss 都用这一个分母，被忽略的 token 在两项里都不出现。

### 完整参考实现（Python 3）

```python
import math

import torch

Z_COEF = 1e-4


def ce_with_z_loss(logits, target, ignore_index=-100, z_coef=Z_COEF):
    """交叉熵 + PaLM z-loss，只在有效 token 上平均。

    logits: [B, T, V]；target: [B, T]，取值是合法词表下标或 ignore_index（负数）。
    返回 (total, ce, z_loss)，其中 z_loss 是未乘系数的 mean(logZ^2)。
    全部 token 被忽略时三项都是 0，且仍可反传。
    """
    if z_coef < 0:
        raise ValueError(f"z_coef must be non-negative, got {z_coef}")
    x = logits.float()
    log_z = torch.logsumexp(x, dim=-1)                      # [B, T]
    logp = x - log_z.unsqueeze(-1)                          # [B, T, V]
    safe_target = target.clamp(min=0)                       # ignore 位置先换成 0，gather 后再 mask 掉
    nll = -logp.gather(-1, safe_target.unsqueeze(-1)).squeeze(-1)
    mask = target != ignore_index
    denom = mask.sum().clamp_min(1)
    ce = nll[mask].sum() / denom
    z_loss = (log_z.square() * mask).sum() / denom
    return ce + z_coef * z_loss, ce, z_loss
```

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
logits = torch.zeros(1, 1, 2, requires_grad=True)
target = torch.zeros(1, 1, dtype=torch.long)

# logits 全 0、V = 2：CE = ln 2，z_loss = (ln 2)^2，total = CE + 1e-4 * z_loss
total, ce, reg = ce_with_z_loss(logits, target)
assert torch.allclose(ce, torch.tensor(math.log(2)))
assert torch.allclose(reg, torch.tensor(math.log(2) ** 2))
assert torch.allclose(total, ce + 1e-4 * reg)

# 全部 ignore：三项都是 0，且可以反传、梯度为 0
all_ignored = ce_with_z_loss(logits, torch.full_like(target, -100))
assert all(value == 0 for value in all_ignored)
assert torch.all(torch.autograd.grad(all_ignored[0], logits)[0] == 0)

# logits 整体平移：CE 不变，z_loss 变大
_, shifted_ce, shifted_reg = ce_with_z_loss(logits + 50, target)
assert torch.allclose(ce, shifted_ce)
assert shifted_reg > reg

# ignore 位置不进分子也不进分母：加一个被忽略的 token，结果不变
two_logits = torch.cat([logits.detach(), torch.full((1, 1, 2), 30.0)], dim=1)
two_target = torch.tensor([[0, -100]])
_, ce_two, reg_two = ce_with_z_loss(two_logits, two_target)
assert torch.allclose(ce_two, ce)
assert torch.allclose(reg_two, reg)

# 系数为负报错
expect_value_error(ce_with_z_loss, logits, target, z_coef=-1.0)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$、词表大小 $V$。时间和空间都是 $O(BTV)$，主要花在 `logsumexp` 和 `logp` 上；z-loss 本身只多 $O(BT)$。

- 追问「`ignore_index` 是正数怎么办」：这里用 `clamp(min=0)` 处理 ignore 位置，只对负数的 `ignore_index` 成立。如果允许任意值，要像 `coding-cross-entropy` 那样先筛出有效目标再 gather。

## 题怎么来的

PaLM 540B 的训练报告里写了这条辅助损失，系数是 $10^{-4}$。Google 研究岗和大模型训练的白板题会问：「CE 已经对平移不变了，为什么还要管 logits 的绝对大小？」Pathways 规模的背景见 `google-palm-pathways`。从公式上看，它就是约束 `coding-logsumexp` 的输出。OpenAI 的 debug 题不一定点名 z-loss，但 bf16 训练时不时出现 NaN，常常也是 logits 漂移这类问题。

## 约束配分函数，不改 softmax

对每个 token 的 logits $x\in\mathbb{R}^{V}$：

$$
z=\mathrm{logsumexp}(x)=\log\sum_i e^{x_i},\qquad
\mathcal{L}_z=\lambda z^2,\quad \lambda=10^{-4}.
$$

PaLM 把 $\mathcal{L}_z$ 加到 token 级交叉熵损失（CE）上。因为 softmax$(x)=$softmax$(x+c)$，而且 $x_y$ 和 $z$ 会一起加 $c$，所以 CE 也不变。也就是说，对 CE 来说 $x\leftarrow x+c$ 这个方向完全没有梯度，$z$ 可以一路漂到几百。bf16 在绝对值大的地方精度很粗，`exp` 和 GEMM 都更容易溢出成 inf，或者把相近的数舍入成同一个值。$z^2$ 的梯度把 $z$ 往 0 推，相当于希望 $\sum e^{x_i}\approx 1$，让 logits 落在合理的范围内。分类结果（argmax）仍然只由 logits 之间的相对差决定。

不要把 z-loss 写成 $\lambda\|x\|_2^2$。那会压缩 logits 之间的相对差，损害 CE。z-loss 正则的是标量 $z$，不是整行 logits。

pad 位置必须和 CE 共用同一个 mask：如果对 ignore 位置也加 $z^2$，padding 多的 batch 辅助损失就会变大。分母是有效 token 数，不是 $B\cdot T$。

## 系数和什么时候需要

$\lambda=10^{-4}$ 是 PaLM 公开的值。太大会过度强迫 $z\approx 0$，和 CE 抢优化方向；太小又压不住漂移。小模型、fp32 训练时往往感觉不到它的作用；词表大到 $10^5$ 量级、用 bf16 / fp8 训练时，这一项才开始有明显价值。

它不是 label smoothing，也不是 entropy bonus：它不鼓励输出分布变均匀，只防止 log-partition 出现极端值。它和 MoE 的 load-balancing aux loss 也不是一类东西，不要往路由损失上套。

## 追问

- **为什么不直接 clip logits？** clip 在边界外梯度为 0，还会损伤 logits 之间的相对差。$z^2$ 是平滑的，而且只约束整体平移这一个自由度。
- **$z$ 能不能直接用 `log(sum(exp))` 算？** 不行。$x$ 很大时 `exp` 溢出成 inf，辅助损失本身就成了 NaN。必须用 log-sum-exp 技巧，见 `coding-logsumexp`。
- **推理时还加吗？** 不加，它只存在于训练图里。推理时的 softmax 不需要 $z\approx 0$。
- **和 weight decay 有什么关系？** weight decay 管参数的范数，z-loss 管 logits 的绝对尺度。两者可以同时使用。

## 相关题

- [[coding-logsumexp]]：z-loss 里的 $\log Z$ 必须用减 max 的 logsumexp 算，那张讲这个技巧和整行 $-\infty$ 的边界。
- [[coding-cross-entropy]]：z-loss 加在这个 CE 上，那张讲 CE 本身的 log 域写法和 ignore 下标的分母。

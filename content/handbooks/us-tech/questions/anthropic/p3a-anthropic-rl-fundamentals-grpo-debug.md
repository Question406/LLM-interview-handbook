---
id: p3a-anthropic-rl-fundamentals-grpo-debug
section: anthropic
order: 617
level: S
title: "Anthropic：GRPO 调试与重要性采样比追问"
quick: "调 GRPO 时按数据流逐层检查：采样前要 softmax，组内优势在得分全相同时设为 0 以免除零，重要性采样比是 logprob 差取 exp 且 old 值固定，损失只对 response token 求平均。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · rl-fundamentals-grpo-debug"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug
    type: secondary
---

## 题目

给一份植入了若干 bug 的 GRPO 训练脚本，找出并修复这些错误；之后面试官会追问 clip 的作用、组内优势归一化，以及 on-policy 和 off-policy 的区别（重要性采样比为什么会偏离 1）。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。具体植入了哪几行 bug 以现场脚本为准，摘要不足以确认第三个 bug。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

调试时按数据流逐层检查，每层都能用小例子单独验证：

- 采样：从 logits 采样前要先做 softmax，得到非负且和为 1 的概率，不能把 logits 直接当权重；
- 组内优势：同一个 prompt 的 G 个回答，减去组均值再除以组内标准差。如果一组得分全相同，标准差是 0，直接除会得到 NaN；这组本来就没有学习信号，优势应该全设成 0；
- 重要性采样比：$r = \exp(\log \pi_\text{new} - \log \pi_\text{old})$，是 logprob 之差再取 exp，漏掉 exp 是常见 bug。`old` 的 logprob 要在采样时固定下来，不能参与求导；
- response mask：只让回答部分的 token 进入损失，prompt 和 padding 都要 mask 掉，平均时分母是有效 token 数。

这份练习设定的三个错误是「logits 直接采样」「零方差除零」「漏 exp」。其中只有前两类在已有的面经转述里有具体线索，不能把三处都当成已核实的原题内容。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `advantages(rewards)`：`rewards` 形状 $(P, G)$，P 个 prompt、每个 G 个回答。每组用总体标准差归一化；标准差小于 $10^{-8}$ 的组优势全为 0。
- `loss_grad(new_logp, old_logp, adv, mask, eps=0.2) -> (loss, grad)`：`new_logp`、`old_logp` 形状 $(P \cdot G, T)$，是被采样 token 的 log 概率；`adv` 形状 $(P \cdot G,)$；`mask` 与 logprob 同形状的 bool。返回 PPO 式 clipped surrogate 取负后在有效 token 上的均值，以及它对 `new_logp` 的梯度。
- `old_logp` 和 `adv` 视为常量；不加参考模型 KL；`mask` 全为 False 时返回损失 0 和全零梯度。形状不符或 `eps` 不在 $(0, 1)$ 内抛 `ValueError`。

### 输入输出示例

```text
advantages([[1, 1], [0, 2]])   -> [[0, 0], [-1, 1]]
loss_grad(x, x, adv, mask)     # new == old，所有 ratio 都是 1，损失等于负的有效 token 平均优势
```

### 解题思路与正确性

训练时是最小化损失，所以要对 surrogate $\min(r A, \operatorname{clip}(r, 1-\epsilon, 1+\epsilon) A)$ 取负。

梯度要分情况看。优势为正、$r$ 已超过 $1+\epsilon$ 时，取的是 clip 分支，是常数，梯度为 0；优势为负、$r$ 已低于 $1-\epsilon$ 时同理。其余情况取的是未截断的 $rA$，而 $\partial r / \partial \log\pi_\text{new} = r$，所以每个 token 的梯度是 $-A \cdot r / n$（n 为有效 token 数）。测试用中心差分逐元素核对了这个解析梯度。

第一个 epoch 里 new 和 old 是同一个策略，ratio 恒等于 1；同一批数据训练到第二个 epoch 时策略已经变了，ratio 才开始偏离 1，这就是 off-policy 的部分，也是 clip 起作用的地方。clip 只限制单个 token 的更新幅度，并不给 KL 散度设硬上限。

### 完整参考实现（Python 3）

```python
import numpy as np

STD_FLOOR = 1e-8


def advantages(rewards):
    """组内归一化优势。rewards: (P, G)，每行是同一个 prompt 的 G 个回答的得分。

    每组减去组均值、除以组内总体标准差；一组得分全相同（std < 1e-8）时优势全为 0，不除零。
    """
    rewards = np.asarray(rewards, dtype=float)
    if rewards.ndim != 2 or rewards.shape[1] == 0:
        raise ValueError(f"rewards must have shape (P, G) with G >= 1, got {rewards.shape}")
    centered = rewards - rewards.mean(axis=1, keepdims=True)
    std = rewards.std(axis=1, keepdims=True)
    return np.divide(centered, std, out=np.zeros_like(centered), where=std >= STD_FLOOR)


def _check_loss_inputs(new_logp, old_logp, adv, mask, eps):
    if new_logp.ndim != 2:
        raise ValueError(f"logprobs must be 2-D (B, T), got {new_logp.shape}")
    if old_logp.shape != new_logp.shape or mask.shape != new_logp.shape:
        raise ValueError("new_logp, old_logp and mask must have the same shape")
    if adv.shape != (len(new_logp),):
        raise ValueError(f"adv must have shape ({len(new_logp)},), got {adv.shape}")
    if not 0 < eps < 1:
        raise ValueError(f"eps must be in (0, 1), got {eps}")


def loss_grad(new_logp, old_logp, adv, mask, eps=0.2):
    """PPO 式 clipped surrogate 的损失（取负，用于最小化）和它对 new_logp 的梯度。

    new_logp, old_logp, mask: (B, T)，B = P * G，是被采样 token 的 log 概率；adv: (B,)。
    old_logp 和 adv 视为常量；损失对 mask 内的有效 token 求平均；不含参考模型 KL。
    """
    new_logp = np.asarray(new_logp, dtype=float)
    old_logp = np.asarray(old_logp, dtype=float)
    adv = np.asarray(adv, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    _check_loss_inputs(new_logp, old_logp, adv, mask, eps)

    num_tokens = int(mask.sum())
    if num_tokens == 0:
        return 0.0, np.zeros_like(new_logp)

    adv = adv[:, None]  # (B, 1)，广播到每个 token
    ratio = np.exp(new_logp - old_logp)  # 重要性采样比 π_new / π_old
    unclipped = ratio * adv
    clipped = np.clip(ratio, 1 - eps, 1 + eps) * adv
    loss = float((-np.minimum(unclipped, clipped) * mask).sum() / num_tokens)

    # 只有当 clip 阻止策略继续往「有利方向」移动时梯度才为 0：
    # 正优势且 ratio 已超过 1+eps，或负优势且 ratio 已低于 1-eps。
    flat = ((adv > 0) & (ratio > 1 + eps)) | ((adv < 0) & (ratio < 1 - eps))
    grad = -adv * ratio * ~flat * mask / num_tokens  # d ratio / d new_logp = ratio
    return loss, grad
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 第一组得分相同，优势全 0；第二组标准化为 -1 和 1
assert np.allclose(advantages([[1, 1], [0, 2]]), [[0, 0], [-1, 1]])

# 解析梯度和中心差分对照；第二行的两个 token 分别落在 clip 平坦区和非平坦区
new_logp = np.array([[0.05, -0.1], [0.4, -0.5]])
old_logp = np.zeros_like(new_logp)
adv = np.array([1.0, -1.0])
mask = np.array([[1, 0], [1, 1]], dtype=bool)
_, grad = loss_grad(new_logp, old_logp, adv, mask)
step = 1e-6
for i in range(2):
    for j in range(2):
        plus = new_logp.copy()
        minus = new_logp.copy()
        plus[i, j] += step
        minus[i, j] -= step
        loss_plus = loss_grad(plus, old_logp, adv, mask)[0]
        loss_minus = loss_grad(minus, old_logp, adv, mask)[0]
        numeric = (loss_plus - loss_minus) / (2 * step)
        assert np.isclose(numeric, grad[i, j], atol=1e-7)

# new == old 时 ratio 为 1，损失等于负的平均优势
loss, _ = loss_grad(old_logp, old_logp, adv, mask)
assert np.isclose(loss, -(1 + (-1) + (-1)) / 3)

# 全部 mask 掉时损失为 0
assert loss_grad(new_logp, old_logp, adv, np.zeros_like(mask))[0] == 0

# 形状和 eps 校验
expect_value_error(advantages, [1, 2])
expect_value_error(loss_grad, new_logp, old_logp, np.array([1.0]), mask)
expect_value_error(loss_grad, new_logp, old_logp, adv, mask, 1.5)
```

### 复杂度与追问

设 P 个 prompt、每组 G 个回答、序列长 T。`advantages` 是 O(PG)，`loss_grad` 的时间和空间都是 O(PGT)。

- 采样那一步：要先对 logits 做 softmax（可以先除以 temperature），再按概率采样；把 logits 直接当权重会遇到负数，分布也不对。
- mask 的范围：只覆盖 response token。把 prompt token 算进去会让模型在它没生成的 token 上受到梯度。
- 加 KL 惩罚：要先说明 reference 策略是谁（通常是 SFT 模型）、KL 用哪种估计、按 token 还是按序列平均。old 策略的 ratio 是为了做重要性采样修正，reference KL 是为了防止策略漂离初始模型，两者不能合成一项。

## 相关题

- [[anthropic-grpo-debug]]：手册已有的同类题，两边题面契约不完全一样，练习时分别对照，不要混用；那张多了真题记录和修完后的追问。
- [[sys-rollout-logprob]]：展开「重要性采样比为什么会偏离 1」，按 micro batch、温度、权重版本逐项排查。
- [[sys-adv-bcast]]：这里说 mask 只覆盖 response token，那张讲序列级优势铺到 token 时 prompt、pad、工具返回为什么必须是 0。
- [[sys-kl-place]]：这里提到 ref KL 和 old ratio 不能合成一项，那张讲 KL 写进奖励还是写进 loss。

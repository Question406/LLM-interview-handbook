---
id: p3a-anthropic-rl-fundamentals-grpo-debug
section: anthropic
order: 617
level: S
title: Anthropic：GRPO 调试与 importance sampling 比追问
quick: >-
  我会按 sampling、组内优势、importance sampling 比和 response mask 的顺序排查 GRPO。得分全同的组优势设为
  0，ratio 用固定 old logprob 与 new 的差取 exp，损失只平均有效回答 token；这些都可以用小输入单独核对。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Anthropic · rl-fundamentals-grpo-debug
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug
    type: secondary
---

## 题目描述

实现组内奖励 normalization 和带裁剪的策略损失，用于检查一个小型 GRPO 训练步骤。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`advantages(rewards)` 接收 NumPy 浮点数组 `[P,G]`，每行是一道 prompt 的 G 个奖励，返回同形数组：每组减去本组均值，再除以该行组内总体标准差（ddof=0）；标准差小于 `1e-8` 的组全部返回 0。

`loss_grad(new, old, adv, mask, eps=0.2)` 返回 `(loss, grad)`。`new`、`old` 是 `[P*G,T]` 的 sampling token log probability，`adv` 是 `[P*G]`，`mask` 是同形布尔数组，True 表示计入损失；`0 < eps < 1`。令 `r=exp(new-old)`，每个有效 token 的损失定义为 `-min(r*A, clip(r,1-eps,1+eps)*A)`，其中 A 是该序列的优势。`loss` 是有效 token 的均值，`grad` 是对 new 的导数，形状与 new 一致。old、adv 是常量；不加入额外 reference model KL 项。全部 token 被屏蔽时返回 0 和全零梯度。

### 示例

```text
advantages([[1,1],[0,2]]) = [[0,0],[-1,1]]
new = old = [[0],[0]], adv = [1,-1], mask = [[True],[True]]
loss = 0, grad = [[-0.5],[0.5]]
```

## 解题思路与参考答案

## 题目

给一份植入了若干 bug 的 GRPO 训练脚本，找出并修复这些错误；之后面试官会追问 clip 的作用、组内优势 normalization，以及 on-policy 和 off-policy 的区别（importance sampling 比为什么会偏离 1）。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站收录了这类面经，不代表公司确认。具体植入了哪几行 bug 以现场脚本为准，摘要不足以确认第三个 bug。下面的接口、约束和测试是手册补的练习约定。

我会沿数据流排查，每层用一个小输入验证，再看总损失。比如同一 prompt 的 G 个回答得分全一样，减均值后全是 0，标准差也是 0；直接相除就变成 NaN，这组没有相对学习信号，应把优势设为 0。

sampling 前先把 logits 经 softmax 变成非负、和为 1 的概率。组内优势按同一个 prompt 分组，减均值、除组内标准差，并处理上面这个 zero-variance edge case。

再看 importance sampling 比：$r = \exp(\log \pi_\text{new} - \log \pi_\text{old})$。logprob 之差还要取 exp，`old` 则在 sampling 时固定，不参与求导。损失的 response mask 只放回答 token，排除 prompt 和 padding，分母也用有效 token 数。

下面练习设置了 logits 直接 sampling、零方差除零和漏 exp 三类错误；已有面经转述只有前两类的具体线索，第三类是练习约定，现场仍以给出的脚本为准。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `advantages(rewards)`：`rewards` 形状 $(P, G)$，P 个 prompt、每个 G 个回答。每组用总体标准差 normalization；标准差小于 $10^{-8}$ 的组优势全为 0。
- `loss_grad(new_logp, old_logp, adv, mask, eps=0.2) -> (loss, grad)`：`new_logp`、`old_logp` 形状 $(P \cdot G, T)$，是被 sampling token 的 log 概率；`adv` 形状 $(P \cdot G,)$；`mask` 与 logprob 同形状的 bool。返回 PPO 式 clipped surrogate 取负后在有效 token 上的均值，以及它对 `new_logp` 的梯度。
- `old_logp` 和 `adv` 视为常量；不加 reference model KL；`mask` 全为 False 时返回损失 0 和全零梯度。形状不符或 `eps` 不在 $(0, 1)$ 内抛 `ValueError`。

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
    """组内 normalization 优势。rewards: (P, G)，每行是同一个 prompt 的 G 个回答的得分。

    每组减去组均值、除以组内总体标准差；一组得分全相同（std < 1e-8）时优势全为 0，不除零。
    """
    rewards = np.asarray(rewards, dtype=float)
    if rewards.ndim != 2 or rewards.shape[1] == 0:
        raise ValueError(
            f"rewards must have shape (P, G) with G >= 1, got {rewards.shape}"
        )
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

    new_logp, old_logp, mask: (B, T)，B = P * G，是被 sampling token 的 log 概率；adv: (B,)。
    old_logp 和 adv 视为常量；损失对 mask 内的有效 token 求平均；不含 reference model KL。
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
    ratio = np.exp(new_logp - old_logp)  # importance sampling 比 π_new / π_old
    unclipped = ratio * adv
    clipped = np.clip(ratio, 1 - eps, 1 + eps) * adv
    loss = float((-np.minimum(unclipped, clipped) * mask).sum() / num_tokens)

    # 只有当 clip 阻止策略继续往「有利方向」移动时梯度才为 0：
    # 正优势且 ratio 已超过 1+eps，或负优势且 ratio 已低于 1-eps。
    flat = ((adv > 0) & (ratio > 1 + eps)) | ((adv < 0) & (ratio < 1 - eps))
    grad = -adv * ratio * ~flat * mask / num_tokens  # d ratio / d new_logp = ratio
    return loss, grad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(advantages([[1, 1], [0, 2]]), [[0, 0], [-1, 1]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 第一组得分相同，优势全 0；第二组 standardization 为 -1 和 1
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

- sampling 那一步：要先对 logits 做 softmax（可以先除以 temperature），再按概率 sampling；把 logits 直接当权重会遇到负数，分布也不对。
- mask 的范围：只覆盖 response token。把 prompt token 算进去会让模型在它没生成的 token 上受到梯度。
- 加 KL 惩罚：要先说明 reference 策略是谁（通常是 SFT 模型）、KL 用哪种估计、按 token 还是按序列平均。old 策略的 ratio 是为了做 importance sampling 修正，reference KL 是为了防止策略漂离初始模型，两者不能合成一项。

## 相关题

- [[anthropic-grpo-debug]]：手册已有的同类题，两边题面契约不完全一样，练习时分别对照，不要混用；那张多了真题记录和修完后的追问。
- [[sys-rollout-logprob]]：展开「importance sampling 比为什么会偏离 1」，按 micro batch、温度、权重版本逐项排查。
- [[sys-adv-bcast]]：这里说 mask 只覆盖 response token，那张讲序列级优势铺到 token 时 prompt、pad、工具返回为什么必须是 0。
- [[sys-kl-place]]：这里提到 ref KL 和 old ratio 不能合成一项，那张讲 KL 写进奖励还是写进 loss。

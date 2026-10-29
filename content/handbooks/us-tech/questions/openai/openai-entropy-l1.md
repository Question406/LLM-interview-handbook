---
id: openai-entropy-l1
section: openai
order: 3
level: A
title: OpenAI ML Coding：用 linear + softmax 算 entropy；换成 L1 怎么做？
quick: >-
  我会先用逐行减 max 的稳定 softmax 得到概率，再算熵；L1 仍然可以搭配同一个 softmax。对 logits 求梯度时，把 L1 的次梯度乘
  softmax Jacobian，并处理相等位置与 batch 平均。
tags:
  - 完整编程练习
  - OpenAI
  - Entropy
  - Softmax
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: OpenAI ML Coding 面经
    url: 'https://www.1point3acres.com/bbs/thread-1177444-1-1.html'
    type: candidate-first-hand
---

## 题目描述

实现一个线性分类头的类别概率和熵，以及概率 L1 损失对分类 logits 的梯度。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `linear_entropy(x, w, b) -> (p, H)`：`x` 是 `[B, D]`，`w` 是 `[D, C]`，`b` 是 `[C]`，`C >= 1`。计算 $z = xw + b$、$p=\mathrm{softmax}(z)$，返回概率 `p [B, C]` 和每个样本的熵 `H [B]`（自然对数，单位 nat）。
- `l1_loss_grad_logits(p, q) -> (loss, grad)`：`q` 和 `p` 同形，每一行都是合法的概率分布。损失是 batch 上平均的 $\sum_i \lvert p_i-q_i\rvert$，返回损失和它对 logits $z$ 的梯度 `[B, C]`。在 $p_i=q_i$ 处 $\lvert\cdot\rvert$ 不可导，取次梯度 0。
- 所有输入形状匹配，线性输出有限，`p`、`q` 各行均为合法概率分布。熵中 `0 * log(0)` 按 0 计。


### 输入输出示例

```text
x=[[0]], w=[[0,0]], b=[0,0]
linear_entropy(x,w,b) -> (p=[[0.5,0.5]], H=[ln(2)])
l1_loss_grad_logits([[0.5,0.5]], [[1,0]])
-> (loss=1, grad=[[-0.5,0.5]])
```

## 解题思路与参考答案

我会保留 linear + softmax 作为概率输出，熵和 L1 分别按各自定义算。比如二分类 logits 都是 0，概率就是各 0.5，熵为 ln 2；目标换成 [1, 0]，只需要改损失为 L1，不必换输出层。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy（回帖说原题用 numpy）。

### 题面、接口与约束

- `linear_entropy(x, w, b) -> (p, H)`：`x` 是 `[B, D]`，`w` 是 `[D, C]`，`b` 是 `[C]`，`C >= 1`。计算 $z = xw + b$、$p=\mathrm{softmax}(z)$，返回概率 `p [B, C]` 和每个样本的熵 `H [B]`（自然对数，单位 nat）。
- `l1_loss_grad_logits(p, q) -> (loss, grad)`：`q` 和 `p` 同形，每一行都是合法的概率分布。损失是 batch 上平均的 $\sum_i \lvert p_i-q_i\rvert$，返回损失和它对 logits $z$ 的梯度 `[B, C]`。在 $p_i=q_i$ 处 $\lvert\cdot\rvert$ 不可导，取次梯度 0。
- 形状不对、logits 出现非有限值、`p`/`q` 不是合法分布时抛 `ValueError`。线性层本身溢出成 inf 时直接报错，不在后面补救。
- L1 只是损失函数的选择，输出照样可以用 softmax，不需要换成 ReLU 再 normalization。

### 输入输出示例

```text
二分类，logits = [0, 0]       -> p = [0.5, 0.5]，H = ln 2 ≈ 0.693
目标 q = [1, 0]               -> L1 = |0.5-1| + |0.5-0| = 1
                               -> 对 logits 的梯度 = [-0.5, 0.5]
```

### 解题思路与正确性

计算熵时先逐行减最大值，用 log-sum-exp 得到 $\log p$，再求 $H=-\sum_i p_i\log p_i$。这样不必对已下溢为 0 的概率取 $\log 0$；即使 $p_i$ 变成 0，保存的 $\log p_i$ 仍为有限负值，这项乘积就是 0。

L1 求导先从概率开始，得到 $g=\mathrm{sign}(p-q)$，相等处选 0 次梯度。再乘 softmax Jacobian $\partial p/\partial z=\mathrm{diag}(p)-pp^\top$，把梯度传回 logits：

$$
\frac{\partial L}{\partial z} = p\odot\bigl(g-\textstyle\sum_j p_j g_j\bigr),
$$

最后因为损失是 batch 平均，再除以 $B$。

用 L1 并不要求改变输出的概率参数化。是否需要输出精确为 0 的概率，是另一项建模需求，见下文。

### 完整参考实现（Python 3）

```python
import numpy as np


def linear_entropy(x, w, b):
    """z = x @ w + b，返回 softmax 概率 p [B, C] 和逐样本熵 H [B]（nat）。"""
    x, w, b = (np.asarray(array, dtype=float) for array in (x, w, b))
    if x.ndim != 2 or w.ndim != 2 or b.ndim != 1:
        raise ValueError(
            f"expected x [B, D], w [D, C], b [C], got {x.shape}, {w.shape}, {b.shape}"
        )
    if len(x) == 0 or len(b) == 0 or x.shape[1] != w.shape[0] or w.shape[1] != len(b):
        raise ValueError(f"incompatible shapes x {x.shape}, w {w.shape}, b {b.shape}")
    z = x @ w + b  # [B, C]
    if not np.isfinite(z).all():
        raise ValueError("linear layer produced non-finite logits")
    shifted = z - z.max(axis=-1, keepdims=True)  # 减每行最大值，exp 不溢出
    log_p = shifted - np.log(np.exp(shifted).sum(axis=-1, keepdims=True))
    p = np.exp(log_p)
    return p, -(p * log_p).sum(axis=-1)


def l1_loss_grad_logits(p, q):
    """batch 平均的 sum|p - q|，以及它对 softmax logits 的梯度。p == q 处取次梯度 0。"""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.ndim != 2 or p.shape != q.shape or len(p) == 0 or p.shape[1] == 0:
        raise ValueError(
            f"p and q must be the same non-empty [B, C] shape, got {p.shape}, {q.shape}"
        )
    for name, dist in (("p", p), ("q", q)):
        if (
            not np.isfinite(dist).all()
            or (dist < 0).any()
            or not np.allclose(dist.sum(-1), 1)
        ):
            raise ValueError(f"every row of {name} must be a probability distribution")
    sign = np.sign(p - q)  # dL/dp，相等处为 0
    # softmax Jacobian 乘 sign：p * (g - <p, g>)，再除以 batch 大小
    grad = p * (sign - (p * sign).sum(axis=-1, keepdims=True)) / len(p)
    loss = np.abs(p - q).sum(axis=-1).mean()
    return loss, grad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(entropy, np.log(2))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 题面示例：二分类均匀分布，熵为 ln 2；L1 与梯度
p, entropy = linear_entropy([[0.0]], [[0.0, 0.0]], [0.0, 0.0])
assert np.allclose(entropy, np.log(2))
loss, grad = l1_loss_grad_logits(p, [[1.0, 0.0]])
assert np.isclose(loss, 1)
assert np.allclose(grad, [[-0.5, 0.5]])

# 极端 logits：接近 one-hot，熵有限且约为 0
p, entropy = linear_entropy([[1.0]], [[1000.0, -1000.0]], [0.0, 0.0])
assert np.isfinite(entropy).all()
assert np.allclose(entropy, 0)

# p == q：损失为 0，次梯度取 0
assert l1_loss_grad_logits(p, p)[0] == 0
assert np.all(l1_loss_grad_logits(p, p)[1] == 0)

# 均匀分布熵最大，等于 ln C
_, entropy = linear_entropy(np.zeros((2, 3)), np.zeros((3, 5)), np.zeros(5))
assert np.allclose(entropy, np.log(5))

# 解析梯度与有限差分一致
z = np.array([[0.3, -0.7, 1.1], [0.1, 0.9, -0.5]])
q = np.array([[0.2, 0.3, 0.5], [0.5, 0.2, 0.3]])


def objective(logits):
    probs, _ = linear_entropy(logits, np.eye(3), np.zeros(3))
    return l1_loss_grad_logits(probs, q)[0]


p, _ = linear_entropy(z, np.eye(3), np.zeros(3))
_, analytical = l1_loss_grad_logits(p, q)
step = 1e-6
for index in np.ndindex(z.shape):
    plus = z.copy()
    minus = z.copy()
    plus[index] += step
    minus[index] -= step
    numerical = (objective(plus) - objective(minus)) / (2 * step)
    assert np.isclose(analytical[index], numerical, atol=1e-7)

# 非法输入：形状不匹配、线性层溢出、q 不是分布
expect_value_error(lambda: linear_entropy([[1.0, 2.0]], [[1.0]], [0.0]))
expect_value_error(lambda: linear_entropy([[1e308]], [[1e308]], [0.0]))
expect_value_error(lambda: l1_loss_grad_logits([[0.5, 0.5]], [[0.7, 0.7]]))
expect_value_error(lambda: l1_loss_grad_logits([[0.5, 0.5]], [[1.0, 0.0, 0.0]]))
```

### 复杂度与追问

设 batch 为 B、输入维度 D、类别数 C。线性层 O(B·D·C)，熵和 L1 梯度 O(B·C)，中间空间 O(B·C)。

- 追问「熵的单位」：这里用自然对数，单位是 nat；要 bit 就再除以 $\ln 2$。
- 追问「线性层已经溢出了怎么办」：减 max 只能防止 `exp` 溢出，修不了已经变成 inf 的 logits，所以实现在这一步直接报错。

## 真题记录

- 公司：OpenAI（Research org）
- 岗位：候选人写的是 Research 侧的 ML Coding，共两轮
- 来源：一亩三分地 2026-05 的帖子，细节对游客隐藏；可见部分明确写了「Entropy 计算」，以及 follow-up「如果换成 L1 distance，怎么用 neural network 实现」
- 实现：回复里说用 numpy，不要求 PyTorch

公开可见的题面就这两句。下面按信息论和概率单纯形的几何，把能公开讲的部分写完整，不编造帖子里被隐藏的数据构造。

## Entropy：先得到合法分布，再算 $H$

输入 $x\in\mathbb{R}^d$，线性层 $z=Wx+b$（练习里用行向量写成 $z=xw+b$），

$$
p_i=\frac{e^{z_i-\max_j z_j}}{\sum_k e^{z_k-\max_j z_j}},\qquad
H(p)=-\sum_i p_i\log p_i.
$$

减 max 是必须的，直接 `exp(z)` 会溢出。$p_i=0$ 的项按 $p\log p\to 0$ 的约定处理。如果是先算 $p$ 再取 log，就要对 $p_i<\varepsilon$ 的项跳过，或者写 `p * log(p + eps)` 并在注释里说明这是近似；练习里从 log-sum-exp 直接得到 $\log p$，就不会遇到 $\log 0$。

熵的单位取决于 log 的底：$\log_2$ 是 bit，$\ln$ 是 nat，面试里说一次就行。$n$ 类均匀分布的熵最大，等于 $\log n$；one-hot 的熵是 0。这两个性质正好拿来写单元测试。

不要把 entropy 写成 cross entropy loss（CE）。CE 是 $H(p,q)=-\sum p\log q$，当 $p$ 是经验 one-hot 分布时，CE 就变成 NLL，和分布自身的熵 $H(p)$ 不是同一个量。

## L1：输出参数化与训练损失分别选择

概率输出与训练损失可以分别选择。softmax(z) 后接 L1 距离或 total variation 是合法组合，上面的实现用有限差分检查了梯度。若业务还要求精确为 0 的概率，再考虑 ReLU 后 normalization 或 sparsemax，它们的 edge-case behavior 与 softmax 不同；L1 本身没有要求稀疏输出。

## 追问

**softmax 能直接配 L1 吗？**
可以。用 softmax 的 Jacobian 把 L1 的次梯度传回 logits 即可；如果业务要求输出精确为 0 的概率，再讨论稀疏的参数化。
**和 MAE 回归有什么区别？**
MAE 是对 point estimate 算 $\ell_1$ 误差，不是概率单纯形上两个分布之间的距离。题目给的是类别概率，就不要答成回归。
**numpy 怎么写 softmax？**
`z -= z.max(axis=-1, keepdims=True)`，再 `exp`、按行求和 normalization。不要对整个 batch 减同一个标量，否则某些行仍可能溢出或全部下溢成 0。

## 相关题

- [[coding-softmax-stable]]：这题第一步用到的稳定 softmax 单独成题，讲为什么逐行减 max、轴怎么选。
- [[coding-cross-entropy]]：容易和这里的熵混淆：CE 是目标分布对模型分布的 cross entropy，用 logsumexp 直接算，不先求概率。
- [[coding-token-logprob]]：RL 里从同一份 logits 取 token logprob 时顺便算熵，要注意 vocabulary 维的显存切块。

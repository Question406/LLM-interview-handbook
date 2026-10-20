---
id: coding-dropout
section: coding
order: 9
level: S
title: 白板：dropout mask 训练/推理缩放（inverted dropout）
quick: >-
  训练时每个元素以概率 $p$ 置零，留下的乘 $1/(1-p)$，期望不变；推理原样返回，不再乘 $1-p$。PyTorch 默认就是这种 inverted dropout。
tags:
  - 完整编程练习
  - Coding
  - Dropout
  - Regularization
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Dropout — A Simple Way to Prevent Neural Networks from Overfitting
    url: https://jmlr.org/papers/v15/srivastava14a.html
    type: primary
  - title: torch.nn.functional.dropout
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.dropout.html
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `dropout(x, p, training, generator=None) -> Tensor`：inverted dropout。训练时每个元素以概率 $1-p$ 保留，保留下来的除以 $1-p$；推理（`training=False`）或 `p == 0` 时原样返回 `x`。
- 传入同样种子的 `torch.Generator`，结果可复现。
- `attn_with_dropout(scores, p, training, generator=None)`：对已经加过 mask 的注意力 logits `[B, H, T, S]` 做 softmax，再对权重做 dropout。
- 要求 `0 <= p < 1` 且有限；否则不管训练还是推理都抛 `ValueError`。

### 输入输出示例

```text
x = ones(N), p = 0.5, training=True   -> 每个元素是 0 或 2，均值约为 1
x = ones(N), p = 0.5, training=False  -> 原样返回，全是 1
dropout(x, 1.0, training=False)       -> ValueError
```

### 解题思路与正确性

保留概率是 $1-p$，保留的元素除以 $1-p$，所以每个元素的期望是 $(1-p)\cdot x/(1-p) = x$，和推理时的原样输出一致。

attention 的 dropout 作用在 softmax 之后的权重上。被丢掉的权重直接变成 0，剩下的放大，所以 dropout 之后每一行**不再**和为 1，这是正常的：期望意义上每行仍然和为 1。

`p` 的检查放在最前面，推理时传了非法的 `p` 也会报错，配置错误不会等到训练时才暴露。

### 完整参考实现（Python 3）

```python
import math

import torch


def dropout(x, p, training, generator=None):
    """Inverted dropout：训练时以 1-p 保留并除以 1-p，推理原样返回。要求 0 <= p < 1。"""
    if not math.isfinite(p) or p < 0.0 or p >= 1.0:
        raise ValueError(f"p must be in [0, 1), got {p}")
    if not training or p == 0.0:
        return x
    keep = 1.0 - p
    mask = torch.empty_like(x).bernoulli_(keep, generator=generator)
    return x * mask / keep


def attn_with_dropout(scores, p, training, generator=None):
    """scores: [B, H, T, S]，已用 -inf 加过 mask。dropout 打在 softmax 之后的权重上。"""
    weights = torch.softmax(scores, dim=-1)
    return dropout(weights, p, training, generator)
```

### 可执行测试

```python
torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


x = torch.ones(100000)

# 同一种子结果可复现，期望约等于 1
first = dropout(x, 0.3, True, torch.Generator().manual_seed(8))
second = dropout(x, 0.3, True, torch.Generator().manual_seed(8))
assert torch.equal(first, second)
assert abs(first.mean().item() - 1) < 0.015

# p = 0.5 时训练输出只有 0 和 2
halves = dropout(x, 0.5, True, torch.Generator().manual_seed(0))
assert set(halves.unique().tolist()) == {0.0, 2.0}

# 推理或 p = 0：原样返回
assert torch.equal(dropout(x, 0.3, False), x)
assert torch.equal(dropout(x, 0.0, True), x)

# 非法 p：推理时也报错
expect_value_error(lambda: dropout(x, 1.0, False))
expect_value_error(lambda: dropout(x, 1.0, True))
expect_value_error(lambda: dropout(x, -0.1, True))
expect_value_error(lambda: dropout(x, float("nan"), False))

# attention dropout：推理时每行和为 1；训练时非零权重被放大 1/(1-p)，行和不再固定为 1
scores = torch.randn(2, 3, 4, 5, generator=torch.Generator().manual_seed(1))
scores[..., -1] = float("-inf")
eval_weights = attn_with_dropout(scores, 0.5, False)
assert torch.allclose(eval_weights.sum(-1), torch.ones(2, 3, 4))
assert torch.all(eval_weights[..., -1] == 0)
train_weights = attn_with_dropout(scores, 0.5, True, torch.Generator().manual_seed(2))
kept = train_weights != 0
assert torch.allclose(train_weights[kept], 2 * eval_weights[kept])
```

### 复杂度与追问

设 `x` 的元素数为 N。时间 O(N)，额外空间是一份同形状的 mask，O(N)。

- 追问「省掉 mask 的显存」：反向需要同一份 mask。可以只存随机种子和 offset，反向时重新生成 mask（FlashAttention 的 attention dropout 就是这样做的），用一点计算换 O(N) 显存。

## 题怎么来的

Srivastava et al. 2014 提出的 dropout，是面试里最容易把缩放写反的一层。OpenAI 的 Transformer debug 题会故意把 `train()` / `eval()` 混用，这时即使把 mask 改对了，输出也对不上。Apple 手写 MHA 之后会追问：attention dropout 在推理时要不要保留。PyTorch 默认用 inverted dropout，缩放发生在训练阶段。白板上把期望推一遍，比背 `p=0.1` 有用。

## 训练乘 $1/(1-p)$，推理恒等

输入 $x$ 的形状是 `[B, T, D]`，或者注意力权重 `[B, H, T, S]`。训练时：

$$
m_i\sim\mathrm{Bernoulli}(1-p),\qquad
y=\frac{m}{1-p}\odot x.
$$

因为 $\mathbb{E}[y\mid x]=x$，推理时直接输出 $y=x$，不必再乘 $1-p$，这就是 inverted dropout。原论文的写法是训练时只乘 mask、推理时乘 $1-p$；这要求推理图和训练图不一样，框架一般不采用。PyTorch 的 `F.dropout` 走 inverted 写法，`training=False` 时原样返回。

$p=0$ 等于关掉 dropout。$p=1$ 时训练输出全是 0，$1/(1-p)$ 也没有定义，实现上要么拒绝，要么当成「全部丢弃」处理；上面的练习选择拒绝。mask 和 $x$ 的形状相同、逐元素采样。不要只沿 batch 维采样，否则同一条序列的所有激活会被一起丢掉。

注意力 dropout 打在 softmax 之后的权重上，而不是 logits 上。打在 logits 上相当于随机把某些 key 设成 $-\infty$，softmax 会重新归一化，语义就变了。残差分支上的 dropout 和 attention dropout 用的是两份独立的 mask。

## 和 debug / 端侧的关系

做评测、对齐 greedy 输出、对比有无 KV cache 时，必须先 `eval()`：训练态的 dropout 会让「有 cache」和「无 cache」两条路径的输出对不上。OpenAI 那一轮要先固定住观测条件，再去改 bug，见 `openai-transformer-debug`。Apple 端侧推理时 $p=0$，训练图里的除法不会出现在 ANE 上；不要把训练用的缩放常量编译进推理图。

随机种子：想复现结果，必须把 generator 传进去。不同设备上 Bernoulli 采样的实现可能不同，所以单测固定在 CPU 上。LayerDrop / DropPath 是「整层或整条残差分支共用一个 Bernoulli」，不是逐元素采样，不要和普通 dropout 混为一谈。

## 追问

- **为什么推理时不乘 $1-p$？** inverted dropout 在训练时已经保持了激活的期望。推理再乘一次，激活会整体缩小，和训练出来的 checkpoint 不匹配。
- **mask 要不要传梯度？** 离散的 mask 当作常数。反向传播就是把上游梯度乘上同一份 `mask / (1 - p)`，不需要对 Bernoulli 采样求导。
- **和 DropConnect 有什么区别？** Dropout 丢的是激活，DropConnect 丢的是权重。白板默认写逐元素丢激活。Transformer 里 FFN 和 attention 的 dropout 各有各的 $p$。

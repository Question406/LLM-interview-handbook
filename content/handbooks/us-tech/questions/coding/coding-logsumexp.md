---
id: coding-logsumexp
section: coding
order: 20
level: S
title: 白板：log-sum-exp trick，和 cross entropy 的关系
quick: "$\\mathrm{logsumexp}(z)=m+\\log\\sum e^{z-m}$（$m=\\max z$）是 softmax 分母的对数；交叉熵就是 $\\mathrm{logsumexp}(z)-z_y$，不用先算概率。"
tags:
  - 完整编程练习
  - Coding
  - LogSumExp
  - Cross Entropy
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
  - title: torch.nn.functional.cross_entropy
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: torch.nn.functional.log_softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，CPU 上验证；没有验证 GPU 或性能。

### 题面、接口与约束

- `logsumexp(z, dim=-1, keepdim=False)`：数值稳定地计算 $\log\sum_j e^{z_j}$，参数含义和 `torch.logsumexp` 一样。整行都是 `-inf` 时返回 `-inf`；在长度为 0 的维度上约简时抛 `ValueError`。
- `log_softmax(z, dim=-1)`：返回 $z-\mathrm{logsumexp}(z)$。每行至少要有一个有限 logit，全屏蔽行没有概率定义，抛 `ValueError`。
- `nll_from_logits(logits, target)`：`logits` 是 `[N, V]`，`target` 是 `[N]` 的类别下标，返回每个样本的交叉熵 `[N]`。下标越界时抛 `ValueError`。
- 除了全屏蔽行，输入 logits 都是有限值。fp16 / bf16 输入先升到 float32 计算，float64 保持 float64。

### 输入输出示例

```text
logsumexp([1000, 1000])               -> 1000 + ln 2 ≈ 1000.6931
logsumexp([-inf, -inf])               -> -inf
log_softmax([1000, 1001])             -> [-1.3133, -0.3133]
nll_from_logits([[1000, 1001]], [1])  -> [0.3133]
```

### 解题思路与正确性

先求每行的最大值 $m$，计算 $m+\log\sum_j e^{z_j-m}$。所有 $e^{z_j-m}$ 都落在 $(0,1]$，求和不会溢出，而且结果和原式完全相等。

整行都是 `-inf` 时 $m=-\infty$，直接相减会出现 $-\infty-(-\infty)=\text{NaN}$。所以把这种行的平移量换成 0：此时每一项 $e^{-\infty}=0$，求和为 0，取 log 得到 `-inf`，正是数学上的结果。

交叉熵不先算概率再取 log，而是直接在 log 空间里用 `gather` 取出目标类别那一列。这样即使目标类别的概率小到下溢，结果仍是有限值。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def _upcast(z):
    """fp16 / bf16 / 整数升到 float32，float64 保持不变。"""
    return z.to(torch.promote_types(z.dtype, torch.float32))


def logsumexp(z, dim=-1, keepdim=False):
    """数值稳定的 log(sum(exp(z)))；整行都是 -inf 时返回 -inf。"""
    z = _upcast(z)
    if z.shape[dim] == 0:
        raise ValueError(f"cannot reduce over empty dim {dim}")
    row_max = z.amax(dim=dim, keepdim=True)
    # 全 -inf 行的最大值是 -inf，直接相减会得到 -inf - (-inf) = NaN，改用 0 做平移
    shift = torch.where(torch.isfinite(row_max), row_max, torch.zeros_like(row_max))
    out = shift + (z - shift).exp().sum(dim=dim, keepdim=True).log()
    return out if keepdim else out.squeeze(dim)


def log_softmax(z, dim=-1):
    """z - logsumexp(z)；每行至少要有一个有限 logit。"""
    z = _upcast(z)
    row_max = z.amax(dim=dim, keepdim=True)
    if not torch.isfinite(row_max).all():
        raise ValueError("log_softmax needs at least one finite logit per row")
    shifted = z - row_max
    return shifted - shifted.exp().sum(dim=dim, keepdim=True).log()


def nll_from_logits(logits, target):
    """每个样本的交叉熵 -log softmax(logits)[target]。logits: [N, V]，target: [N]。"""
    num_classes = logits.shape[-1]
    if target.min() < 0 or target.max() >= num_classes:
        raise ValueError(f"target must be in [0, {num_classes}), "
                         f"got range [{target.min()}, {target.max()}]")
    log_probs = log_softmax(logits, dim=-1)                       # [N, V]
    return -log_probs.gather(1, target.unsqueeze(1)).squeeze(1)  # [N]
```

### 可执行测试

```python
import math


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
logits = torch.tensor([[1000.0, 1001.0], [-1000.0, -999.0]])

# 大正数和大负数 logit 都不溢出，结果和 PyTorch 一致
assert torch.allclose(logsumexp(logits), torch.logsumexp(logits, -1))
assert torch.allclose(log_softmax(logits), F.log_softmax(logits, -1))

# 示例：logsumexp([1000, 1000]) = 1000 + ln 2
pair = logsumexp(torch.tensor([1000.0, 1000.0]))
assert torch.allclose(pair, torch.tensor(1000.0 + math.log(2)))

# 全 -inf 的一行：logsumexp 返回 -inf 而不是 NaN
all_masked = torch.full((1, 2), -float("inf"))
assert torch.isneginf(logsumexp(all_masked)).all()

# keepdim=True 保留被约简的维度，可以直接广播回原形状
assert logsumexp(logits, dim=-1, keepdim=True).shape == (2, 1)

# float64 不被降成 float32
assert logsumexp(logits.double()).dtype == torch.float64

# 交叉熵：在 log 空间按 target 取值，和 F.cross_entropy 一致
target = torch.tensor([1, 0])
expected = F.cross_entropy(logits, target, reduction="none")
assert torch.allclose(nll_from_logits(logits, target), expected)

# 非法输入：log_softmax 遇到全屏蔽行；target 越界；在空维度上约简
expect_value_error(log_softmax, all_masked)
expect_value_error(nll_from_logits, logits, torch.tensor([2, 0]))
expect_value_error(logsumexp, torch.empty(3, 0))
```

### 复杂度与追问

设输入有 N 个元素。三个函数的时间都是 O(N)；额外空间是每行最大值和求和结果，大小等于被约简轴之外的元素数。

- 追问「全 `-inf` 行为什么 logsumexp 可以算、log_softmax 却要报错」：logsumexp 的结果 `-inf` 本身有意义（比如表示「这一行没有可选项」），但 log_softmax 要用它做分母，得到的是 $-\infty-(-\infty)$，没有概率分布可言。不要把这两种情况混为一谈。

## 题怎么来的

OpenAI 的数值题和交叉熵损失（CE）白板考的是同一项基本功。面试官让你写 `logsumexp`，再问「交叉熵还要不要先过 softmax」。答案是不要：CE 本身就是在 log 空间里用这条归约算出来的。稳定 softmax 见 `coding-softmax-stable`，完整 CE 见 `coding-cross-entropy`。PaLM 的 z-loss 直接对 $z=\mathrm{logsumexp}$ 做正则，见 `coding-z-loss`。

## Trick：先减 max

对向量 $z$（分类时是最后一维，长度为词表大小 $V$）：

$$
\mathrm{logsumexp}(z)=\log\sum_j e^{z_j}=m+\log\sum_j e^{z_j-m},\quad m=\max_j z_j.
$$

减掉 $m$ 后每项 $e^{z_j-m}$ 都在 $(0,1]$，求和落在 $(0,V]$。如果不减，fp32 里 $z_j=80$ 时 `exp` 就已经是 inf，`log(inf)` 让整行结果变成非有限值。减 $m$ 不改变函数值，因为 $\log(e^{m} \sum e^{z-m})=m+\log\sum e^{z-m}$。约简的轴必须和 softmax 用的轴一致，`keepdim` 要保证结果能广播回 `[B, T, V]`。

它和 softmax 的关系是：

$$
\log\mathrm{softmax}(z)_i=z_i-\mathrm{logsumexp}(z),\qquad
\mathrm{softmax}(z)_i=\exp(\log\mathrm{softmax}(z)_i).
$$

one-hot 标签 $y$ 的交叉熵可以直接写成

$$
\ell=-z_y+\mathrm{logsumexp}(z)=-\log\mathrm{softmax}(z)_y.
$$

全程都不需要把概率 $p$ 算出来。如果先 softmax 再 `log(p[y])`，$p_y$ 一旦下溢成 $0$ 就会得到 $-\infty$。熵 $H(\pi)=-\sum\pi\log\pi$ 也可以全程用 log-softmax 来算，见 `openai-entropy-l1`。

`torch.logsumexp` 做的就是这件事。自己写时如果漏了 `keepdim`，`[B, T]` 的结果没法和 `[B, T, V]` 的 logits 相减。

## 平移不变和 z-loss

softmax 在 $z\leftarrow z+c$ 下不变，但 $\mathrm{logsumexp}(z+c)=\mathrm{logsumexp}(z)+c$。CE 也不变，因为 $z_y$ 和 logsumexp 同时加了 $c$。这意味着 logits 可以整体漂移，而 bf16 下绝对值大了会丢精度。z-loss 把 $\mathrm{logsumexp}^2$ 拉回 0 附近，正好固定住这个自由度。FlashAttention 的在线归约维护一对 $(m,\ell)$，满足 $\mathrm{logsumexp}=m+\log\ell$，见 `coding-online-softmax`。

## 追问

- **`log(sum(exp(z)))` 什么时候看起来还能用？** logits 很小，或者用 fp64 的时候。词表上的 CE 和注意力 scores 不要冒这个险。
- **和 `log_softmax` 谁先谁后？** 先算 logsumexp（或者直接用融合的 log-softmax），CE 再 gather 出目标那一列。不要先 softmax 再取 log。
- **整行都是 $-\infty$ 怎么办？** 朴素写法里 max 是 $-\infty$，相减后 $\exp$ 和 $\log$ 都会变成 NaN。上面的参考实现把平移量换成 0，logsumexp 返回 $-\infty$；但 log-softmax 和 CE 在这种行上没有定义，所以 mask 要保证每行至少有一个有限值，或者直接跳过这一行。
- **有温度 $T$ 时呢？** 算 $\mathrm{logsumexp}(z/T)$。先除以 $T$，再做减 max 的 trick，顺序和 `coding-topk-nucleus` 一样。

## 相关题

- [[coding-softmax-stable]]：同一个减 max 技巧用在 softmax 上，重点是轴怎么选，不涉及 log 域。
- [[coding-cross-entropy]]：把这里的恒等式落到带 ignore 下标和有效 token 分母的 CE 实现上。
- [[p3a-openai-masked-cross-entropy-loss]]：OpenAI 的 NumPy 交叉熵题，用 logsumexp 算 log-softmax，再加 mask、label smoothing 和手写梯度。
- [[coding-z-loss]]：z-loss 罚的 $\log Z$ 就是这里的 logsumexp，那张讲它为什么会漂、系数取多少。
- [[coding-fused-ce]]：把 logsumexp 沿词表分块、用 running $(m,\ell)$ 攒起来，避免物化整份 logits。

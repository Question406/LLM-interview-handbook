---
id: coding-fused-ce
section: coding
order: 29
level: S
title: 白板：融合 linear 和 cross entropy，不要物化 `[B, T, V]` logits
quick: "沿词表分块算 $hW^\\top$，用 running $(m,\\ell)$ 累计 logsumexp，目标 logit 则单独算 $h^\\top w_y$。这样前向不分配完整 `[N, V]` logits；训练峰值显存的收益还需要自定义 backward 或重算。"
tags:
  - 完整编程练习
  - Coding
  - Cross Entropy
  - Fused Kernel
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: The Liger Kernel — Efficient Triton Kernels for LLM Training
    url: https://arxiv.org/abs/2410.10989
    type: primary
  - title: torch.nn.functional.cross_entropy
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: Online normalizer calculation for softmax
    url: https://arxiv.org/abs/1805.02867
    type: primary
---

## 题目描述

在不能保存完整词表 logits 矩阵的条件下，实现线性输出层与交叉熵的组合。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`fused_linear_ce(h,weight,target,ignore_index=-100,chunk=4096)` 返回平均交叉熵标量。h 为 `[N,D]`，weight 为 `[V,D]`，target 为 `[N]` 整数标签；未忽略标签在 `[0,V)`，`ignore_index` 可为任意整数。第 i 个样本的词表 logits 是 h[i] 与 weight 各行的内积，交叉熵使用完整词表归一化。

只对 target 不等于 `ignore_index` 的样本取平均。全部忽略时返回仍连接计算图的标量 0，使 h、weight 的梯度均为 0。chunk 为正整数，运算中不能分配完整 `[N,V]` logits，应限制同时处理的词表列数不超过 chunk；结果和梯度须与完整交叉熵一致。

### 示例

```text
h=[[0]], weight=[[1],[2]], target=[0], chunk=1
返回约 0.69314718。
若 target=[99], ignore_index=99，返回 0，h 和 weight 梯度均为 0。
```

## 解题思路与参考答案

我会沿词表分块计算，因为交叉熵 $\ell=-z_y+\mathrm{logsumexp}(z)$ 只依赖目标 logit $z_y$ 和每行 logsumexp，不需要先保留整张 logits。$z_y=h^\top w_y$ 可以直接取出权重的第 $y$ 行做点积。logsumexp 沿词表分块累计：每一行维护到目前为止的最大值 $m$ 和以 $m$ 为基准的指数和 $\ell$；新块的最大值更大时，旧的 $\ell$ 乘以 $\exp(m_{\text{old}}-m_{\text{new}})$ 换到新基准，再加上新块的指数和。第一块时 $m=-\infty$，$\exp(-\infty)=0$，旧和自然清零。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证；这是分块前向的参考实现，没有写自定义 backward，也没有测显存。

### 题面、接口与约束

- `fused_linear_ce(h, weight, target, ignore_index=-100, chunk=4096) -> Tensor`：`h` 形状 `[N, D]`，`weight` 形状 `[V, D]`（`nn.Linear` 的 weight），`target` 形状 `[N]`。沿词表每次只算 `chunk` 列 logits，不分配完整的 `[N, V]`，返回未忽略目标上的平均交叉熵。
- `chunk` 是正整数，否则抛 `ValueError`；未忽略的目标必须在 `[0, V)` 内，否则抛 `ValueError`。`ignore_index` 可以是任意整数，包括大于 V 的值。
- 全部目标被忽略时，返回一个同时连着 `h` 和 `weight` 的标量 0，反传后两者梯度都是 0。

### 输入输出示例

```text
h: [3, 4], weight: [7, 4], target = [1, 99, 6], ignore_index = 99
fused_linear_ce(..., chunk=1)   == F.cross_entropy(h @ weight.T, target, ignore_index=99)
fused_linear_ce(..., chunk=20)  == 同上（chunk >= V 时退化成一整块）
target 全是 99                  -> 0，h 和 weight 的梯度全为 0
```

### 解题思路与正确性

被忽略的目标先替换成 0 再 gather，避免 `ignore_index` 大于 V 时越界；平均只在有效位置上做。

普通 autograd 会为每一块保留反向需要的中间结果，所以这份代码只保证前向的临时 logits 是 O(N·chunk)，不能说训练时的峰值显存也降到这个量级。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def fused_linear_ce(h, weight, target, ignore_index=-100, chunk=4096):
    """沿词表分块的 linear + cross entropy 前向。

    h: [N, D]，weight: [V, D]，target: [N]。不分配完整的 [N, V] logits，
    返回未忽略目标上的平均损失。
    """
    if type(chunk) is not int or chunk < 1:
        raise ValueError(f"chunk must be a positive int, got {chunk!r}")
    num_rows, vocab = h.size(0), weight.size(0)
    keep = target != ignore_index
    if bool((((target < 0) | (target >= vocab)) & keep).any()):
        raise ValueError(f"target outside [0, {vocab})")

    h32 = h.float()
    w32 = weight.float()
    running_max = h32.new_full((num_rows,), float("-inf"))  # [N]
    running_sum = h32.new_zeros(num_rows)                     # [N]，以 running_max 为基准
    for start in range(0, vocab, chunk):
        logits = h32 @ w32[start : start + chunk].T           # [N, C]
        new_max = torch.maximum(running_max, logits.amax(dim=-1))
        running_sum = running_sum * torch.exp(running_max - new_max) + torch.exp(logits - new_max[:, None]).sum(-1)
        running_max = new_max

    if not bool(keep.any()):
        return (h.sum() + weight.sum()) * 0.0  # 保留到 h 和 weight 的计算图

    safe_target = torch.where(keep, target, torch.zeros_like(target))
    target_logit = (h32 * w32[safe_target]).sum(-1)          # [N]，z_y = h · w_y
    nll = -target_logit + running_max + running_sum.log()
    return nll[keep].mean()
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(fused, reference, atol=1e-6)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(2)
h = torch.randn(3, 4, requires_grad=True)
w = torch.randn(7, 4, requires_grad=True)
target = torch.tensor([1, 99, 6])

# 不同 chunk（含 1、不整除 V、大于 V）的损失和梯度都与未融合版本一致
for chunk in (1, 3, 20):
    fused = fused_linear_ce(h, w, target, ignore_index=99, chunk=chunk)
    reference = F.cross_entropy(h @ w.T, target, ignore_index=99)
    assert torch.allclose(fused, reference, atol=1e-6)
    fused_grads = torch.autograd.grad(fused, (h, w))
    reference_grads = torch.autograd.grad(reference, (h, w))
    for got, want in zip(fused_grads, reference_grads):
        assert torch.allclose(got, want, atol=1e-6)

# 全部忽略：返回 0，h 和 weight 的梯度都是 0
zero = fused_linear_ce(h, w, torch.full((3,), 99), ignore_index=99, chunk=2)
assert zero == 0
for grad in torch.autograd.grad(zero, (h, w)):
    assert torch.all(grad == 0)

# 很大的 logits 也不溢出
big_h = torch.tensor([[100.0, 0.0]])
big_w = torch.tensor([[10.0, 0.0], [0.0, 1.0]])
assert torch.isclose(fused_linear_ce(big_h, big_w, torch.tensor([0]), chunk=1), torch.tensor(0.0), atol=1e-6)

# 非法 chunk、越界目标
expect_value_error(fused_linear_ce, h, w, target, ignore_index=99, chunk=0)
expect_value_error(fused_linear_ce, h, w, torch.tensor([0, 1, 7]))
```

### 复杂度与追问

设 N 行、隐藏维 D、词表 V、块宽 C（即 `chunk`）。前向时间 O(NVD)；临时 logits 块 O(NC)，另外还有 `h`、`weight` 的 float32 副本。

- 追问「训练时显存也能降下来吗」：要自定义 backward 或在反向时重算每块 logits，不能只靠 Python 的 for 循环。反向需要 $\partial L/\partial z=p-e_y$，可以再扫一遍 V 的块重算 $p$，不存整表。
- 追问「chunk 是不是越小越好」：不是。块太小时 GEMM 太瘦、硬件占用率低。应该选能放进 SRAM / L2 的 C，而不是 C=1。

## 题怎么来的

词表 $V$ 到十万量级时，logits `[B, T, V]` 往往比隐状态还大。NVIDIA 训练 kernel 岗和 OpenAI 的 debug 题都会问：交叉熵损失（CE）要不要物化整张 logits 表。损失只依赖目标那一列和整行的 logsumexp，不必保留 `[N, V]`。Liger、Apex、Megatron 的 fused linear-cross-entropy 都是沿 $V$ 分块算 $hW^\top$，用 online 归约累计分母，反向时再扫一遍块。公式基础见 `coding-cross-entropy` 和 `coding-logsumexp`。

## 只留 $z_y$ 和 $(m,\ell)$

把 `[B, T, D]` 展平成 $h\in\mathbb{R}^{N\times D}$，$W\in\mathbb{R}^{V\times D}$，目标 $y\in\{0,\ldots,V-1\}^N$。

$$
z=hW^\top,\qquad
\ell_{\mathrm{CE}}=-z_y+\mathrm{logsumexp}(z).
$$

$z_y=h^\top W_{y}$ 只要按行 gather 权重，复杂度 $O(ND)$。logsumexp 沿 $V$ 切成宽 $C$ 的块：第 $c$ 块 $z^{(c)}=h W^{(c)\top}$ 形状 `[N, C]`，用和 FlashAttention 相同的 running max / sumexp 更新全局 $(m,\ell)$，用完就丢。最后

$$
\mathrm{logsumexp}(z)=m+\log\ell,\qquad
\ell_{\mathrm{CE}}=-z_y+m+\log\ell.
$$

pad 和 ignore 下标不进均值，分母是有效 token 数，与 `coding-cross-entropy` 是同一契约。shift 仍是 `h[:, :-1]` 对 `labels[:, 1:]`，要在展平之前做。

单测时用小 $V$ 对照 `F.cross_entropy(h @ W.T, y)`。如果对不上，通常是 ignore 位置进了分母，或者 $z_y$ 取错了行。第一块时 $m=-\infty$、$\exp(m-m_2)=0$，和 `coding-online-softmax` 的空起点一样。

## 显存、反向和权重绑定

分块前向时，单块临时 logits 约为 $O(NC)$。但普通 autograd 可能为每块保留反向所需的激活，所以不能据此断言训练峰值显存从 $O(NV)$ 降到了 $O(NC)$，要靠自定义 backward 或重计算才能拿到这部分收益。举个量级：$V=128256$、$N=B\cdot T=8192$、$C=4096$ 时，一块 bf16 logits 约 $64\,\mathrm{MiB}$，整表则在 $2\,\mathrm{GiB}$ 量级。fused kernel 就是用反向时重算 $p$ 的额外计算换掉这部分显存。如果面试官只要求写前向，先把「不物化整表」讲清楚。

Weight tying 时 $W$ 就是 embedding 矩阵，见 `coding-weight-tying`。fused 路径仍然用同一份存储，不要为了分块再 clone 一份 $W$。z-loss 需要的 $\mathrm{logsumexp}$ 正是这里的 $m+\log\ell$，可以在同一趟里加上 $10^{-4}(m+\log\ell)^2$，见 `coding-z-loss`。Tensor parallel 沿 $V$ 切开时，每张卡先算局部 logsumexp，再跨卡 all-reduce 最大值和换基准后的 $\ell$，这和 split-K 注意力是同一类归约，见 `coding-flash-decode`。

## 追问

**为什么不能先 softmax 再 log？**
原因和未融合的 CE 一样：概率会下溢成 0，取 log 得到 $-\infty$。融合不改变这条数值约束。
**label smoothing 怎么办？**
目标不再是单列，只算 $z_y$ 不够，要对整行算 $-q\log\pi$。仍然可以分块，但每块都要累加 $q_c\log\pi_c$，实现明显更复杂。
**$(m,\ell)$ 能用 fp16 存吗？**
应该升到 fp32。词表上的 sumexp 和注意力里一样容易溢出。

## 相关题

- [[coding-cross-entropy]]：未融合的 CE，先把 log 域写法、ignore 下标和分母做对，再来做这题。
- [[coding-logsumexp]]：这里沿词表攒的 $(m,\ell)$ 就是分块版的 logsumexp，那张讲单块的减 max 技巧。
- [[coding-online-softmax]]：同一套 running max / sumexp 的 rescale，那里沿 key 维用在注意力上，这里沿词表维用在 CE 上。
- [[coding-token-logprob]]：RL 里从 logits 取 response 的 token logprob，同样会撞上 `[B, T, V]` 的显存问题。

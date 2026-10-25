---
id: coding-grad-clip
section: coding
order: 10
level: A
title: 白板：global norm clip， inf/nan 怎么处理
quick: "先算所有梯度拼成一个向量后的 $L_2$ 范数 $g$，有限且超阈值时才统一缩放。NaN/Inf 时按约定报错或跳过 step，不能边检查边改梯度；混合精度先 unscale，再 clip。"
tags:
  - 完整编程练习
  - Coding
  - Gradient Clipping
  - NVIDIA
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: torch.nn.utils.clip_grad_norm_
    url: https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
    type: primary
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5065
    type: primary
---

## 题目描述

训练中多个参数共享一个梯度范数上限。实现全局范数计算与原位裁剪，保持各参数梯度的相对比例，并允许部分参数没有梯度。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `total_grad_norm(params) -> float` 返回所有非空梯度合并后的 L2 范数；跳过 `grad is None`，没有梯度则返回 0。
- `clip_grad_norm_(params, max_norm, eps=1e-6, error_if_nonfinite=True) -> float` 返回裁剪前的范数，并把所有梯度原位乘同一个系数 `min(1, max_norm/(norm+eps))`。
- params 可以是序列或只可遍历一次的生成器，梯度形状可以各不相同。本练习输入梯度均有限，`max_norm` 为有限非负数、eps 为正数；无需实现非有限梯度校验扩展。

### 输入输出示例

```text
grad = [3, 4], max_norm = 2.5  -> grad 变成 [1.5, 2.0]，返回 5.0
grad = [3, 4], max_norm = 10   -> grad 不变，返回 5.0
```

## 解题思路与参考答案

超过阈值时，所有梯度统一乘 $\mathrm{max}/(g+\varepsilon)$，保持整个梯度向量的方向。global norm clip 要分两步：先完整计算所有梯度的总范数并确认有限，再用同一个系数缩放。如果边算边改，遇到后面某个参数的 NaN 时，前面的梯度已经被改过了，没法回到原状。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `total_grad_norm(params) -> float`：所有参数梯度合起来的全局 $L_2$ 范数；跳过 `grad is None` 的参数，没有梯度时返回 `0.0`；任何梯度含 NaN/Inf 时返回 `inf`。
- `clip_grad_norm_(params, max_norm, eps=1e-6, error_if_nonfinite=True) -> float`：按全局范数统一原位缩放所有梯度，返回裁剪**前**的范数。
- `params` 是参数序列（也可以是生成器），允许有 `grad=None` 的参数。
- `max_norm` 必须有限且非负，否则抛 `ValueError`。
- 梯度含 NaN/Inf 时：默认抛 `RuntimeError`，而且抛出之前不能改动任何梯度；`error_if_nonfinite=False` 时返回 `inf`，梯度保持原样。

### 输入输出示例

```text
grad = [3, 4], max_norm = 2.5  -> grad 变成 [1.5, 2.0]，返回 5.0
grad = [3, 4], max_norm = 10   -> grad 不变，返回 5.0
grad = [nan, 1], max_norm = 1  -> RuntimeError，grad 不变
```

### 解题思路与正确性

所有梯度乘的是同一个系数 $\mathrm{max\_norm}/(g+\varepsilon)$，整个梯度向量的方向不变，只是长度缩短。逐参数各自裁剪会让不同参数的缩放比例不同，方向就变了。系数不小于 1 时什么都不做，保证不会把小梯度放大。

范数先转成 float32 再算，这样 fp16/bf16 的梯度平方求和不会溢出。

### 完整参考实现（Python 3）

```python
import math

import torch
from torch import nn


def total_grad_norm(params):
    """所有非 None 梯度的全局 L2 范数；有 NaN/Inf 时返回 inf。"""
    total = 0.0
    for param in params:
        if param.grad is None:
            continue
        grad = param.grad.detach().float()  # 低精度梯度先转 float32，平方和不溢出
        if not torch.isfinite(grad).all():
            return float("inf")
        total += float(grad.norm(2).item() ** 2)
    return math.sqrt(total)


def clip_grad_norm_(params, max_norm, eps=1e-6, error_if_nonfinite=True):
    """按全局 L2 范数原位裁剪梯度，返回裁剪前的范数。

    范数非有限时：默认抛 RuntimeError；error_if_nonfinite=False 时返回 inf。两种情况都不改梯度。
    """
    if not (math.isfinite(max_norm) and max_norm >= 0):
        raise ValueError(f"max_norm must be finite and non-negative, got {max_norm}")
    params = [param for param in params if param.grad is not None]
    norm = total_grad_norm(params)
    if not math.isfinite(norm):
        if error_if_nonfinite:
            raise RuntimeError("gradient norm is non-finite, no gradients were modified")
        return norm
    scale = max_norm / (norm + eps)
    if scale < 1.0:
        for param in params:
            param.grad.mul_(scale)
    return norm
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert norm == 5` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
torch.set_num_threads(1)


def expect_error(error_type, action):
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


# 题面示例：范数 5 裁到 2.5，返回裁剪前的范数
param = nn.Parameter(torch.zeros(2))
param.grad = torch.tensor([3.0, 4.0])
norm = clip_grad_norm_([param], 2.5)
assert norm == 5
assert torch.allclose(param.grad, torch.tensor([1.5, 2.0]), atol=1e-6)

# 范数没超过阈值：梯度不变
param.grad = torch.tensor([3.0, 4.0])
assert clip_grad_norm_([param], 10.0) == 5
assert torch.equal(param.grad, torch.tensor([3.0, 4.0]))

# 含 NaN：默认报错，梯度保持原状
param.grad = torch.tensor([float("nan"), 1.0])
before = param.grad.clone()
expect_error(RuntimeError, lambda: clip_grad_norm_([param], 1))
assert torch.allclose(param.grad, before, equal_nan=True)

# 后一个参数含 Inf 时，前一个参数的梯度也不能被先改掉
first = nn.Parameter(torch.zeros(2))
first.grad = torch.tensor([30.0, 40.0])
second = nn.Parameter(torch.zeros(1))
second.grad = torch.tensor([float("inf")])
assert clip_grad_norm_([first, second], 1.0, error_if_nonfinite=False) == float("inf")
assert torch.equal(first.grad, torch.tensor([30.0, 40.0]))

# 没有梯度的参数被跳过；全都没有梯度时范数为 0
assert total_grad_norm([nn.Parameter(torch.ones(2))]) == 0
no_grad_params = [nn.Parameter(torch.zeros(1)), nn.Parameter(torch.ones(3))]
assert clip_grad_norm_(no_grad_params, 1.0) == 0

# 多个参数按全局范数统一缩放，方向不变
left = nn.Parameter(torch.zeros(1))
left.grad = torch.tensor([6.0])
right = nn.Parameter(torch.zeros(1))
right.grad = torch.tensor([8.0])
assert clip_grad_norm_(iter([left, right]), 5.0) == 10
assert torch.allclose(left.grad, torch.tensor([3.0]), atol=1e-5)
assert torch.allclose(right.grad, torch.tensor([4.0]), atol=1e-5)

# fp16 梯度的平方和超出 fp16 范围，也能算对
half = nn.Parameter(torch.zeros(2, dtype=torch.float16))
half.grad = torch.tensor([300.0, 400.0], dtype=torch.float16)
assert total_grad_norm([half]) == 500

# 非法 max_norm
expect_error(ValueError, lambda: clip_grad_norm_([left], -1.0))
expect_error(ValueError, lambda: clip_grad_norm_([left], float("inf")))
```

### 复杂度与追问

设梯度元素总数为 P。时间 O(P)；参考实现对每个 tensor 产生一份 float32 临时副本，额外空间是最大那个 tensor 的大小。

- 追问「分布式训练里怎么算全局范数」：各 rank 先算本地分片的平方和，all-reduce 求和后再开方。被复制到多个 rank 上的参数（例如张量并行里没切分的 LayerNorm）只能算一次，不能重复累加。
- 追问「少一次 host 同步」：现在每个 tensor 调一次 `.item()`。可以把各 tensor 的平方和在设备上 `stack` 起来求和，最后只同步一次（PyTorch 的 foreach 路径就是这么做的）。

## 题怎么来的

Pascanu et al. 把 global norm clip 作为 RNN 训练的标准做法；LLM 预训练同样靠它限制过大的梯度。NVIDIA 训练岗爱问「clip 的是什么范数、遇到 inf 怎么办」；OpenAI / Meta 的训练代码题会把 clip 放在 scaler unscale 之前，作为埋进去的 bug。PyTorch 的入口是 `clip_grad_norm_`。和 AdamW 怎么衔接，见 `coding-adamw`。

## Global $L_2$：一个标量管所有参数

$$
g=\sqrt{\sum_i \|h_i\|_2^2},\qquad
c=\min\bigl(1,\ \mathrm{max\_norm}/(g+\varepsilon)\bigr),\qquad
h_i\leftarrow c\,h_i.
$$

$h_i$ 是第 $i$ 个参数的 `.grad`。这是全局范数，不是每层各自 clip。逐层 clip 会改变层与层之间的相对步长；全局 clip 只保证拼起来的整个梯度向量的欧氏长度不超过 `max_norm`。$g\le \mathrm{max\_norm}$ 时 $c=1$，梯度不动。

不要对每个 tensor 单独除以自己的范数再乘 `max_norm`，那是 per-tensor clip，和 `clip_grad_norm_` 不是一回事。`clip_grad_value_` 是逐元素夹到区间里，也不是全局范数裁剪。

返回值 $g$ 是 clip 之前的范数，用来打日志：如果它突然变成 `inf`，说明这一批数据的梯度出现了异常。$\varepsilon$ 只是防止 $g=0$ 时除零，正常训练中 $g$ 不会真的是 0。

## inf / nan：不要乘一个 NaN 系数

如果某个 `.grad` 已经是 inf 或 nan，$g$ 就不是有限值，`max_norm / g` 会变成 0 或 NaN，再 `mul_` 下去，所有参数的梯度都会被污染成 NaN，训练就坏了。PyTorch 1.13 起，`error_if_nonfinite=True` 会直接抛异常。训练中的处理方式：

1. 跳过这一步：`zero_grad`，不调用 `optimizer.step`；
2. 或者直接 crash，从 checkpoint 回滚；
3. 不要悄悄把它当成 0 继续训练，却不打任何日志。

混合精度要先 `GradScaler.unscale_(opt)` 再 clip。先 clip 再 unscale，等于在被放大过的 fp16 梯度上算范数，阈值完全对不上。在梯度有限时，foreach kernel 和逐 tensor 循环应该算出同一个 $g$；有 inf 时 foreach 路径的具体行为要查当前版本的文档，白板上说「先检查有限性，再算范数」更稳妥。

NVIDIA 还会问：clip 改变的是梯度向量的长度，不改变各坐标之间的相对比例。如果是 loss 本身爆成了 inf，clip 救不了，要先查数据、数值溢出，以及没有减去最大值的 softmax，见 `coding-softmax-stable`。

## 追问

**为什么用全局范数而不是逐层？**
全局 clip 保持层与层之间的相对尺度；逐层 clip 相当于每层各自做一次归一化，深层和浅层的步长被强行拉到一样。
**$g=0$ 是什么情况？**
所有参数都没有梯度，比如忘了 backward，或者 loss 全被 mask 掉了。这时不要 step。$\varepsilon$ 只是除零保护。
**和 grad scaler 的顺序？**
unscale → clip → step → scaler.update。顺序反了，阈值就是错的，还可能把 inf 写进 master weight。

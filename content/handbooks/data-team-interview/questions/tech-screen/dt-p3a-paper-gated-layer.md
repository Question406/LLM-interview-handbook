---
id: dt-p3a-paper-gated-layer
section: tech-screen
order: 94
level: S
title: Apple CV/ML 面经形式练习：读公式实现可训练的 gated residual layer
quick: >-
  先澄清 tensor 形状、matrix 乘法方向、广播与 parameter sharing，再从公式写 forward。用可手算的初始状态检查输出，用
  gradient 和参数注册检查能否真正训练；本题公式自拟，原帖未公开论文或层名。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地
  - AFM 专项 2026-10
  - 来源主题扩展
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: Apple CV/ML 面经，Chrome 原帖核对
    url: 'https://www.1point3acres.com/bbs/thread-950206-1-1.html'
    type: interview
  - title: PyTorch Parameter
    url: >-
      https://docs.pytorch.org/docs/stable/generated/torch.nn.parameter.Parameter.html
    type: primary
  - title: PyTorch gradcheck
    url: 'https://docs.pytorch.org/docs/stable/notes/gradcheck.html'
    type: primary
---

## 题目描述

### 来源与练习约定

原帖页面显示 2022-12-02 14:37:36，Apple CV/ML MLE，具体团队未披露。2026-10-26 在 Chrome 查看主楼和可见作者回复：候选人报告给论文、用 TensorFlow 或 PyTorch 实现其中一层；后续回复说明从底层权重和运算开始。原帖未公开论文、公式或层名。

以下 gating 残差公式为手册自拟，只模拟“从公式实现可训练 layer”的面试形式，不声称 Apple 问过该层，因此 `realInterview: false`。建议限时 25 分钟。

### 输入与接口

实现 `GatedResidual(dim)`，继承 `torch.nn.Module`，提供 `forward(x)`。dim 为正整数，x 为浮点 tensor，形状 `[B,T,D]` 或 `[B,D]`，D=dim，B、T 为正。输入与模块参数 dtype 和 device 一致。参数需被 optimizer 和 state_dict 正确识别。

### 输出与约束

层的计算约定如下：

$$g=\sigma(xW+b),\qquad y=x+g\odot(x\odot s).$$

W 形状 `[D,D]`，b 与 s 形状 `[D]`，共享于所有样本与时间位置，sigmoid 按元素计算，乘法按末维广播。W、b 初始为 0，s 初始为 1，三者均可训练。返回与 x 同形状的 y，不修改 x，不使用 detach 或 data 改写结果。保留自动求导路径，不允许直接调用已有 gating layer。

### 示例

```text
初始dim=2，x=[[[2.,-4.],[0.,6.]]]
g恒为0.5，输出=[[[3.,-6.],[0.,9.]]]
```

## 解题思路与参考答案

先按行向量约定读懂 xW：最后一维 D 乘权重首维 D，输出仍为 D。偏置和缩放只在最后一维，不能按 batch 长度创建。继承 Module 并注册 Parameter，保证 optimizer 拿得到参数。

```python
import torch
from torch import nn


class GatedResidual(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.weight = nn.Parameter(torch.zeros(dim, dim))
        self.bias = nn.Parameter(torch.zeros(dim))
        self.scale = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        gate = torch.sigmoid(x @ self.weight + self.bias)
        return x + gate * (x * self.scale)
```

初始 W 与 b 为零，gate 为 0.5，因此输出为 1.5x。这是本题便于手算的初始化，不是声称残差 gating 应普遍采用这种初始化。参数量为 D 平方加 2D；对 `[B,T,D]` 输入，主要计算为 $O(BTD^2)$。

## 简单测试怎么写

将实现与下面测试保存为 `solution.py`，运行 `python3 solution.py`，需要 PyTorch。先手算初始输出与输入 gradient，再检查所有参数都注册，并用双精度数值检查自动求导。gradcheck 只检查传入的 x；参数 gradient 由额外 assertion 验证存在且为有限值，不把此项误称为全部参数的数值验证。

```python
layer = GatedResidual(2).double()
x = torch.tensor([[[2.0, -4.0], [0.0, 6.0]]], dtype=torch.float64, requires_grad=True)
before = x.detach().clone()
y = layer(x)
assert y.shape == x.shape
assert torch.allclose(y, torch.tensor([[[3.0, -6.0], [0.0, 9.0]]], dtype=torch.float64))
assert torch.equal(x.detach(), before)
y.sum().backward()
assert torch.allclose(x.grad, torch.full_like(x, 1.5))
assert set(dict(layer.named_parameters())) == {'weight', 'bias', 'scale'}
assert all(
    p.grad is not None and torch.isfinite(p.grad).all() for p in layer.parameters()
)
# dL/db = 0.25 * sum(x)，dL/ds = 0.5 * sum(x)，沿所有前置维求和。
assert torch.allclose(layer.bias.grad, torch.tensor([0.5, 0.5], dtype=torch.float64))
assert torch.allclose(layer.scale.grad, torch.tensor([1.0, 1.0], dtype=torch.float64))
check_x = torch.tensor([[0.3, -0.7]], dtype=torch.float64, requires_grad=True)
assert torch.autograd.gradcheck(layer, (check_x,), eps=1e-6, atol=1e-5)
# 显式设非对称权重，发现把xW误写成xW转置的问题。
with torch.no_grad():
    layer.weight.copy_(torch.tensor([[0.0, 1.0], [0.0, 0.0]], dtype=torch.float64))
nonzero = layer(torch.tensor([[2.0, 1.0]], dtype=torch.float64))
expected = torch.tensor(
    [[3.0, 1.0 + torch.sigmoid(torch.tensor(2.0)).item()]], dtype=torch.float64
)
assert torch.allclose(nonzero, expected, atol=1e-7)
```

## 面试追问

**公式不完整时先问什么？** 明确输入输出形状、parameter sharing 维度、matrix 方向、初始化和是否需要手写 backward。若论文符号矛盾，先指出并约定，不能一边猜一边改接口。

**forward 对了就能训练吗？** 不足。还要检查参数注册、gradient 路径、optimizer 是否接收到参数，以及 train/eval 是否包含状态变化。本题没有 dropout 或 normalization 状态，但真实论文层可能有。

**gradient 检查不通过一定是公式错吗？** 不一定。随机性、精度不足、不 differentiable 点或过大/过小差分步长都可能造成失败。固定输入与状态，用双精度和可手算位置逐步定位。

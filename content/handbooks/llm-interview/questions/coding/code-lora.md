---
id: code-lora
section: coding
order: 13
level: A
title: 手写 LoRA 前向：$y=Wx+(\alpha/r)BAx$
quick: >-
  冻住 $W$，只训 $A\in\mathbb{R}^{r\times d_{\mathrm{in}}}$ 和
  $B\in\mathbb{R}^{d_{\mathrm{out}}\times r}$，前向是 $Wx+(\alpha/r)B(Ax)$。$A$
  用高斯、$B$ 全零初始化，起步就等价于原模型；$\alpha/r$ 把更新幅度从 rank 里解耦。LoRA 别接在 LayerNorm 后面。
tags:
  - LoRA
  - PEFT
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: LoRA
    url: 'https://arxiv.org/abs/2106.09685'
    type: primary
---

## 题目描述

为已有线性层增加低秩可训练增量，同时冻结原权重。初始化后应与原线性层完全相同。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `LoRALinear(W,r=8,alpha=16)` 及 `forward(x)`。W 为 [`d_out`,`d_in`] 浮点张量，以 buffer 保存；r 为正整数。A 为 [r,`d_in`] 可训练随机小权重，B 为 [`d_out`,r] 可训练全零权重；x 为 [...,`d_in`]。

### 输出与约束

返回 x@W.T+(alpha/r)*(x@A.T)@B.T，形状 [...,`d_out`]。只有 A/B 参与训练，W 不更新。由于 B 初始为零，初始化时输出应等于基础投影。

### 示例

```text
W=[[1,2]], x=[[3,4]], r=1, alpha=1
初始化后的 forward(x) -> [[11]]；W不出现在可训练参数中。
```

## 解题思路与参考答案

LoRA 的前向就是原来的 $Wx$ 再加一条低秩支路：冻住 $W$，只训练 $A$ 和 $B$，支路输出乘上缩放 $\alpha/r$。现场最常见的写法是在激活上做两次小 GEMM，先算 $Ax$ 再乘 $B$，结果要和「先把 $BA$ 加到 $W$ 上再乘 $x$」一致。

$$
y=Wx+\frac{\alpha}{r}B(Ax).
$$

这相当于把 $\Delta W$ 参数化成低秩：$W'=W+BA$，再乘缩放 $\alpha/r$，其中 $r\ll \min(d_{\mathrm{in}},d_{\mathrm{out}})$。$\alpha$ 一般固定，常见 16 或 32，有了这个缩放，改 $r$ 的时候学习率不用按 $r$ 重调。初始化是 $A$ 高斯、$B$ 全零，$B=0$ 起步 $\Rightarrow$ $y=Wx$，和原模型完全一样。

```python
import torch
import torch.nn as nn


class LoRALinear(nn.Module):
    def __init__(self, W, r=8, alpha=16):
        super().__init__()
        d_out, d_in = W.shape
        self.register_buffer("W", W)
        self.A = nn.Parameter(torch.randn(r, d_in) * 0.02)
        self.B = nn.Parameter(torch.zeros(d_out, r))
        self.scale = alpha / r

    def forward(self, x):
        return x @ self.W.T + self.scale * (x @ self.A.T) @ self.B.T
```

形状上 $x$ 是 `[..., d_in]`。写成 `B @ A @ x` 的话，很容易把 batch 维挤掉。

实现时还有几处容易出事。LoRA 别挂在 LayerNorm 后面：LN 输出的分布和 $W$ 训练时看到的不一致，低秩适配器的训练可能偏离预期，美团那张卡也写过「LoRA 不要接在 LayerNorm 后」。推理时可以把 $(\alpha/r)BA$ 合并回 $W$，去掉额外延迟；训练时别每步都 merge，不然和优化器状态对不上。QLoRA 是把 $W$ 量化存储，前向时先反量化再加 LoRA 支路，手写这题用全精度 $W$ 就够了。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

B 初始化为零时，LoRA 输出必须等于原线性层。之后 backpropagation 检查 B 有梯度且被冻结的 W 没有梯度；这能发现初始化或冻结方式的错误。

```python
torch.manual_seed(7)
W = torch.randn(3, 2)
layer = LoRALinear(W, r=1, alpha=1)
x = torch.tensor([[1.0, 2.0]])
torch.testing.assert_close(layer(x), x @ W.T)
layer(x).sum().backward()
assert layer.B.grad is not None and layer.B.grad.abs().sum() > 0
assert layer.W.grad is None
print("simple tests passed")
```

## 追问

**为什么 $B$ 初始化成零、$A$ 用高斯？**
反过来的话，起步时 $\Delta W\neq 0$，一上来就破坏了基座。

**rank 和 $\alpha$ 谁管更新幅度？**
有效步长 $\propto \alpha/r$。只加大 $r$、不动 $\alpha$，更新会变弱。

**和 Adapter 有什么区别？**
Adapter 在层间插一个小 FFN，会改变深度、增加延迟；LoRA 改的是已有的矩阵，训完可以 merge 回去。

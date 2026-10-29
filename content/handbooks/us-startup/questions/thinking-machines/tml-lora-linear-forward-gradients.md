---
id: tml-lora-linear-forward-gradients
section: thinking-machines
order: 900
level: A
title: "Thinking Machines 机制练习：LoRA Linear、初始化与 gradients"
quick: "我会先让输出在初始化时与 base model 一致，再检查第一步是否有学习信号。A 随机、B 为零时 update 为零，但 B 的 gradient 仍可能非零；两边都为零则会阻断这条乘积参数化的初始 gradients。"
companies:
  - thinking-machines
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "公开机制练习"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "Thinking Machines Lab：LoRA Without Regret"
    url: "https://thinkingmachines.ai/blog/lora/"
    type: primary
---

## 题目描述

来源类别：官方研究文章衍生的编程练习。参考 John Schulman 等人的 LoRA Without Regret，将 LoRA 参数化整理成一个可运行 Linear layer。

### 输入、接口与规则

实现 PyTorch `LoRALinear(weight,rank,alpha)`。weight 为 floating `[out,in]` 的非空矩阵，rank 为正整数，alpha 为 finite 正数。复制并冻结 base weight，A 为 `[rank,in]` 小随机初始化，B 为 `[out,rank]` 全零初始化；两者可训练。Layer 不含 bias。

`forward(x)` 对 `[B,in]` 输入返回 `[B,out]`，按 base Linear 加 `alpha/rank` 缩放的 LoRA update 计算。`merged_weight()` 返回新 tensor `weight + (alpha/rank)*(B@A)`，不修改 base weight 或 adapters。

验证初始输出等于 base、base 不接收 gradients、第一次 backward 中 A 的 gradient 为零但 B 可非零，以及更改 B 后 merged forward 与 adapter forward 一致。另把 A/B 都置零，检查为什么不能从这种初始化正常开始学习。测试固定 seed，不要求复现文章实验数字。

### 输入输出示例

```text
weight.shape=[3,5], rank=2, alpha=4 -> A.shape=[2,5], B.shape=[3,2]。
初始 B=0，forward(x) 等于 x@weight.T；可训练参数数目=2*(5+3)=16。
```

## 回答思路

> **输入与任务：** 区分 frozen base weight 与两个 trainable adapters。  
> **做法与原因：** 初始 update 为零，但随机 A 使 B 可以拿到第一步 gradient。  
> **正确性检查：** 检查 gradients、trainable 参数数目和 merge 后的数值等价。

## 解题思路与参考答案

我会先让输出在初始化时与 base model 一致，再检查第一步是否有学习信号。A 随机、B 为零时 update 为零，但 B 的 gradient 仍可能非零；两边都为零则会阻断这条乘积参数化的初始 gradients。

Merged weight 可以用于检验前向等价，但不能在有多个动态 adapters 时假设 merge 没有管理成本。是否选 LoRA、rank 多少，仍需结合任务与预算做实验。

### 完整参考实现

```python
import torch


class LoRALinear(torch.nn.Module):
    def __init__(self, weight, rank, alpha):
        super().__init__()
        if weight.ndim != 2 or rank < 1:
            raise ValueError("expected [out,in] weight and positive rank")
        out_features, in_features = weight.shape
        self.weight = torch.nn.Parameter(weight.detach().clone(), requires_grad=False)
        self.A = torch.nn.Parameter(
            torch.randn(rank, in_features, dtype=weight.dtype, device=weight.device)
            * 0.02
        )
        self.B = torch.nn.Parameter(
            torch.zeros(out_features, rank, dtype=weight.dtype, device=weight.device)
        )
        self.scale = alpha / rank

    def forward(self, x):
        return x @ self.weight.T + self.scale * ((x @ self.A.T) @ self.B.T)

    @torch.no_grad()
    def merged_weight(self):
        return self.weight + self.scale * (self.B @ self.A)
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
torch.manual_seed(4)
layer = LoRALinear(torch.randn(3, 5, dtype=torch.float64), rank=2, alpha=4.0)
x = torch.randn(6, 5, dtype=torch.float64)
assert torch.equal(layer(x), x @ layer.weight.T)
layer(x).square().sum().backward()
assert layer.weight.grad is None
assert layer.A.grad.eq(0).all() and layer.B.grad.abs().sum() > 0
with torch.no_grad():
    layer.B.add_(torch.randn_like(layer.B) * 0.01)
torch.testing.assert_close(
    layer(x), x @ layer.merged_weight().T, rtol=1e-12, atol=1e-12
)
assert sum(p.numel() for p in layer.parameters() if p.requires_grad) == 2 * (5 + 3)
layer.zero_grad(set_to_none=True)
with torch.no_grad():
    layer.A.zero_()
    layer.B.zero_()
layer(x).square().sum().backward()
assert layer.A.grad.eq(0).all() and layer.B.grad.eq(0).all()
print("Thinking Machines mechanism: LoRA implementation passed")
```

## 复杂度与追问

Forward update 的额外计算约 `O(B*rank*(in+out))`，额外 trainable 参数 `rank*(in+out)`。Merge 得到完整 weight matrix，空间与 base matrix 同阶。

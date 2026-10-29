---
id: code-layernorm
section: coding
order: 41
level: A
title: 手写 LayerNorm：减均值、除以 D 的方差，以及和 RMSNorm 差哪一项
quick: >-
  在最后一维上算 $\mu=\mathrm{mean}(x)$ 和 $\sigma^2=\mathrm{mean}((x-\mu)^2)$，方差除以
  $D$，对应 `unbiased=False`，再算
  $w\odot(x-\mu)/\sqrt{\sigma^2+\varepsilon}+b$。RMSNorm 少了减 $\mu$ 这一步，也没有
  $b$；Llama / Qwen 用 RMSNorm，BERT / GPT-2 用 LayerNorm。eps 常见 $10^{-5}$，统计量转到
  fp32 再算。
tags:
  - LayerNorm
  - Normalization
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28T00:00:00.000Z
sources:
  - title: Layer Normalization
    url: 'https://arxiv.org/abs/1607.06450'
    type: primary
---

## 题目描述

实现只沿最后一维 normalization 的可训练 LayerNorm，不使用运行均值或运行方差。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `LayerNorm(dim,eps=1e-5)` 及 `forward(x)`。x 为 [...,dim] 浮点张量；weight 和 bias 为长度 dim 的可训练参数，分别初始化为1和0。

### 输出与约束

对每个最后维向量使用总体方差（除 dim）normalization，再做逐元素 affine；返回同形张量。统计用 float32，normalization 结果转回输入 dtype 后应用参数。eps 加在方差内；保留梯度。

### 示例

```text
dim=2，默认参数：
x=[[1,3],[2,2]] -> 约 [[-0.999995,0.999995],[0,0]]
把weight设为2、bias设为3时，常数行[2,2]输出[3,3]。
```

## 解题思路与参考答案

LayerNorm 在最后一维上先减均值、再除以标准差，方差按 $D$ 来除，最后乘 $w$ 加 $b$。它和 `code-rmsnorm` 一般成对出现，面试官主要看四件事：沿哪个轴 normalization，有没有减均值，方差除以 $D$ 还是 $D-1$，仿射参数是不是 `[D]` 的形状。仿射参数每个特征一个，和 batch、序列长度都没关系，写成 `[B,T,D]` 就错了。

对最后一维 $x\in\mathbb{R}^{D}$：

$$
\mu=\frac1D\sum_i x_i,\quad
\sigma^2=\frac1D\sum_i(x_i-\mu)^2,\quad
y=w\odot\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}}+b.
$$

方差这里对应 `unbiased=False`，PyTorch 的 `F.layer_norm` 默认就是除以 $D$。顺手写成 `x.var(unbiased=True)` 的话，结果会和框架差一个 $D/(D-1)$ 的因子，单测就对不上。eps 常见取 $10^{-5}$，统计量先转到 fp32 再算：

```python
import torch
import torch.nn as nn


class LayerNorm(nn.Module):
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.bias = nn.Parameter(torch.zeros(dim))
        self.eps = eps

    def forward(self, x):
        z = x.float()
        mu = z.mean(-1, keepdim=True)
        var = z.var(-1, keepdim=True, unbiased=False)
        y = (z - mu) * torch.rsqrt(var + self.eps)
        return y.to(x.dtype) * self.weight + self.bias
```

和 RMSNorm 比，差的就是减均值这一项。RMSNorm 是 $x/\mathrm{RMS}(x)\odot w$，也没有 $b$。Llama、Qwen 用 RMSNorm，BERT、GPT-2 用 LayerNorm。Pre-Norm 结构里，LN 或 RMSNorm 放在子层前面，残差走的是没 normalization 的那条流，见 `code-decoder-block`。

normalization 别放到序列维上。那样不同 token 会进同一组统计；训练和推理的序列长度一变，统计分布也跟着变。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用 [1,3] 得到近似 [-1,1]，再用常数行检查 eps。最后改变可学习的 weight、bias，确保实现没有漏掉仿射变换。

```python
layer = LayerNorm(2)
x = torch.tensor([[1.0, 3.0], [2.0, 2.0]])
expected = torch.nn.functional.layer_norm(x, (2,), layer.weight, layer.bias, layer.eps)
torch.testing.assert_close(layer(x), expected)
with torch.no_grad():
    layer.weight.fill_(2)
    layer.bias.fill_(3)
torch.testing.assert_close(layer(torch.zeros(1, 2)), torch.full((1, 2), 3.0))
print("simple tests passed")
```

## 追问

**为什么沿最后一维 normalization？**
hidden 维是特征维。按 batch 或时间维统计的话，推理时的统计量和训练时对不上。

**fp16 输入为什么先转 fp32？**
平方和在低精度下容易丢小数，也容易溢出。

**去掉 bias 还叫 LayerNorm 吗？**
叫，有的实现就只留 $w$、不要 $b$。它和 RMSNorm 之间仍然差一个减均值。

---
id: ml101-conv-backward
section: neural-networks
order: 12
level: A
title: 不用 autograd，实现二维卷积的 forward 和 backward
quick: 前向在输入局部窗口与卷积核之间做内积；反向把每个输出的上游梯度分给对应窗口和卷积核。重叠窗口对同一个输入、共享核的多次使用，都必须累加梯度。参考实现支持 NCHW、多输入输出通道、整数 stride 和对称零填充，采用深度学习中常见的不翻核互相关约定。
tags: [ML Fundamentals, Backpropagation, Coding]
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23
sources:
  - title: Stanford CS231n, Convolutional networks
    url: https://cs231n.github.io/convolutional-networks/
    type: primary
  - title: PyTorch Conv2d, cross-correlation and output shape
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

不用 autograd 实现二维卷积的前向与反向，支持多个样本和多个输入、输出通道。

### 输入与接口

实现 `conv2d_forward`(X,kernels,bias,*,stride=1,padding=0) 与 `conv2d_backward`(upstream,cache)。X 为 N×Cin×H×W，kernels 为 Cout×Cin×Kh×Kw，bias 为 Cout 维；维度均为正，元素有限。stride=s为正整数，padding=p为非负整数；零填充后的输入须至少容纳一个核窗口。

### 输出与约束

前向采用深度学习常用的不翻核互相关：每个输出是对应窗口与该输出通道核的元素乘积之和，再加该通道偏置。输出高 floor((H+2p-Kh)/s)+1，宽同理，边缘不能容纳完整窗口的部分舍弃。不支持 dilation 或 groups。

forward 返回 (output,cache)，output 为 N×Cout×Hout×Wout；backward 接收同形上游梯度，返回 (dx,dkernels,dbias)，分别与原输入、核、偏置同形。共享核、多个通道及重叠窗口的梯度贡献都须累加；padding 的梯度裁剪后只返回原输入范围。不修改原参数或输入。

### 示例

```text
X=[[[[1,2,3],[4,5,6],[7,8,9]]]]
kernels=[[[[1,0],[0,-1]]]]，bias=[0]，stride=1，padding=0
output -> [[[[-4,-4],[-4,-4]]]]
upstream 全为1时：
dkernels -> [[[[12,16],[24,28]]]]，dbias -> [4]
dx -> [[[[1,1,0],[1,0,-1],[0,-1,-1]]]]
```

## 解题思路与参考答案

可以先用循环实现局部窗口内积，再沿同样的索引计算反向。这样能清楚看到共享参数和重叠窗口的梯度应该加到哪里，之后再考虑向量化。

本练习输入 X 为 N×Cin×H×W，核 K 为 Cout×Cin×Kh×Kw，偏置为 Cout。stride 是正整数 s，padding 为非负整数 p，不支持 dilation 或 groups。前向不翻转核，采用互相关；输出高为 $\lfloor(H+2p-K_h)/s\rfloor+1$，宽同理，不要求窗口恰好整除。

每个输出 $y_{nfij}$ 是对应输入窗口和第 f 个核的内积，再加偏置。设其上游梯度为 g，这个位置贡献 $g\times\text{输入窗口}$ 给核梯度，贡献 $g\times\text{核}$ 给输入窗口梯度。偏置梯度是同一输出通道上所有 g 的和。

```python
import numpy as np


def conv2d_forward(X, kernels, bias, *, stride=1, padding=0):
    X, kernels, bias = [np.asarray(v, dtype=float) for v in (X, kernels, bias)]
    if X.ndim != 4 or kernels.ndim != 4 or min(X.shape) == 0 or min(kernels.shape) == 0:
        raise ValueError("X and kernels must be nonempty 4D arrays")
    n, channels, h, w = X.shape
    filters, kernel_channels, kh, kw = kernels.shape
    if channels != kernel_channels or bias.shape != (filters,):
        raise ValueError("channel or bias dimensions do not match")
    if type(stride) is not int or stride < 1 or type(padding) is not int or padding < 0:
        raise ValueError("invalid stride or padding")
    if not all(np.isfinite(v).all() for v in (X, kernels, bias)):
        raise ValueError("inputs must be finite")
    oh = (h + 2 * padding - kh) // stride + 1
    ow = (w + 2 * padding - kw) // stride + 1
    if oh < 1 or ow < 1:
        raise ValueError("kernel is too large")
    padded = np.pad(X, ((0, 0), (0, 0), (padding, padding), (padding, padding)))
    output = np.zeros((n, filters, oh, ow))
    for sample in range(n):
        for f in range(filters):
            for i in range(oh):
                for j in range(ow):
                    r, c = i * stride, j * stride
                    patch = padded[sample, :, r:r+kh, c:c+kw]
                    output[sample, f, i, j] = np.sum(patch * kernels[f]) + bias[f]
    cache = (X.shape, padded, kernels.copy(), stride, padding, output.shape)
    return output, cache


def conv2d_backward(upstream, cache):
    shape, padded, kernels, stride, padding, output_shape = cache
    g = np.asarray(upstream, dtype=float)
    if g.shape != output_shape or not np.isfinite(g).all():
        raise ValueError("gradient must match output")
    n, filters, oh, ow = output_shape
    kh, kw = kernels.shape[2:]
    dx_padded = np.zeros_like(padded)
    dk = np.zeros_like(kernels)
    db = g.sum(axis=(0, 2, 3))
    for sample in range(n):
        for f in range(filters):
            for i in range(oh):
                for j in range(ow):
                    r, c = i * stride, j * stride
                    value = g[sample, f, i, j]
                    patch = padded[sample, :, r:r+kh, c:c+kw]
                    dk[f] += value * patch
                    dx_padded[sample, :, r:r+kh, c:c+kw] += value * kernels[f]
    h, w = shape[2:]
    dx = dx_padded[:, :, padding:padding+h, padding:padding+w]
    return dx, dk, db
```

例如输入是 1 到 9 按行排成的 3×3 图像，单通道核为 [[1,0],[0,−1]]，偏置为零，stride=1、padding=0。四个输出都是 −4。若上游梯度全为 1，偏置梯度是 4，核梯度为 [[12,16],[24,28]]；这些数分别是四个窗口在对应位置的输入之和。

计算量约为 $O(NC_{out}H_{out}W_{out}C_{in}K_hK_w)$，反向同阶。缓存主要是填充后的输入、核和形状，额外梯度数组与对应参数／输入同量级；代码没有保存所有窗口矩阵。实际高性能实现会用专门卷积内核，本题优先验证索引与梯度。

**为什么输入梯度要用 +=？**
一个输入像素可能同时出现在多个窗口，也可能被多个输出通道使用。链式法则要求把所有路径的贡献相加；赋值会把之前窗口或通道的贡献覆盖掉。核梯度也需要跨样本与空间位置累加。

**padding=0 为什么也单独检查？**
如果裁剪写成 `padding:-padding`，零填充时会变成 `0:0`，得到空数组。这里用原始高度与宽度构造终点，零填充和非零填充都能返回正确形状。

**怎样验证反向？**
用输出与任意上游梯度的内积做标量目标，对 X、核与偏置逐坐标差分。至少覆盖多个通道、重叠窗口、stride>1、非零 padding 和输出尺寸向下取整的情况。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

3×3 输入与对角差分核的每个输出都是 -4。反传全 1 时，核梯度是对应窗口求和；输入梯度重叠位置必须累加。

```python
import numpy as np
X = np.arange(1, 10, dtype=float).reshape(1, 1, 3, 3)
K = np.array([[[[1., 0.], [0., -1.]]]])
out, cache = conv2d_forward(X, K, [0])
np.testing.assert_allclose(out, -4)
dx, dk, db = conv2d_backward(np.ones_like(out), cache)
np.testing.assert_allclose(dk, [[[[12, 16], [24, 28]]]])
np.testing.assert_allclose(dx, [[[[1, 1, 0], [1, 0, -1], [0, -1, -1]]]])
np.testing.assert_allclose(db, [4])
print("simple tests passed")
```

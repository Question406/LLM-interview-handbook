---
id: meta-conv2d-from-scratch
section: meta
order: 900
level: A
title: "Meta ML Coding：从零实现 batched 2D convolution"
quick: "我会先算输出 shape，再取每个位置对应的输入 patch。每个输出 channel 都要和全部输入 channels 做乘加，所以不能只在空间维求和。"
companies:
  - meta
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人自述：Meta AI Coding Interview"
    url: "https://www.reddit.com/r/leetcode/comments/1reuwrd/meta_ai_coding_interview/"
    type: interview
  - title: "PyTorch conv2d cross-correlation convention"
    url: "https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.conv2d.html"
    type: primary
---

## 题目描述

来源：2026-02 的 Reddit 候选人更新提到手写 simple 2D convolution。下面将该方向整理成支持 batch、多通道、stride 与 padding 的独立练习，接口和测试由手册设定。

### 输入、接口与规则

实现 `conv2d_reference(x, weight, bias=None, stride=1, padding=0)`。输入 x 为 floating NumPy-compatible `[B,Cin,H,W]`，weight 为 `[Cout,Cin,Kh,Kw]`；各维为正，bias 为 None 或 `[Cout]`。stride 是正整数，padding 是非负整数，两个空间轴使用相同值；kernel 在 padding 后的输入上至少能放一次。

返回 float64 `[B,Cout,Hout,Wout]`，其中 `Hout=(H+2*padding-Kh)//stride+1`，W 类似。计算 cross-correlation：不翻转 kernel，padding 填零，每个输出累加全部输入 channels 与 kernel 空间位置，再加 bias。不修改输入。只要求 forward；不要求 groups、dilation 或 backward。不能调用现成 conv2d 实现求答案，测试中可用 PyTorch 作独立参考。

### 输入输出示例

```text
x=[[[[1,2,3],[4,5,6],[7,8,9]]]], weight=全 1 的 [1,1,2,2]，stride=1，padding=0。
返回 [[[[12,16],[24,28]]]]。
```

## 回答思路

> **输入与任务：** 明确 NCHW、kernel shape 和输出尺寸，算清一个 2×2 patch。  
> **做法与原因：** 按输出空间取 patch，累加 channels 与 kernel；批量 B 与 Cout 用 einsum。  
> **正确性检查：** 先手算，再与 PyTorch 比较不同 channels、非方形 kernel、stride 和 padding。

## 解题思路与参考答案

我会先算输出 shape，再取每个位置对应的输入 patch。每个输出 channel 都要和全部输入 channels 做乘加，所以不能只在空间维求和。

这里采用 PyTorch 常用的 cross-correlation 约定，不翻转 kernel。先写清楚的 reference，再讨论 im2col 或更快的 kernel，避免优化掩盖 shape 错误。

### 完整参考实现

```python
import numpy as np


def conv2d_reference(x, weight, bias=None, stride=1, padding=0):
    x = np.asarray(x, dtype=np.float64)
    weight = np.asarray(weight, dtype=np.float64)
    batch, channels, height, width = x.shape
    outputs, cin, kh, kw = weight.shape
    if cin != channels or stride < 1 or padding < 0:
        raise ValueError("incompatible dimensions or stride/padding")
    oh = (height + 2 * padding - kh) // stride + 1
    ow = (width + 2 * padding - kw) // stride + 1
    if min(oh, ow) < 1:
        raise ValueError("kernel does not fit")
    padded = np.pad(x, ((0, 0), (0, 0), (padding, padding), (padding, padding)))
    out = np.empty((batch, outputs, oh, ow), dtype=np.float64)
    for row in range(oh):
        for col in range(ow):
            patch = padded[
                :, :, row * stride : row * stride + kh, col * stride : col * stride + kw
            ]
            out[:, :, row, col] = np.einsum("nchw,ochw->no", patch, weight)
    if bias is not None:
        out += np.asarray(bias, dtype=np.float64)[None, :, None, None]
    return out
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
import torch
import torch.nn.functional as F

x = np.arange(1, 10).reshape(1, 1, 3, 3)
w = np.ones((1, 1, 2, 2))
assert conv2d_reference(x, w).tolist() == [[[[12.0, 16.0], [24.0, 28.0]]]]
rng = np.random.default_rng(41)
for stride, pad in [(1, 0), (2, 1), (1, 2)]:
    x = rng.normal(size=(2, 3, 5, 6))
    w = rng.normal(size=(4, 3, 2, 3))
    bias = rng.normal(size=4)
    original = x.copy()
    got = conv2d_reference(x, w, bias, stride, pad)
    expected = F.conv2d(
        torch.tensor(x), torch.tensor(w), torch.tensor(bias), stride=stride, padding=pad
    ).numpy()
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)
    assert np.array_equal(x, original)
print("Meta conv2d: passed")
```

## 复杂度与追问

时间约为 `O(B*Cout*Hout*Wout*Cin*Kh*Kw)`；输出与 padding buffer 另占空间。追问 backward 时，应分别说明 input、weight 和 bias 的 gradients，以及 overlapping patches 的 gradient 需要相加。

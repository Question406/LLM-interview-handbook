---
id: dt-p3a-batchnorm-state
section: tech-screen
order: 83
level: A
title: Apple AIML 视频组原帖：手写 BatchNorm，并分清训练与推断状态
quick: >-
  BatchNorm 按特征聚合 batch 统计量；训练输出使用当前批的有偏方差，同时更新运行统计，推断只读运行均值方差。gamma/beta
  是可学习仿射参数，running statistics 是状态，不能混为一谈。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 一亩三分地追加第二批
  - 完整编程练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: 苹果ML Engineer VO面经，候选人原帖，Chrome核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1041756-1-1.html'
    type: interview
  - title: PyTorch BatchNorm1d variance and running statistics
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.nn.BatchNorm1d.html'
    type: primary
---

## 题目描述

### 原帖核对与练习约定

- 来源：[苹果 ML Engineer VO 面经](https://www.1point3acres.com/bbs/thread-1041756-1-1.html)，Chrome 显示 2024-01-29 16:07:11，采集日期 2026-10-26。
- 主楼及作者回复可见，作者说明为 AIML 视频组。原帖明确写到手写 Batch Normalization、与 LayerNorm 的区别和 learnable parameters；不当作 AFM data team 已确认面经。
- 原帖未给代码接口与运行统计细节。以下为**手册练习约定**：用 NumPy 实现二维 BatchNorm，方差与 momentum 约定参照 PyTorch BatchNorm1d 的常见语义，不声称原面试指定了这些细节。建议限时 25 分钟。

### 输入与接口

实现 `BatchNormState(features,eps=1e-5,momentum=0.1)` 和方法 `forward(x,training=True)`。features 为正整数，eps 为正数，momentum 在 [0,1]。x 为有限 NumPy float64 matrix `[N,features]`，训练时 N>=2，推断时 N>=1。

### 输出与约束

初始化公开数组 `gamma=ones(features)`、`beta=zeros(features)`、`running_mean=zeros(features)`、`running_var=ones(features)`。gamma/beta 可由调用方改值，不要求本题实现 optimizer 或 backpropagation。

训练时，按 batch 维计算当前均值和除以 N 的有偏方差，输出 `(x-mean)/sqrt(var+eps)*gamma+beta`；更新 running_mean 为 `(1-momentum)*旧值+momentum*批均值`，running_var 同式但使用除以 N-1 的无偏批方差。推断使用 running_mean/running_var，且不得修改它们。返回 float64 `[N,features]`，不能修改输入 x。

### 示例

```text
x=[[1,2],[3,4]]，momentum=0.5，gamma=1，beta=0
训练输出两行分别为[-1,-1]/sqrt(1+eps)、[1,1]/sqrt(1+eps)。
running_mean=[1,1.5]，running_var=[1.5,1.5]。
随后推断x=[[2,3]]，输出为[1,1.5]/sqrt(1.5+eps)。
```

## 解题思路与参考答案

先分训练与推断，再做公共仿射变换。训练 normalization 的方差与运行方差估计不同，不能看到两个 `var` 就直接复用。推断不重新估计当前批统计量，否则同一个样本会随 batch 中其他样本改变输出。

```python
import numpy as np


class BatchNormState:
    def __init__(self, features, eps=1e-5, momentum=0.1):
        self.eps = eps
        self.momentum = momentum
        self.gamma = np.ones(features, dtype=np.float64)
        self.beta = np.zeros(features, dtype=np.float64)
        self.running_mean = np.zeros(features, dtype=np.float64)
        self.running_var = np.ones(features, dtype=np.float64)

    def forward(self, x, training=True):
        if training:
            mean = x.mean(axis=0)
            var = x.var(axis=0, ddof=0)
            unbiased_var = var * x.shape[0] / (x.shape[0] - 1)
            m = self.momentum
            self.running_mean = (1 - m) * self.running_mean + m * mean
            self.running_var = (1 - m) * self.running_var + m * unbiased_var
        else:
            mean = self.running_mean
            var = self.running_var
        return (x - mean) / np.sqrt(var + self.eps) * self.gamma + self.beta
```

每次时间为 $O(ND)$，统计与状态空间为 $O(D)$，输出为 $O(ND)$。gamma/beta 为可学习仿射参数；此处只是用 NumPy 存储它们，真实训练框架需将其注册为参数，而把运行统计注册为非 gradient 状态。

## 简单测试怎么写

实现和测试保存为 `solution.py`，运行 `python3 solution.py`，需要 NumPy。先手算两行样本的均值方差，再确认推断不更新状态，以及仿射参数确实影响结果。

```python
x = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)
original = x.copy()
bn = BatchNormState(2, momentum=0.5)
out = bn.forward(x)
assert out.shape == x.shape and out.dtype == np.float64
assert np.allclose(out, np.array([[-1.0, -1.0], [1.0, 1.0]]) / np.sqrt(1 + bn.eps))
assert np.allclose(bn.running_mean, [1.0, 1.5])
assert np.allclose(bn.running_var, [1.5, 1.5])
mean_before, var_before = bn.running_mean.copy(), bn.running_var.copy()
eval_out = bn.forward(np.array([[2.0, 3.0]]), training=False)
assert np.allclose(eval_out, np.array([[1.0, 1.5]]) / np.sqrt(1.5 + bn.eps))
assert np.array_equal(bn.running_mean, mean_before)
assert np.array_equal(bn.running_var, var_before)
bn.gamma[:] = 2
bn.beta[:] = 3
assert np.allclose(bn.forward(np.array([[2.0, 3.0]]), False), eval_out * 2 + 3)
assert np.array_equal(x, original)
constant = BatchNormState(1)
assert np.allclose(constant.forward(np.array([[7.0], [7.0]])), [[0.0], [0.0]])
```

## 面试追问

**与 LayerNorm 的区别？** 本题 BatchNorm 跨 batch 维按每个特征统计，依赖其他样本；典型 LayerNorm 在一个样本/位置内沿指定特征维统计，训练推断通常都使用当前输入统计，不需要这种运行均值方差。不能只说一个用于 CNN 一个用于 Transformer。

**eval 等于关闭 gradient 吗？** 不等于。模式决定哪些统计与随机行为生效，自动求导开关另行控制。真实 PyTorch 代码通常同时使用 eval 和 no_grad/inference_mode 做推断。

**小 batch 与多卡怎么办？** 小 batch 的统计噪声大；不同 rank 独立统计与同步统计语义不同。需要按硬件与任务选择同步 BN、冻结统计或其他 normalization，不能直接认定多卡等价大 batch。

**momentum 为 0.1 是保留 10% 旧值吗？** 按本题定义是吸收 10% 新批统计、保留 90% 旧统计，不同工具可能采用不同约定，应先核对。

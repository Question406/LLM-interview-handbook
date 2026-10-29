---
id: dt-response-logprob-code
section: tech-screen
order: 32
level: S
title: CoderPad：批量计算回答 log probability，EOS 和 padding 怎么对齐？
quick: >-
  先用前一位置 logits 预测后一 token，再按目标位置的回答 mask 选取 log probability。序列概率取 token log
  probability 的和；长度平均是另一种评分，不能无说明替换标准 DPO 的序列求和。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: PyTorch log_softmax
    url: >-
      https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.log_softmax.html
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

## 题目描述

本题为原创练习。建议限时 20 分钟。实现一个回答评分函数，用于分析 preference data 与 rejection sampling 候选。

### 输入与接口

`response_logprob(logits, input_ids, response_mask)`：logits 为有限浮点 tensor `[B,T,V]`，input_ids 为同设备 long tensor `[B,T]`，包含合法 vocabulary ID；response_mask 为同设备 bool tensor `[B,T]`，表示当前位置 token 是否属于要评分的回答。B、V 为正，T 至少为 2。允许一个样本没有回答 token。

### 输出与约束

返回 `(sums, means, counts)`，各形状 `[B]`。位置 t 的 logits 预测位置 t+1 的 ID。位置 0 没有可用的前驱 logits，即使 mask 为 True 也不计入；其余位置由 response_mask 决定。若 EOS 在 mask 中则计入，padding 必须由调用方设为 False。不修改输入，必须保留对 logits 的自动求导路径。sums 和 means 用 float32 计算，counts 为整数；无有效 token 时三项都为 0。

### 三个返回值如何计算

先在 logits 的 vocabulary 轴做 log-softmax。对真实位置 j（`1<=j<T`），取 `logits[:,j-1,:]` 中 `input_ids[:,j]` 的 log probability。每条序列只保留 `response_mask[:,j]=True` 的这些值；`sums` 是其总和，`counts` 是保留数量，`means=sums/counts`。counts 为 0 时 sums、means 均定义为 0。这里是在评分回答 token，不是在计算整个 prompt 的 likelihood。

### 示例

```text
logits=zeros([2,4,2])
input_ids=[[0,1,0,1],[1,0,1,0]]
response_mask=[[False,True,True,False],[False,False,False,False]]
sums=[-2*log(2),0]，means=[-log(2),0]，counts=[2,0]
```

## 解题思路与参考答案

先 shift，再在 vocabulary 维做 log_softmax 和 gather。mask 必须同样取目标侧的 `[:,1:]`，而不是当前 logits 侧的 mask。

```python
import torch
import torch.nn.functional as F


def response_logprob(logits, input_ids, response_mask):
    log_probs = F.log_softmax(logits[:, :-1].float(), dim=-1)
    selected = log_probs.gather(-1, input_ids[:, 1:, None]).squeeze(-1)
    mask = response_mask[:, 1:]
    counts = mask.sum(dim=-1)
    sums = selected.masked_fill(~mask, 0.0).sum(dim=-1)
    means = sums / counts.clamp_min(1)
    return sums, means, counts
```

序列概率是条件概率的乘积，所以 log probability 求和。平均 log probability 更接近每个 token 的平均可预测性，会改变长度偏好。二者用途不同。时间复杂度为 $O(BTV)$；这里保留完整 log_softmax 中间 tensor，实际大 vocabulary 评分可以分块降低峰值内存。

## 简单测试怎么写

将实现与下面测试放进 `solution.py`，运行 `python3 solution.py`。均匀分布给出手算预期值；非均匀分布用于发现 shift 错误；gradient 检查用于发现把结果转成 Python 数后重新包装的错误。

```python
import math

ids = torch.tensor([[0, 1, 0, 1], [1, 0, 1, 0]])
mask = torch.tensor([[False, True, True, False], [False, False, False, False]])
x = torch.zeros(2, 4, 2, requires_grad=True)
sums, means, counts = response_logprob(x, ids, mask)
assert sums.shape == means.shape == counts.shape == (2,)
assert torch.allclose(sums, torch.tensor([-2 * math.log(2), 0.0]))
assert torch.allclose(means, torch.tensor([-math.log(2), 0.0]))
assert counts.tolist() == [2, 0]
(-sums.sum()).backward()
assert x.grad[0, :2].abs().sum() > 0
assert torch.count_nonzero(x.grad[0, 2:]) == 0
assert torch.count_nonzero(x.grad[1]) == 0
# 第0行概率为[0.25,0.75]，用于预测位置1的 token 1。
nonuniform = torch.tensor([[[0.0, math.log(3)], [8.0, -8.0]]])
a, b, c = response_logprob(
    nonuniform, torch.tensor([[0, 1]]), torch.tensor([[True, True]])
)
assert torch.allclose(a, torch.tensor([math.log(0.75)]), atol=1e-6)
assert c.tolist() == [1]
```

## 面试追问

**为什么不先 softmax 再 log？** 很小的概率在浮点下可能下溢为 0，随后 log 变成负无穷；log_softmax 直接在 log 空间计算更稳定。

**回答和 prompt 重复的 token 要排除吗？** 不按 token 值排除。监督区域由位置和任务结构决定，同一个词既能出现在 prompt，也能出现在回答。

**能直接用这个分数选最优回答吗？** 不能把模型 confidence 当正确率。高概率可能来自重复模板，需要独立执行验证、事实核对或 calibration 后的评价信号。

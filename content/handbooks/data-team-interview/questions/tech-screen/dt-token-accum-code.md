---
id: dt-token-accum-code
section: tech-screen
order: 34
level: S
title: CoderPad：变长 microbatch gradient accumulation，为什么平均 loss 会训练错？
quick: >-
  当每个 microbatch 的有效 token 数不同，应把各批 token loss 总和除以整个累积窗口的有效 token 总数，再分别
  backward；直接平均各批均值会把短批放大。一次窗口只清 gradient 和更新一次。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: PyTorch Automatic Mixed Precision examples
    url: 'https://docs.pytorch.org/docs/2.14/notes/amp_examples.html'
    type: primary
---

## 题目描述

本题为原创训练代码练习。建议限时 25 分钟。实现 CPU、单进程、无混合精度的一次 gradient accumulation 更新。

### 输入与接口

实现 `token_accum_step(model, optimizer, microbatches)`。microbatches 为非空列表，每项为 `(x,y,valid)`：x 为 `[N,D]` 浮点 tensor，y 为 `[N]` long 类别 ID，valid 为 `[N]` bool tensor，N 至少为 1。不同批 N 可不同。所有输入为 CPU tensor，model(x) 返回 `[N,C]` logits，C 至少为 2。只对 valid=True 的位置计算 cross-entropy。

model 是无 dropout、无 batch normalization、无跨行交互的逐行分类模型，参数不依赖 batch 内其他样本。optimizer 只管理 model 参数。各批有效 token 总数可为 0。

### 输出与约束

函数对整个列表执行一次 `zero_grad`，若总有效数大于 0，逐批 forward 与 backward，最后只调用一次 optimizer.step；窗口按有效 token 总数 normalization。返回更新前的平均 token loss，类型为 Python float。总有效数为 0 时清 gradient、跳过 forward 和 optimizer.step，返回 0.0。不修改输入，不能把所有输入拼接后一次 forward。

### 示例

```text
二维零权重线性分类器，无bias，SGD学习率0.1。
批1：x=[[1,0]], y=[0], valid=[True]
批2：x=[[0,1],[0,1],[9,9]], y=[1,1,0], valid=[True,True,False]
返回log(2)；更新后weight=[[1/60,-1/30],[-1/60,1/30]]
```

## 解题思路与参考答案

全窗口目标是有效位置 loss 之和除以有效位置总数。先统计分母，每批用 sum reduction，再除同一分母 backward。这样不保留所有 microbatch 的计算图，也不会让只有一个有效 token 的批与十个 token 的批拥有相同权重。

```python
import torch
import torch.nn.functional as F


def token_accum_step(model, optimizer, microbatches):
    optimizer.zero_grad(set_to_none=True)
    total = sum(int(valid.sum()) for _, _, valid in microbatches)
    if total == 0:
        return 0.0
    model.train()
    loss_sum = 0.0
    for x, y, valid in microbatches:
        if not bool(valid.any()):
            continue
        logits = model(x)
        batch_sum = F.cross_entropy(logits[valid], y[valid], reduction="sum")
        (batch_sum / total).backward()
        loss_sum += float(batch_sum.detach())
    optimizer.step()
    return loss_sum / total
```

时间主要由逐批模型前后向决定，保存的激活规模由单个 microbatch 决定。model.train() 开启训练模式但不会冻结或清除 gradient。若加 gradient clipping，应在所有 backward 完成后、step 之前统一裁剪。

## 简单测试怎么写

将实现和下面测试保存为 `solution.py`，运行 `python3 solution.py`。零权重时每个类别概率均为 1/2，所以 loss 可手算。第二项输入的无效行不应贡献 gradient；再与独立的整批更新对照。

```python
import math

model = torch.nn.Linear(2, 2, bias=False)
with torch.no_grad():
    model.weight.zero_()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
batches = [
    (torch.tensor([[1.0, 0.0]]), torch.tensor([0]), torch.tensor([True])),
    (
        torch.tensor([[0.0, 1.0], [0.0, 1.0], [9.0, 9.0]]),
        torch.tensor([1, 1, 0]),
        torch.tensor([True, True, False]),
    ),
]
value = token_accum_step(model, optimizer, batches)
assert math.isclose(value, math.log(2), rel_tol=1e-6)
expected = torch.tensor([[1 / 60, -1 / 30], [-1 / 60, 1 / 30]])
assert torch.allclose(model.weight, expected, atol=1e-7)
# 独立对照：一次整批的均值目标。
full = torch.nn.Linear(2, 2, bias=False)
with torch.no_grad():
    full.weight.zero_()
full_optimizer = torch.optim.SGD(full.parameters(), lr=0.1)
full_optimizer.zero_grad()
F.cross_entropy(
    full(torch.tensor([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])), torch.tensor([0, 1, 1])
).backward()
full_optimizer.step()
assert torch.allclose(model.weight, full.weight, atol=1e-7)
# AdamW 的 weight decay 也会改参数，因此全空窗口必须跳过 step。
empty_optimizer = torch.optim.AdamW(model.parameters(), lr=0.1, weight_decay=0.1)
before = model.weight.detach().clone()
empty = [(torch.ones(1, 2), torch.tensor([0]), torch.tensor([False]))]
assert token_accum_step(model, empty_optimizer, empty) == 0.0
assert torch.equal(before, model.weight)
assert model.weight.grad is None
```

## 面试追问

**为什么限制 dropout 和 batch normalization？** dropout 的随机性和 batch normalization 的批统计会破坏与整批 forward 逐数值相等的假设。normalization 目标仍可正确，但不能承诺与整批完全相同。

**DDP 怎么改？** 若 DDP 默认对 W 个进程的 gradient 取平均，使用全局有效 token 数作分母时，每个进程的本地 loss 总和应乘 W 再除以全局分母。还需保证各进程集合通信顺序一致；本题跳过空批的单机逻辑不能直接搬过去。

**AMP 怎么改？** 每批缩放 normalization 后的 loss 并 backward，整个窗口结束才 unscale、裁剪、step 和更新 scaler。不能每个 microbatch 都更新 scaler。

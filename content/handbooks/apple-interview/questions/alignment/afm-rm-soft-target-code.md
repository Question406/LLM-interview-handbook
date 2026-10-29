---
id: afm-rm-soft-target-code
section: alignment
order: 130
level: S
title: 编程：soft preference BCE，如何区分投票比例与样本权重？
quick: >-
  用奖励差作为 BCE logit，q 表示偏好 A 的概率，w 单独控制样本贡献。全零权重返回可 backpropagation 零，q=0.5 在
  margin=0 处 gradient 为零。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: 'HelpSteer2-Preference: Complementing Ratings with Preferences'
    url: 'https://arxiv.org/abs/2410.01257'
    type: primary
---

## 题目描述

已有 reward model 分别给同一 prompt 的回答 A、B 打分。人工提供偏好 A 的投票比例，另外提供每条 pair 的 confidence weight。请计算这批 pairs 的 weighted soft-preference loss，保留对 reward scores 的 gradients。

本题只计算 loss，不训练模型或划分数据。以下接口和数值规则为原创练习约定。

### 接口与输入含义

实现 `soft_preference_loss(a, b, q, w)`。四个参数均为同设备的浮点 PyTorch tensor，shape 均为 `[B]`，`B>=1`；设备可以是 CPU 或 CUDA。

| 参数 | 每个元素的含义 | 有效范围 |
| --- | --- | --- |
| `a[i]`、`b[i]` | 第 i 个 prompt 下 A、B 的 scalar reward scores，不是特征或 token IDs | 有限且绝对值不超过 10000 |
| `q[i]` | 人工投票中偏好 A 的比例；如四人中三人选 A，则为 0.75 | `[0,1]` |
| `w[i]` | 该 pair 的 confidence weight，用来控制这条样本对总 loss 的贡献 | 非负有限值，允许全部为 0 |

`q`、`w` 是固定监督数据，即使它们设置了 `requires_grad=True`，本函数也不能向它们传播 gradients。不得修改任何输入。

### 输出与计算规则

令 `d=a-b`，对第 i 条定义：

$$\ell_i=-q_i\log\sigma(d_i)-(1-q_i)\log(1-\sigma(d_i)).$$

返回 float32 scalar tensor：当权重和为正时，`loss=sum(w*ell)/sum(w)`；权重和为 0 时返回可调用 backward 的 0，并且 `a`、`b` 的 gradients 均为 0。

使用稳定的 logits-based BCE，避免先算 sigmoid 再取 log。`q=0.5` 仍参与 loss；不能把 q 当作 sample weight，也不能将 soft targets 先转成 hard labels。本题不要求验证输入是否合法。

### 完整输入输出示例

```text
a=[0.0], b=[0.0], q=[0.6], w=[0.2]
返回 loss=log(2)，约 0.69314718。
调用 loss.backward() 后：a.grad=[-0.1]，b.grad=[0.1]；q.grad、w.grad 均为 None。
```

这里只有一条 pair，分子、分母中的 0.2 抵消，因此 gradient 不是 -0.02。

```text
a=[2.0,-2.0], b=[0.0,0.0], q=[1.0,0.0], w=[0.0,0.0]
返回 loss=0；backward 后 a.grad=b.grad=[0.0,0.0]。
```

正常数值比较使用 `atol=1e-6,rtol=1e-6`。

## 解题思路与参考答案

稳定的 BCEWithLogits 同时保留两个方向的监督。单样本 gradient 为 sigmoid(a-b)−q；它与 weight=q 的硬 chosen 损失不同。这里只定义训练目标，不能据此声称投票比例估计没有 sampling 偏差。

```python
import torch
import torch.nn.functional as F


def soft_preference_loss(a, b, q, w):
    weight = w.detach().float()
    per = F.binary_cross_entropy_with_logits(
        a.float() - b.float(), q.detach().float(), reduction="none"
    )
    denominator = weight.sum()
    safe = torch.where(denominator > 0, denominator, torch.ones_like(denominator))
    return (per * weight).sum() / safe
```

## 简单测试怎么写

将实现和下面测试放入 solution.py，在安装了 PyTorch 的环境运行。检查手算 loss 与 gradient、soft target、q/w 无 gradient、全零权重和极端 reward scores；本题不涉及训练/验证划分。

```python
import math

x = torch.tensor([0.0], requires_grad=True)
y = torch.tensor([0.0], requires_grad=True)
q = torch.tensor([0.6], requires_grad=True)
w = torch.tensor([0.2], requires_grad=True)
l = soft_preference_loss(x, y, q, w)
assert math.isclose(l.item(), math.log(2), rel_tol=1e-6)
l.backward()
assert torch.allclose(x.grad, torch.tensor([-0.1]), atol=1e-6)
assert torch.allclose(y.grad, torch.tensor([0.1]), atol=1e-6)
assert q.grad is None and w.grad is None
p = torch.tensor([0.0], requires_grad=True)
soft_preference_loss(p, torch.zeros(1), torch.tensor([0.5]), torch.ones(1)).backward()
assert p.grad.item() == 0
z = torch.tensor([5.0, -5.0], requires_grad=True)
l = soft_preference_loss(z, torch.zeros(2), torch.tensor([1.0, 0.0]), torch.zeros(2))
l.backward()
assert l.item() == 0 and torch.equal(z.grad, torch.zeros(2))
a = torch.tensor([10000.0, -10000.0])
b = -a
assert torch.isfinite(
    soft_preference_loss(a, b, torch.tensor([0.0, 1.0]), torch.ones(2))
)
assert torch.allclose(
    soft_preference_loss(a, b, torch.tensor([0.3, 0.7]), torch.ones(2)),
    soft_preference_loss(b, a, torch.tensor([0.7, 0.3]), torch.ones(2)),
    rtol=1e-6,
)
```

## 面试追问

说明如何把当前内存内实现扩到数据流、哪些统计只在 training set 拟合、怎样版本化标签与输入。不要把 CPU 小样本的收益当成 large model 结论。

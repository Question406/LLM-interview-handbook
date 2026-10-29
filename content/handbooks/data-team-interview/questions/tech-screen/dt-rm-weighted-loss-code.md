---
id: dt-rm-weighted-loss-code
section: tech-screen
order: 45
level: S
title: CoderPad：实现带 confidence weight 的 pairwise reward loss，全零权重怎么 backpropagation？
quick: >-
  对 chosen 与 rejected 奖励差使用 softplus，再按 confidence weight
  normalization。分母是权重总和，不是样本数；全零权重时返回仍连着计算图的零，使 backward 有定义但 gradient 为零。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 题目描述

原创练习；建议限时 20 分钟。人工 preference pairs 有不同 confidence，请实现 reward model 的加权 pairwise loss。

### 输入与接口

`weighted_reward_loss(chosen, rejected, weights)`：三个同设备浮点 tensor 形状均为 `[B]`，B 为正。chosen/rejected 为奖励分数，绝对值不超过 10000；weights 在 `[0,1]`，表示监督 confidence weight，不是 preference probability。允许全部为 0。

### 输出与约束

每对损失为 `-log(sigmoid(chosen-rejected))`，返回按 weights 加权的均值，float32 标量 tensor。weights 作为固定数据，不应收到 gradient；chosen/rejected 保持 differentiable。权重和为 0 时返回可 backward 的零，且奖励 gradient 为零。不得修改输入，避免先 sigmoid 再 log。

### 示例

```text
chosen=[0,1], rejected=[0,0], weights=[1,0]
返回log(2)。第二对不贡献梯度。
```

## 解题思路与参考答案

负 log-sigmoid 等于 softplus 的负 margin 形式。使用固定权重，分母只有全零时替换成 1，不能用 clamp_min(1)，因为合法权重总和可能为 0.2。

```python
import torch
import torch.nn.functional as F


def weighted_reward_loss(chosen, rejected, weights):
    weight = weights.float().detach()
    per_pair = F.softplus(rejected.float() - chosen.float())
    denominator = weight.sum()
    safe_denominator = torch.where(
        denominator > 0, denominator, torch.ones_like(denominator)
    )
    return (per_pair * weight).sum() / safe_denominator
```

时间与空间为 $O(B)$。全零时仍对依赖奖励的表达式求和，gradient 为零，不是新建一个不连计算图的 `torch.tensor(0.)`。本题只保证 loss gradient；训练循环如果调用带 weight decay 的 optimizer，参数仍可能改变，应单独处理跳过更新。

## 简单测试怎么写

实现和测试放入 `solution.py`，运行 `python3 solution.py`，需要 PyTorch。检查手算均匀 margin、屏蔽项 gradient、小于 1 的权重分母与极端 margin。

```python
import math

chosen = torch.tensor([0.0, 1.0], requires_grad=True)
rejected = torch.tensor([0.0, 0.0], requires_grad=True)
weights = torch.tensor([1.0, 0.0], requires_grad=True)
loss = weighted_reward_loss(chosen, rejected, weights)
assert math.isclose(loss.item(), math.log(2), rel_tol=1e-6)
loss.backward()
assert torch.allclose(chosen.grad, torch.tensor([-0.5, 0.0]))
assert torch.allclose(rejected.grad, torch.tensor([0.5, 0.0]))
assert weights.grad is None
small = weighted_reward_loss(torch.zeros(1), torch.zeros(1), torch.tensor([0.2]))
assert math.isclose(small.item(), math.log(2), rel_tol=1e-6)
z = torch.tensor([2.0], requires_grad=True)
empty = weighted_reward_loss(z, torch.zeros(1), torch.zeros(1))
empty.backward()
assert empty.item() == 0.0 and z.grad.item() == 0.0
extreme = weighted_reward_loss(
    torch.tensor([-10000.0]), torch.tensor([10000.0]), torch.ones(1)
)
assert torch.isfinite(extreme) and extreme.item() == 20000.0
```

## 面试追问

**0.6 的 preference probability 能直接当权重吗？** 不能混淆。confidence weight 只缩放 hard labels 损失；preference probability 意味着 soft target，损失应同时考虑两种偏好方向。

**为什么加一个常数后 loss 不变？** 此目标只看奖励差，绝对奖励尺度与偏移需要额外 calibration 或约束。不能把其输出直接解释成任务成功概率。

**分歧大的 preference pairs 全删掉好吗？** 不一定。先判断歧义、标注失误与合法偏好多样性，按目标考虑 soft labels、分维度评价或 re-annotation，而不是只保留简单共识题。

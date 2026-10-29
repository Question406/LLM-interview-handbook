---
id: dt-dpo-batch-code
section: tech-screen
order: 33
level: S
title: CoderPad：实现带 reference policy 的 DPO loss，并验证 gradient 方向
quick: >-
  DPO 比较策略与 reference policy 对 chosen/rejected 的序列 log probability 差，用稳定的负
  log-sigmoid 求 loss。参考分数不应收到 gradient；当两组相对差相同时 loss 为 log(2)。
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
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: PyTorch log_softmax
    url: >-
      https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.log_softmax.html
    type: primary
---

## 题目描述

本题是根据 DPO 论文设计的原创实现练习。建议限时 20 分钟。上一道回答评分题负责从 token logits 得到序列 log probability，本题直接接收序列分数。

### 输入与接口

实现 `dpo_batch_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta)`。前四项为形状 `[B]` 的有限浮点 tensor，设备相同，B 为正；beta 为正标量。分数均为回答 token 的 log probability 总和，已由调用方完成 mask 与 shift。

### 输出与约束

返回标量 tensor，计算每对的标准 DPO loss 再对 B 取平均。参考分数作为固定常量，即使输入有 requires_grad 也不能获得 gradient。对策略分数保留 gradient；使用 float32 计算，不修改输入。禁止用先 sigmoid 再 log 的不稳定形式。

### 数据含义与完整 objective

每个下标对应同一个 prompt 的 chosen / rejected 回答；policy 分数来自当前可训练模型，ref 分数来自固定 reference policy。令 `margin=(policy_chosen-policy_rejected)-(ref_chosen-ref_rejected)`，单条 loss 为 `-log(sigmoid(beta*margin))`，返回所有 B 条的算术平均。不得把 chosen/rejected 分别当两个独立任务，也不额外加 KL penalty。

### 示例

```text
policy_chosen=[-2], policy_rejected=[-3]
ref_chosen=[-4], ref_rejected=[-5], beta=0.1
策略和参考的差都为1，loss=log(2)
```

## 解题思路与参考答案

定义策略的 chosen/rejected 差为 $\Delta_\theta$，参考差为 $\Delta_{\rm ref}$，每对损失为：

$$\ell=-\log\sigma\bigl(\beta(\Delta_\theta-\Delta_{\rm ref})\bigr).$$

它鼓励策略相对于参考更偏好 chosen。这里输入的是 log probability，不能再对这些分数做一次 softmax。

```python
import torch
import torch.nn.functional as F


def dpo_batch_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta):
    policy_margin = policy_chosen.float() - policy_rejected.float()
    reference_margin = (ref_chosen.float() - ref_rejected.float()).detach()
    return -F.logsigmoid(beta * (policy_margin - reference_margin)).mean()
```

时间和额外空间都为 $O(B)$，不包括上游模型 forward。gradient 下降时，单独看本题输入变量，应提高 chosen 的 log probability、降低 rejected 的 log probability。实际模型 parameter sharing，更新后仍需评测其他样本。

## 简单测试怎么写

把实现和测试放进 `solution.py`，运行 `python3 solution.py`。检查相等差值、gradient 方向与参考冻结，再检查极端分数下的稳定性。

```python
import math

pc = torch.tensor([-2.0], requires_grad=True)
pr = torch.tensor([-3.0], requires_grad=True)
rc = torch.tensor([-4.0], requires_grad=True)
rr = torch.tensor([-5.0], requires_grad=True)
loss = dpo_batch_loss(pc, pr, rc, rr, 0.1)
assert loss.ndim == 0
assert math.isclose(loss.item(), math.log(2), rel_tol=1e-6)
loss.backward()
assert torch.allclose(pc.grad, torch.tensor([-0.05]))
assert torch.allclose(pr.grad, torch.tensor([0.05]))
assert rc.grad is None and rr.grad is None
better = dpo_batch_loss(torch.tensor([-1.0]), torch.tensor([-3.0]), rc, rr, 0.1)
assert better < loss.detach()
extreme = dpo_batch_loss(
    torch.tensor([-10000.0, 0.0]),
    torch.tensor([0.0, -10000.0]),
    torch.zeros(2),
    torch.zeros(2),
    1.0,
)
assert torch.isfinite(extreme)
assert torch.allclose(extreme, torch.tensor(5000.0))
```

## 面试追问

**chosen 更长怎么办？** 标准 DPO 用序列 log probability 总和，不能不说明地改成均值。先按长度差 evaluation slices 评测、检查标签是否偏爱冗长，再设计长度受控 preference pairs；若改目标，应作为另一个算法变体验证。

**beta 大小怎么解释？** 在 DPO 推导对应的奖励优化目标里，beta 是相对 reference policy 的 KL 惩罚系数；在这个固定 batch 的 loss 中，它也直接缩放 margin 和 gradient。不能简单说 beta 越大，策略一定偏离越远。

**loss 降了说明更好吗？** 只说明当前偏好目标更容易被满足。还需要独立 human evaluation、真实性和安全检查，并对照长度与分布变化。

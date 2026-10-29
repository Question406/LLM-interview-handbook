---
id: dt-distill-forward-kl-code
section: tech-screen
order: 46
level: S
title: >-
  CoderPad：手写 temperature-scaled distillation KL，teacher、student 和 reduction
  哪个方向？
quick: >-
  本题用 teacher 分布到 student 分布的 forward KL，在 vocabulary 维求和，再按有效 token
  平均并乘温度平方。teacher 必须冻结，不能把 KL 的输入顺序或对 vocabulary 的平均与 token 平均混淆。
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
  - title: PyTorch kl_div
    url: >-
      https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.kl_div.html
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

原创练习；建议限时 25 分钟。给已对齐的 teacher 与 student logits，计算仅在指定位置生效的 distillation 目标，本题不执行 token shift。

### 输入与接口

`distill_forward_kl(student_logits, teacher_logits, valid, temperature=1.0)`：前两项为 `[B,T,V]` 同设备浮点 tensor，logits 绝对值不超过 10000；valid 为 `[B,T]` bool tensor。B、T、V 为正，温度为正常范围的正浮点数。允许 valid 全 False。

### 输出与约束

令 p 为 teacher logits 除以温度后的 softmax，q 为 student 对应分布。每个 token 的 KL 为 `sum_v p_v*(log(p_v)-log(q_v))`。返回有效 token 的平均 KL 乘温度平方，float32 标量；无有效 token 时返回 differentiable 的零。teacher 不得获得 gradient，student 需要 gradient；不得修改输入。

### 示例

```text
teacher_logits=[[[log(3),0]]], student_logits=[[[0,0]]], valid=[[True]]
temperature=1
p=[0.75,0.25], q=[0.5,0.5]
loss=0.75*log(1.5)+0.25*log(0.5)，约0.130812
```

## 解题思路与参考答案

直接在 log 空间形成两个分布，teacher 断开 gradient。先求 vocabulary 维总和，再在有效 token 上平均，避免默认 reduction 把分母额外乘 vocabulary 大小。

```python
import torch
import torch.nn.functional as F


def distill_forward_kl(student_logits, teacher_logits, valid, temperature=1.0):
    student_logp = F.log_softmax(student_logits.float() / temperature, dim=-1)
    teacher_logp = F.log_softmax(teacher_logits.detach().float() / temperature, dim=-1)
    per_token = (teacher_logp.exp() * (teacher_logp - student_logp)).sum(dim=-1)
    loss = per_token.masked_fill(~valid, 0.0).sum() / valid.sum().clamp_min(1)
    return loss * temperature**2
```

时间和中间 tensor 空间为 $O(BTV)$。有限精度下 KL 可能有极小负误差，不宜强行 clamp 并掩盖数值或实现问题，应使用合理容差。此题假设 vocabulary、tokenization 与位置完全对齐；teacher 和 student vocabulary 不同时不能直接逐 token 做 KL。

## 简单测试怎么写

保存代码与测试为 `solution.py`，运行 `python3 solution.py`。使用二类分布手算 KL，检查 teacher 无 gradient 和被 mask 位置无 gradient，并用非 1 温度验证缩放。

```python
import math

s = torch.zeros(1, 2, 2, requires_grad=True)
t = torch.tensor([[[math.log(3), 0.0], [0.0, 9.0]]], requires_grad=True)
valid = torch.tensor([[True, False]])
loss = distill_forward_kl(s, t, valid)
expected = 0.75 * math.log(1.5) + 0.25 * math.log(0.5)
assert math.isclose(loss.item(), expected, abs_tol=1e-6)
loss.backward()
assert t.grad is None
assert torch.allclose(s.grad[0, 0], torch.tensor([-0.25, 0.25]), atol=1e-6)
assert torch.count_nonzero(s.grad[0, 1]) == 0
same = distill_forward_kl(t.detach(), t.detach(), torch.ones(1, 2, dtype=torch.bool))
assert abs(same.item()) < 1e-6
z = torch.zeros(1, 1, 2, requires_grad=True)
zero = distill_forward_kl(z, torch.ones_like(z), torch.tensor([[False]]))
zero.backward()
assert zero.item() == 0.0 and torch.count_nonzero(z.grad) == 0
# 温度为2，教师原logits乘2，软分布仍为[0.75,0.25]，再乘T平方。
hot = distill_forward_kl(
    torch.zeros(1, 1, 2),
    torch.tensor([[[2 * math.log(3), 0.0]]]),
    torch.tensor([[True]]),
    2.0,
)
assert math.isclose(hot.item(), 4 * expected, abs_tol=1e-6)
```

## 面试追问

**reverse KL 会一样吗？** 不一样。reverse KL 对覆盖不同模式的激励不同，且要重新检查 teacher/student 各自分布在权重中的角色，不能只交换函数参数名。

**温度平方总是必须吗？** 这是本题目标约定，常用于补偿温度对 gradient 尺度的影响。是否使用、如何与 hard labels loss 混合，需要写清配方并实验。

**teacher 越强，student 收益越大吗？** 不保证。任务覆盖、解释长度、student 容量和 token 对齐都可能限制收益；用 student 的独立迁移结果选数据。

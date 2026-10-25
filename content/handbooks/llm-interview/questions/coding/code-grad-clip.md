---
id: code-grad-clip
section: coding
order: 43
level: A
title: 手写 global-norm 梯度裁剪：总 L2、缩放系数、遇到 inf/nan 怎么办
quick: "把所有参数梯度的 L2 合成一个标量 $n=\\sqrt{\\sum\\|g_i\\|_2^2}$，$n>\\texttt{max\\_norm}$ 时每个梯度都乘 $\\texttt{max\\_norm}/(n+\\varepsilon)$，否则不动。$n$ 不是有限值就把梯度清零、跳过这一步，别拿 NaN 去做除法。AMP 下必须先 unscale 再量 $n$。"
tags:
  - GradClip
  - Training
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5063
    type: primary
---

## 题目描述

实现对一组模型参数梯度的全局 L2 范数裁剪，而不是分别裁剪每个参数。参数的 `.grad` 可能为 None，没有梯度的参数不参与计算。

### 接口与结果

`clip_grad_norm_(params,max_norm)` 接收可遍历的 PyTorch 参数和正数阈值，返回裁剪前所有有效梯度合在一起的 L2 范数，并原地修改超限梯度，使它们使用同一个缩放比例、裁剪后总范数不超过阈值。范数没有超限时保留原梯度；没有任何梯度时返回数值为 0 的张量。

本卡对有限梯度进行面试验证，不要求额外处理 NaN 或 infinity；参考实现附带的防御逻辑不属于默认练习要求。

### 示例

```text
两个标量参数的梯度分别为[3]和[4]，max_norm=1
返回的裁剪前总范数 -> 5
调用后梯度约为[0.6]和[0.8]
params为空 -> 返回0
```

浮点结果按容差比较，不能因为微小舍入误差判错。

## 解题思路与参考答案

Global-norm 梯度裁剪是把所有参数的梯度当成一个大向量，算一个总的 L2 范数 $n$；$n$ 超过 `max_norm` 时，所有梯度共用同一个系数 $\texttt{max\_norm}/(n+\varepsilon)$ 缩小，没超过就不动。$n$ 是 inf 或 nan 的话，就把梯度清零、跳过这一步。Llama 常见的设置是 `max_grad_norm=1.0`。

这题面试常和 AMP 连着问。容易写错成两种：按参数各自 clip，那是 clip-by-value 或者 per-tensor 裁剪；或者先 clip 再 unscale，阈值和真实的 $n$ 差了一个 scale。

## 总范数

$$
n=\Big(\sum_{p\in\theta}\|g_p\|_2^2\Big)^{1/2},\qquad
g_p\leftarrow g_p\cdot\min\Big(1,\frac{\texttt{max\_norm}}{n+\varepsilon}\Big).
$$

$n$ 是一个标量，所有张量共用一个系数。先 `stack` 各张量自己的 `norm`，再对外面做一次 `norm`，结果和把全部元素 flatten 之后算 norm 一样。

```python
import torch

def clip_grad_norm_(params, max_norm):
    grads = [p.grad for p in params if p.grad is not None]
    if not grads:
        return torch.tensor(0.0)
    total = torch.norm(torch.stack([g.detach().float().norm(2) for g in grads]), 2)
    if not torch.isfinite(total):
        for g in grads:
            g.zero_()
        return total
    scale = (max_norm / (total + 1e-6)).clamp(max=1.0)
    for g in grads:
        g.mul_(scale)
    return total
```

$n$ 不是有限值时清梯度，是为了这一步的 Adam 状态不被 inf 写脏。AMP 下的顺序是先 `unscale_`，再 clip，再看有没有 inf，决定要不要 `step`、要不要降 scale，见 `code-grad-accum-amp`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两组梯度分别为 3 和 4，全局范数应是 5。裁到 1 后两者约为 0.6、0.8，可以发现错误地给每个参数单独裁剪的实现；无梯度时返回 0。

```python
p1, p2 = torch.nn.Parameter(torch.zeros(1)), torch.nn.Parameter(torch.zeros(1))
p1.grad, p2.grad = torch.tensor([3.]), torch.tensor([4.])
torch.testing.assert_close(clip_grad_norm_([p1, p2], 1), torch.tensor(5.))
torch.testing.assert_close(p1.grad, torch.tensor([0.6]))
torch.testing.assert_close(p2.grad, torch.tensor([0.8]))
assert clip_grad_norm_([], 1).item() == 0
print("simple tests passed")
```

## 追问

**为什么不用 per-layer clip？**
因为它会改掉层与层之间梯度的相对比例。global norm 只缩放整体步长。

**和 clip-by-value 有什么区别？**
`clamp(-c,c)` 会改变梯度方向，global norm 只改长度。

**FSDP / ZeRO 下 $n$ 怎么算？**
各个 rank 先算本地的平方和，all-reduce 之后再开方。手写写单卡就行，但要提这一句。

---
id: code-adamw
section: coding
order: 42
level: A
title: 手写 AdamW 一步：m/v、bias correction、解耦 weight decay
quick: >-
  AdamW 一步是：$m\leftarrow\beta_1 m+(1-\beta_1)g$，$v\leftarrow\beta_2
  v+(1-\beta_2)g^2$，做 bias correction 得 $\hat m=m/(1-\beta_1^t)$、$\hat
  v=v/(1-\beta_2^t)$，参数先乘 $1-\lambda\eta$ 做 decay，再减 $\eta\,\hat m/(\sqrt{\hat
  v}+\varepsilon)$，$t$ 从 1 起。decay 不进 $m/v$，这就是它和 Adam+L2 的差别。
tags:
  - AdamW
  - Optimizer
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28T00:00:00.000Z
sources:
  - title: Decoupled Weight Decay Regularization
    url: 'https://arxiv.org/abs/1711.05101'
    type: primary
---

## 题目描述

实现一次 AdamW 参数更新。输入当前参数、梯度、一阶和二阶矩状态，输出更新后的三份张量；weight decay 与梯度的矩估计分开处理。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01)`。p、g、m、v 是同形浮点张量；t 从 1 开始，是本次更新步数；lr 为学习率，b1/b2 为矩衰减系数，eps 为分母稳定项，wd 为衰减系数。

### 输出与约束

返回 `(p_new,m_new,v_new)`。新矩为 b1*m+(1-b1)*g 与 b2*v+(1-b2)*g²；使用第 t 步偏差校正。参数先按 (1-lr*wd) 衰减，再减 lr*`m_hat`/(sqrt(`v_hat`)+eps)。返回新状态，不要求原地修改输入。

### 示例

```text
p=[1], g=[2], m=[0], v=[0], t=1, lr=0.1, wd=0
返回 p_new≈[0.9], m_new=[0.2], v_new=[0.004]
p=[1], g=[0], m=v=[0], t=1, lr=0.1, wd=0.2 -> p_new=[0.98]
```

## 解题思路与参考答案

AdamW 一步就是先更新一阶矩 $m$ 和二阶矩 $v$，做 bias correction，然后参数先乘 $(1-\eta\lambda)$ 做 weight decay，再减去自适应的更新量。关键在 decay 直接作用在参数上，不进 $m$ 和 $v$；把 $\lambda p$ 加进梯度再交给 Adam，写出来的就是 Adam+L2。

另外还有两个常见错误，一是 $t$ 从 0 起，bias correction 直接除零；二是 bias correction 用 $\beta^t$ 时，把 $t$ 当成已经更新后的步数。超参也要先问：Llama 预训练默认 $\beta=(0.9,0.95)$、weight decay $0.1$，和 PyTorch 默认的 $0.999/0.01$ 不一样。

## 一步

$$
m_t=\beta_1 m_{t-1}+(1-\beta_1)g_t,\quad
v_t=\beta_2 v_{t-1}+(1-\beta_2)g_t^2
$$

$$
\hat m_t=\frac{m_t}{1-\beta_1^t},\quad
\hat v_t=\frac{v_t}{1-\beta_2^t},\quad
p\leftarrow p(1-\eta\lambda)-\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\varepsilon}.
$$

$t$ 是更新次数，第一次更新时 $t=1$。$m,v$ 和 $p$ 同形状。embedding 和 LN / RMSNorm 的 $w$ 通常不做 decay，手写时要能按参数名跳过。

```python
def adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01):
    # t 从 1 起。decay 直接乘 p，不写进 g。
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * (g * g)
    mh = m / (1 - b1**t)
    vh = v / (1 - b2**t)
    p = p * (1 - lr * wd) - lr * mh / (vh.sqrt() + eps)
    return p, m, v
```

和 gradient clipping 一起用的时候，顺序是：AMP 下先把缩放过的梯度还原（unscale），再做 gradient clipping clip，最后调 `adamw_step`。clip 见 `code-grad-clip`，动态损失缩放见 `code-grad-accum-amp`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

第一步设 p=1、g=2、lr=0.1，校正后的 m=2、v=4，预期参数约 0.9。再单测零梯度与 weight decay，参数应变为 0.98。

```python
import torch

p, m, v = adamw_step(
    torch.tensor([1.0]),
    torch.tensor([2.0]),
    torch.zeros(1),
    torch.zeros(1),
    1,
    lr=0.1,
    wd=0.0,
)
torch.testing.assert_close(p, torch.tensor([0.9]))
torch.testing.assert_close(m, torch.tensor([0.2]))
p, _, _ = adamw_step(
    torch.tensor([1.0]),
    torch.zeros(1),
    torch.zeros(1),
    torch.zeros(1),
    1,
    lr=0.1,
    wd=0.2,
)
torch.testing.assert_close(p, torch.tensor([0.98]))
print("simple tests passed")
```

## 追问

**为什么要解耦？**
L2 项加进梯度以后，也会被 $v$ 的自适应缩放除一下，梯度大的坐标受到的衰减就变弱了。AdamW 的 $\lambda\eta p$ 对每个参数都一样。

**bias correction 是干什么的？**
$m,v$ 从 0 起步，前几步偏小。除以 $1-\beta^t$ 把期望拉回到 $g$ 和 $g^2$。

**Lion、Adafactor 呢？**
白板先写 AdamW。Adafactor 用行、列两个因子近似保存 $v$，以减少优化器状态的显存。

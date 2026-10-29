---
id: coding-adamw
section: coding
order: 3
level: A
title: 白板：AdamW 一步更新，m/v、bias correction、decoupled decay
quick: >-
  AdamW 用梯度更新并纠偏 $m,v$，再按自适应步长更新参数，weight decay 单独作用于更新前的参数。比如梯度为零时仍会按比例衰减；把
  decay 加进梯度会让它进入矩估计、被 $\sqrt{v}$ 缩放，得到耦合 L2。
tags:
  - 完整编程练习
  - Coding
  - AdamW
  - Optimizer
  - Meta
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Decoupled Weight Decay Regularization
    url: 'https://arxiv.org/abs/1711.05101'
    type: primary
  - title: torch.optim.AdamW
    url: 'https://pytorch.org/docs/stable/generated/torch.optim.AdamW.html'
    type: primary
---

## 题目描述

实现一次 AdamW 参数更新，返回更新后的参数和优化器状态。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出

`adamw_step(p,g,m,v,t,lr=0.001,b1=0.9,b2=0.999,eps=1e-8,wd=0.01)` 返回 `(new_p,new_m,new_v)`，不修改输入。p、g、m、v 是同形浮点张量，依次为当前参数、梯度、此前一阶矩、此前二阶矩；t 是从 1 开始计数的本次更新序号。

采用标准 AdamW 定义：一阶矩按 b1 平滑梯度，二阶矩按 b2 平滑梯度平方，使用第 t 步的偏差校正；参数更新包含自适应梯度项及独立于梯度的 `lr*wd*p` weight decay。分母为校正二阶矩的平方根加 eps。b1、b2 在 `[0,1)`，eps 为正，lr、wd 非负。

### 完整数值定义

令 `m_new=b1*m+(1-b1)*g`，`v_new=b2*v+(1-b2)*g*g`，再计算 `m_hat=m_new/(1-b1**t)`、`v_hat=v_new/(1-b2**t)`。最终 `new_p=(1-lr*wd)*p-lr*m_hat/(sqrt(v_hat)+eps)`。返回值顺序为 `(new_p,m_new,v_new)`；weight decay 使用旧 p，不进入 m、v。所有运算逐元素执行。

### 示例

```text
p=[1], g=[0], m=[0], v=[0], t=1, lr=0.1, wd=0.2
返回 new_p=[0.98], new_m=[0], new_v=[0]。
p=[1], g=[2], m=v=[0], t=1, lr=0.1, wd=0
返回 new_p 约为 [0.9], new_m=[0.2], new_v=[0.004]。
```

## 解题思路与参考答案

我会先更新一阶、二阶矩并做 bias correction，再把解耦衰减和自适应更新分别作用到参数。最直观的检查是梯度为零：参数仍应按学习率与 weight decay 的乘积衰减，示例从 1 变成 0.98。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证，用 `torch.optim.AdamW` 做数值对照。

### 题面、接口与约束

- `adamw_step(p, g, m, v, t, lr, b1, b2, eps, wd) -> (p, m, v)`：做一步 AdamW 更新，返回新参数和新的一阶、二阶矩状态，不修改输入张量。要用 bias correction 和解耦 weight decay（decoupled weight decay）。
- 约束：`p`、`g`、`m`、`v` 是同形状的浮点张量；`t` 从 1 开始；`0 <= b1, b2 < 1`；`eps > 0`。不满足时抛 `ValueError`。

### 输入输出示例

```text
p=1, g=0, m=v=0, t=1, lr=0.1, wd=0.2  -> p = 1 * (1 - 0.1 * 0.2) = 0.98
p=[1, -2], g=[0.5, 0.25], t=1         -> 和 torch.optim.AdamW(lr=1e-3, weight_decay=0.01) 走一步的结果相同
```

### 解题思路与正确性

先用梯度更新 $m$、$v$ 两个指数滑动平均，再分别除以 $1-\beta_1^t$、$1-\beta_2^t$ 做纠偏。$m,v$ 初始化为 0，前几步会偏小，纠偏把它们放大回 unbiased estimate。

weight decay 直接乘在参数上：`p *= (1 - lr * wd)`，用的是更新前的参数。它不加进梯度，所以不会进入 $m$、$v$，也不会被 $\sqrt{\hat v}$ 缩放。这正是 AdamW 和「Adam + L2」的区别。

### 完整参考实现（Python 3）

```python
import torch
from torch import nn


def adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01):
    """AdamW 的一步更新，不修改输入，返回 (新参数, 新 m, 新 v)。

    p, g, m, v 同形状；t 是从 1 开始的 optimizer step 计数。
    weight decay 直接作用在参数上（decoupled），不进入梯度和矩估计。
    """
    if t < 1:
        raise ValueError(f"step t starts at 1, got {t}")
    if not (0 <= b1 < 1 and 0 <= b2 < 1):
        raise ValueError(f"betas must be in [0, 1), got b1={b1}, b2={b2}")
    if eps <= 0:
        raise ValueError(f"eps must be positive, got {eps}")
    m = b1 * m + (1.0 - b1) * g
    v = b2 * v + (1.0 - b2) * g * g
    m_hat = m / (1.0 - b1**t)  # bias correction：早期 m、v 偏向 0
    v_hat = v / (1.0 - b2**t)
    p = p * (1.0 - lr * wd)  # decoupled decay，用更新前的参数
    p = p - lr * m_hat / (v_hat.sqrt() + eps)
    return p, m, v
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(new_params, reference)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
params = torch.tensor([1.0, -2.0])
grad = torch.tensor([0.5, 0.25])
m0 = torch.zeros_like(params)
v0 = torch.zeros_like(params)

# 首步与 torch.optim.AdamW 一致
new_params, m1, v1 = adamw_step(params, grad, m0, v0, 1)
reference = nn.Parameter(params.clone())
optimizer = torch.optim.AdamW([reference], lr=0.001, weight_decay=0.01)
reference.grad = grad.clone()
optimizer.step()
assert torch.allclose(new_params, reference)

# 连续三步仍与 PyTorch 一致（检查 t 递增时的 bias correction）
current, m_state, v_state = new_params, m1, v1
for step in (2, 3):
    step_grad = grad * step
    current, m_state, v_state = adamw_step(current, step_grad, m_state, v_state, step)
    reference.grad = step_grad.clone()
    optimizer.step()
assert torch.allclose(current, reference)

# 梯度为 0 时只剩衰减：1 * (1 - 0.1 * 0.2) = 0.98
decayed, _, _ = adamw_step(
    torch.tensor([1.0]),
    torch.zeros(1),
    torch.zeros(1),
    torch.zeros(1),
    1,
    lr=0.1,
    wd=0.2,
)
assert torch.allclose(decayed, torch.tensor([0.98]))

# 不修改输入
assert torch.equal(params, torch.tensor([1.0, -2.0]))
assert torch.equal(m0, torch.zeros(2))

# 非法超参数
expect_value_error(adamw_step, params, grad, m0, v0, 0)
expect_value_error(adamw_step, params, grad, m0, v0, 1, b2=1.0)
expect_value_error(adamw_step, params, grad, m0, v0, 1, eps=0.0)
```

### 复杂度与追问

设参数个数为 $P$。一步更新是 $O(P)$ 时间；新参数和两份状态各占 $O(P)$ 空间，也就是优化器状态是参数量的两倍。

- 追问「为什么测试要走多步」：只对一步时 $t=1$，两个纠偏系数恰好让 $\hat m=g$、$\hat v=g^2$，写错 $t$ 的用法也可能通过；多走几步才能测出 bias correction 写得对不对。
- 追问「原地版本」：真实优化器用 `p.mul_(1 - lr * wd)`、`m.lerp_(g, 1 - b1)` 等原地操作省显存，逻辑不变。

## 题怎么来的

Llama / GPT 的训练栈默认用 AdamW，它不是「Adam 加一点 L2」。Meta、OpenAI、Anthropic 的研究岗会让你在白板上写一步更新，再追问为什么耦合的 weight decay 会让梯度大的参数几乎衰减不动。方法出自 Loshchilov & Hutter 的论文，PyTorch 的 `AdamW` 按解耦方式实现。NVIDIA 还会问混合精度下这一步和 GradScaler 的先后顺序。

## 一步更新：$m,v$ → 纠偏 → 自适应步长 → 衰减

梯度 $g_t=\nabla_\theta L(\theta_{t-1})$，其中不含 weight decay 项：

$$
\begin{aligned}
m_t&=\beta_1 m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2 v_{t-1}+(1-\beta_2)g_t^2,\\
\hat m_t&=m_t/(1-\beta_1^t),\quad \hat v_t=v_t/(1-\beta_2^t).
\end{aligned}
$$

$t$ 从 1 开始。参数更新为：

$$
\theta_t=\theta_{t-1}-\eta\Big(\hat m_t/(\sqrt{\hat v_t}+\varepsilon)+\lambda\theta_{t-1}\Big).
$$

代码里的写法 `theta *= (1 - lr * wd)` 再 `theta -= lr * m_hat / (sqrt(v_hat) + eps)` 和上式等价：衰减用的是更新前的 $\theta$，不经过 $\sqrt{v}$。

`m`、`v` 和参数同形状，每个参数各有一份状态。Bias 通常不做衰减，LayerNorm / RMSNorm 的 $\gamma$ 在很多训练配方里也不衰减。白板上先按普通的 dense 参数写，再口头说明哪些参数要排除。

## 耦合 L2 错在哪

Adam 加 L2 是把正则写进损失：$g \leftarrow g+\lambda\theta$，然后整体除以 $\sqrt{v}$。$|g|$ 大的坐标 $v$ 也大，衰减项被自适应分母缩小，正则强度就和梯度尺度绑在了一起。AdamW 把 $\lambda\theta$ 留在参数空间里单独作用，论文标题里的 decoupled 指的就是这一点。因此解释 AdamW 时，需要指出衰减没有进入自适应分母。

混合精度下的顺序是：先 `unscale_`，再 gradient clipping，最后 `optimizer.step()`。gradient clipping 见 `coding-grad-clip`。$t$ 是 optimizer step 的计数，用 gradient accumulation 时，累积多个 micro-step 才加一次 $t$。

## 追问

**$\beta_1=0.9$ 和 $\beta_2=0.999$ 在纠偏上有什么不同？**
$1-\beta_2^t$ 要几千步才接近 1，$v$ 的纠偏持续得比 $m$ 久得多。漏掉 $\beta_2$ 的纠偏，$v$ 被低估，分母偏小，前期步长会偏大；漏掉 $\beta_1$ 的纠偏则让前期步长偏小。
**把 weight decay 加进 $g$ 会怎样？**
衰减被 $1/\sqrt{v}$ 缩放，实际强度和 $\eta,\lambda$ 的直觉对不上，梯度大的坐标几乎不衰减。
**和 SGD + L2 比呢？**
SGD 加 L2 的更新本来就是 $\theta \leftarrow (1-\eta\lambda)\theta-\eta g$，衰减已经和梯度分开。是 Adam 的自适应分母让 L2 变成了耦合的。

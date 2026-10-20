---
id: code-adamw
section: coding
order: 42
level: A
title: 手写 AdamW 一步：m/v、bias correction、解耦 weight decay
quick: >-
  $m\leftarrow\beta_1 m+(1-\beta_1)g$，$v\leftarrow\beta_2 v+(1-\beta_2)g^2$，再
  $\hat m=m/(1-\beta_1^t)$、$\hat v=v/(1-\beta_2^t)$。参数先乘 $1-\lambda\eta$ 做 decay，再减
  $\eta\,\hat m/(\sqrt{\hat v}+\varepsilon)$。$t$ 从 1 起。decay 不进 $m/v$，这就是和 Adam+L2 的差别。
tags:
  - AdamW
  - Optimizer
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Decoupled Weight Decay Regularization
    url: https://arxiv.org/abs/1711.05101
    type: primary
---

常见误区是：把 $\lambda p$ 加进梯度再丢给 Adam（那是 Adam+L2）；或 $t$ 从 0 起导致除零；或 bias correction 用 $\beta^t$ 却把 $t$ 当成已经更新后的步。Llama 预训练默认 $\beta=(0.9,0.95)$，weight decay $0.1$，和 PyTorch 默认 $0.999/0.01$ 不一样，先问超参再写。

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

$t$ 是更新次数，第一次 $t=1$。$m,v$ 与 $p$ 同形。embedding 和 LN / RMSNorm 的 $w$ 常常不做 decay，手写要能按参数名跳过。

```python
def adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01):
    # t 从 1 起。decay 直接乘 p，不写进 g。
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * (g * g)
    mh = m / (1 - b1 ** t)
    vh = v / (1 - b2 ** t)
    p = p * (1 - lr * wd) - lr * mh / (vh.sqrt() + eps)
    return p, m, v
```

与梯度裁剪一起使用时，先在 AMP 下还原缩放后的梯度（unscale），再做梯度裁剪 clip，最后调用 `adamw_step`。clip 见 `code-grad-clip`，动态损失缩放见 `code-grad-accum-amp`。

## 追问

- **为什么解耦？** L2 项加入梯度后，也会受到 $v$ 的自适应缩放，因此梯度较大的坐标所受的衰减会变弱。AdamW 的 $\lambda\eta p$ 对每个参数一样。
- **bias correction 干什么？** $m,v$ 从 0 起步，前几步偏小。除以 $1-\beta^t$ 把期望拉回 $g$ / $g^2$。
- **和 Lion / Adafactor？** 白板先写 AdamW。Adafactor 用行、列因子近似保存 $v$，以减少优化器状态占用。

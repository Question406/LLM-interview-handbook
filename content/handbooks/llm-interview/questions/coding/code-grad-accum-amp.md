---
id: code-grad-accum-amp
section: coding
order: 31
level: A
title: 手写梯度累积 + fp16 动态 loss scaling：unscale、查 inf、clip 的顺序
quick: "loss 除以 accum_steps 再乘 scale 反传；累积完先 unscale 并查 inf/nan，溢出就跳过这步、scale 减半。没溢出才 clip 和 step，连续多步无溢出再把 scale 翻倍。"
tags:
  - Mixed Precision
  - Loss Scaling
  - Gradient Accumulation
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
---

面试官让你别用 `GradScaler` 自己写，考的是顺序。常见误区是：损失（loss） 没除以 accum_steps，等效 lr 放大 k 倍；clip 放在 unscale 之前，阈值被 scale 放大了几万倍，clip 形同虚设；发现 inf 以后照样 `step()`，参数直接变 nan；scale 只减不增，训练后期小梯度又开始下溢。fp16 和 bf16 的数值差别见 `stepfun-bf16-fp16` 和 `sys-precision`，clip 本身见 `fund-gradclip`。

## 流程

Mixed Precision Training 那篇的做法：fp16 做前向和反向，fp32 保留一份 master weights，loss 乘一个 scale $S$ 再 backward，让本来会下溢成 0 的小梯度落进 fp16 的可表示范围，更新前再除回去。动态版本不固定 $S$：溢出就减半并跳过这步，连续 $N$ 步没溢出就翻倍，$S$ 会贴着溢出边缘自适应。

一个 optimizer step 的顺序：

1. 对 $k$ 个 micro-batch：`loss / k`，乘 $S$，backward，梯度在 `.grad` 里累加。
2. 所有梯度乘 $1/S$（unscale）。
3. 查全部梯度是否 finite。有 inf/nan：清梯度，$S\leftarrow S/2$，计数清零，这步不更新。
4. 没溢出：算 global norm，超过阈值就整体缩放。
5. `optimizer.step()`，计数加一，满 $N$ 步 $S\leftarrow 2S$。

```python
import torch

class DynamicLossScaler:
    def __init__(self, init_scale=2.0 ** 16, growth_interval=2000, min_scale=1.0):
        self.scale = init_scale
        self.growth_interval = growth_interval
        self.min_scale = min_scale
        self.good_steps = 0

    def update(self, found_inf):
        if found_inf:
            self.scale = max(self.scale / 2, self.min_scale)
            self.good_steps = 0
        else:
            self.good_steps += 1
            if self.good_steps % self.growth_interval == 0:
                self.scale *= 2

def train_step(model, opt, micro_batches, loss_fn, scaler, max_norm=1.0):
    k = len(micro_batches)
    opt.zero_grad(set_to_none=True)
    for x, y in micro_batches:
        # DDP 下前 k-1 个 micro-step 放进 model.no_sync()，最后一个才 all-reduce
        loss = loss_fn(model(x), y) / k
        (loss.float() * scaler.scale).backward()

    params = [p for p in model.parameters() if p.grad is not None]
    found_inf = False
    for p in params:
        p.grad.mul_(1.0 / scaler.scale)
        if not torch.isfinite(p.grad).all():
            found_inf = True
    if found_inf:
        opt.zero_grad(set_to_none=True)
        scaler.update(True)
        return False, None

    total_norm = torch.norm(torch.stack([p.grad.norm(2) for p in params]), 2)
    coef = max_norm / (total_norm + 1e-6)
    if coef < 1:
        for p in params:
            p.grad.mul_(coef)
    opt.step()
    scaler.update(False)
    return True, total_norm
```

这里模型参数就是 fp32，省掉了 master weights 的拷贝。真 fp16 训练里，模型参数是 fp16，梯度要先拷到 fp32 的 master 梯度上再 unscale、clip、step，step 完再把 fp32 权重 cast 回 fp16。unscale 放在 fp32 上做，否则除以 $S$ 那一下本身又可能下溢。

## DDP 和累积

DDP 默认每次 backward 都 all-reduce 梯度。累积 $k$ 步时，前 $k-1$ 个 micro-step 用 `with model.no_sync():` 包住，只在本地累加，最后一个 micro-step 的 backward 才触发一次 all-reduce，通信量降到 $1/k$。inf 检查要在 all-reduce 之后做：某个 rank 溢出，平均后所有 rank 的梯度都是 inf，大家一起跳过，不会出现有的 rank 更新了有的没更新。多卡间 scale 一致、同步跳步的细节见 `sys-allreduce-loss-scale`。

## 追问

- **bf16 为什么通常不用 loss scaling？** bf16 有 8 位指数，和 fp32 同样的动态范围，最小正规数约 $10^{-38}$，小梯度基本不会下溢。fp16 只有 5 位指数，最小正规数约 $6\times10^{-5}$，这才需要乘 $S$ 往上挪。bf16 的问题是尾数只有 7 位，精度差，要靠 fp32 master weights 和 fp32 累加补。
- **为什么 clip 必须在 unscale 之后？** clip 阈值是按真实梯度范数定的。unscale 前的范数是真实值乘 $S$，拿它比 `max_norm` 会几乎每步都触发，而且缩放后的系数也不对。
- **loss 为什么除以 $k$ 而不是事后把梯度除以 $k$？** 两者数学等价。除 loss 更省事，也能避免累加过程中 fp16 梯度变大溢出。但要保证各 micro-batch 有效 token 数相同，否则按 token 加权才等价于大 batch。
- **跳步会不会影响 lr schedule？** 跳过的那步没有 `opt.step()`，按 `code-lr-schedule` 的口径 scheduler 也不该前进。训练初期 scale 从 $2^{16}$ 往下找的几次跳步通常可以忽略。
- **scale 一直在减半怎么办？** 说明梯度本身出了 inf/nan，不是范围问题：查 loss 是否 nan、有没有除零、log(0)、attention 的 softmax 是否在 fp16 里算。`min_scale` 兜底，避免 scale 一路减半逼近 0，乘完之后梯度全部下溢成 0。
- **为什么查 inf 要看所有参数？** 只要一个参数梯度溢出，global norm 就是 inf，clip 会把所有梯度乘成 0 或 nan。必须整体判断、整体跳过。

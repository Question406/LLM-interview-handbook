---
id: code-grad-accum-amp
section: coding
order: 31
level: A
title: 手写梯度累积 + fp16 动态 loss scaling：unscale、查 inf、clip 的顺序
quick: "每个 micro-batch 的 loss 先除以 accum_steps、再乘 scale 反传；累积完先 unscale，再查 inf/nan，溢出就跳过这一步、scale 减半。没溢出才 clip 和 step，连续很多步没溢出再把 scale 翻倍。"
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

## 题目描述

实现带梯度累积、动态 loss scaling 和全局梯度裁剪的单次训练更新；同一组 micro-batch 只触发一次优化器更新。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `DynamicLossScaler(init_scale=2**16,growth_interval=2000,min_scale=1)` 的 `update(found_inf)`，以及 `train_step(model,opt,micro_batches,loss_fn,scaler,max_norm=1.0)`。`micro_batches` 是非空且各批大小相同的 (x,y) 列表，`loss_fn` 返回标量均值损失；model/opt 为传入的可训练模型和优化器。

### 输出与约束

累计各 micro-batch 损失的平均梯度，先解除 scale，再检查有限性并裁剪总 L2 范数。有限时 step，返回 `(True,裁剪前总范数)`；溢出时跳过 step 并清梯度，返回 `(False,None)`。连续 `growth_interval` 次成功后 scale 翻倍；溢出后减半且不低于 `min_scale`，同时重置成功计数。溢出是此训练题的正常分支。

### 示例

```text
scaler初始 scale=4, growth_interval=2, min_scale=2
依次 update(False), update(False), update(True) 后，scale依次为4、8、4。
两份相同 micro-batch 的平均梯度应与只训练一份相同，而非翻倍。
```

## 解题思路与参考答案

顺序是这样的：每个 micro-batch 的 loss 先除以 accum_steps，再乘上 scale 做 backward；$k$ 个 micro-batch 累积完，先 unscale，再检查有没有 inf/nan。有溢出就清掉梯度、跳过这一步、scale 减半；没溢出才做 clip 和 `step()`，连续若干步都没溢出再把 scale 翻倍。面试官让你别用 `GradScaler` 自己写，考的就是这个顺序。

顺序错了各有各的后果。损失（loss）没除以 accum_steps，等效 lr 放大了 k 倍。clip 放在 unscale 之前，阈值相当于被 scale 放大了几万倍，clip 形同虚设。发现 inf 还照样 `step()`，参数直接变成 nan。scale 只减不增，训练后期小梯度又开始下溢。fp16 和 bf16 的数值差别见 `stepfun-bf16-fp16` 和 `sys-precision`，clip 本身见 `fund-gradclip`。

## 流程

这套做法来自 Mixed Precision Training 那篇：fp16 做前向和反向，fp32 留一份 master weights，loss 乘一个 scale $S$ 再 backward，让本来会下溢成 0 的小梯度落进 fp16 能表示的范围，更新之前再除回去。动态版本不固定 $S$：溢出就减半并跳过这一步，连续 $N$ 步没溢出就翻倍，$S$ 会贴着溢出的边缘自己调。

一个 optimizer step 按这个顺序走：

1. 对 $k$ 个 micro-batch，各自 `loss / k`，乘 $S$，backward，梯度在 `.grad` 里累加。
2. 所有梯度乘 $1/S$，也就是 unscale。
3. 检查全部梯度是否 finite。有 inf/nan 就清梯度，$S\leftarrow S/2$，计数清零，这一步不更新。
4. 没溢出就算 global norm，超过阈值时整体缩放。
5. `optimizer.step()`，计数加一，满 $N$ 步就 $S\leftarrow 2S$。

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

这里模型参数本身就是 fp32，所以省掉了 master weights 的拷贝。真正的 fp16 训练里，模型参数是 fp16，梯度要先拷到 fp32 的 master 梯度上，再 unscale、clip、step，step 完再把 fp32 权重 cast 回 fp16。unscale 放在 fp32 上做，是因为在 fp16 里除以 $S$ 这一下本身也可能下溢。

## DDP 和累积

DDP 默认每次 backward 都会 all-reduce 梯度。累积 $k$ 步时，前 $k-1$ 个 micro-step 用 `with model.no_sync():` 包住，只在本地累加，最后一个 micro-step 的 backward 才触发一次 all-reduce，通信量降到 $1/k$。inf 检查要放在 all-reduce 之后：某个 rank 溢出了，平均之后所有 rank 的梯度都是 inf，大家一起跳过，不会出现有的 rank 更新了、有的没更新。多卡之间 scale 怎么保持一致、怎么同步跳步，见 `sys-allreduce-loss-scale`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先单独测试 scaler 的状态变化：连续两次成功放大，遇到溢出缩小，达到 min_scale 后不再下降。这是最小状态测试；训练更新还应补整批与等大小 micro-batch 的参数对照。

```python
scaler = DynamicLossScaler(init_scale=4, growth_interval=2, min_scale=2)
scaler.update(False)
assert scaler.scale == 4
scaler.update(False)
assert scaler.scale == 8
scaler.update(True)
assert scaler.scale == 4 and scaler.good_steps == 0
scaler.update(True)
scaler.update(True)
assert scaler.scale == 2
print("simple tests passed")
```

## 追问

**bf16 为什么通常不用 loss scaling？**
因为 bf16 有 8 位指数，动态范围和 fp32 一样，最小正规数约 $10^{-38}$，小梯度基本不会下溢。fp16 只有 5 位指数，最小正规数约 $6\times10^{-5}$，所以才需要乘 $S$ 往上挪。bf16 的问题在精度：尾数只有 7 位，要靠 fp32 master weights 和 fp32 累加来补。

**为什么 clip 必须在 unscale 之后？**
clip 阈值是按真实梯度范数定的。unscale 之前的范数是真实值乘以 $S$，拿它去和 `max_norm` 比，几乎每步都会触发，算出来的缩放系数也不对。

**为什么在 loss 上除以 $k$，不在事后把梯度除以 $k$？**
两者数学上等价。除 loss 更省事，也能避免累加过程中 fp16 梯度变大溢出。前提是各个 micro-batch 的有效 token 数相同，否则要按 token 加权才和大 batch 等价。

**跳步会影响 lr schedule 吗？**
跳过的那一步没有 `opt.step()`，按 `code-lr-schedule` 的口径，scheduler 也不该前进。训练初期 scale 从 $2^{16}$ 往下找的那几次跳步通常可以忽略。

**scale 一直在减半怎么办？**
说明梯度本身出了 inf/nan，和数值范围无关了。去查 loss 是不是 nan、有没有除零或 log(0)、attention 的 softmax 是不是在 fp16 里算的。`min_scale` 用来兜底，免得 scale 一路减半逼近 0，乘完之后梯度全部下溢成 0。

**为什么查 inf 要看所有参数？**
只要有一个参数的梯度溢出，global norm 就是 inf，clip 会把所有梯度乘成 0 或者 nan。所以必须整体判断、整体跳过。

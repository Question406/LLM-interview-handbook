---
id: code-lr-schedule
section: coding
order: 30
level: A
title: 手写 warmup + cosine 学习率：step 从几开始、衰减到 min_lr、WSD 变体
quick: >-
  把 lr 写成 step 的纯函数：warmup 段从 $\eta_{\max}/W$ 线性涨到 $\eta_{\max}$，之后按余弦降到 $\eta_{\min}$；WSD 则是 warmup 后一段长平台，最后一小段再衰减。用 `LambdaLR` 返回倍率或每步手动写 `param_group['lr']` 都行，要紧的是 step 计数口径一致、warmup 第一步 lr 不为 0、resume 时把 scheduler state 或全局 step 一起存。
tags:
  - Learning Rate
  - Warmup
  - Cosine Decay
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "SGDR: Stochastic Gradient Descent with Warm Restarts"
    url: https://arxiv.org/abs/1608.03983
    type: primary
---

## 题目描述

实现以训练 step 为输入的学习率日程，并提供与 PyTorch 优化器配套的小型调度接口。step 从 0 开始，输入参数均满足合法范围。

### 接口与日程定义

- `cosine_lr(step,max_lr,min_lr,warmup,total)`：前 warmup 步从 `max_lr/warmup` 均匀升至 `max_lr`；从 step=warmup 到 total 按半个余弦周期从 `max_lr` 降到 `min_lr`；step>=total 时固定为 `min_lr`。warmup 为正数，total 大于 warmup，`0 <= min_lr <= max_lr`。
- `wsd_lr(...,decay_frac=0.1)`：前段 warmup 相同，之后保持 `max_lr`，直到 `int(total*(1-decay_frac))` 开始线性下降，在 total 达到 `min_lr`。输入保证平台段与衰减段有合理顺序。
- `make_scheduler(opt,...,fn)` 返回使用相应日程的 LambdaLR，opt 初始学习率设为 `max_lr`；`set_lr_manually(opt,step,**kw)` 将同一数值设置到每个参数组。
- `train(model,opt,sched,batches,ckpt_path=None)`：batches 是 `(x,y)` 的可迭代批次，model(x) 与 y 形状相同。每批使用固定的均方误差 `mean((model(x)-y)**2)`，完成一次参数更新后再完成一次调度更新；无返回值。提供 `ckpt_path` 时，保存以 `model`、`opt`、`sched` 为键的三个 `state_dict`。

### 示例

```text
max_lr=1.0, min_lr=0.1, warmup=2, total=10
两种日程在step=0 -> 0.5
两种日程在step=1 -> 1.0
两种日程在step=10及以后 -> 0.1
```

这是手册统一的计步约定，不要求兼容每个外部训练框架的默认 step 含义。

## 解题思路与参考答案

我会把 lr 写成 step 的纯函数：warmup 段从 $\eta_{\max}/W$ 线性涨到 $\eta_{\max}$，之后按余弦降到 $\eta_{\min}$。面试官看的是这个函数写得对不对，再就是你能不能说清 step 从几开始数、resume 之后接不接得上。为什么要 warmup 见 `fund-warmup`，AdamW 本身见 `fund-adamw`。

最常见的错是 warmup 写成 `max_lr * step / warmup`，而 step 从 0 起，第一步 lr 就等于 0。这一步参数没动，AdamW 的二阶矩却更新了一次。还有人在余弦公式里用 `step / total` 当进度，该用的是 `(step - warmup) / (total - warmup)`，结果 warmup 一结束 lr 已经掉下去一截，训练结束时也到不了 min_lr。resume 时只存了模型和 optimizer，scheduler 从头开始又 warmup 一遍，这种情况也很多。

设 $W$ 为 warmup 步数，$N$ 为总步数，$s$ 从 0 计数，表示第 $s$ 次 `optimizer.step()` 用的 lr：

$$
\eta(s)=\begin{cases}
\eta_{\max}\cdot\dfrac{s+1}{W}, & s \lt W\\[6pt]
\eta_{\min}+\dfrac{1}{2}(\eta_{\max}-\eta_{\min})\Big(1+\cos\big(\pi\cdot\dfrac{s-W}{N-W}\big)\Big), & W\le s \lt N\\[6pt]
\eta_{\min}, & s\ge N
\end{cases}
$$

余弦段来自 SGDR，LLM 预训练一般只用一个周期，不做 restart。WSD（warmup-stable-decay）把余弦换成三段：warmup 之后保持 $\eta_{\max}$ 的长平台，最后在占总步数一小部分（比如 10%）的区间里降到 $\eta_{\min}$，下面代码里用的是线性衰减。它的好处是平台期任意一个 checkpoint 都可以拿出来单独跑衰减段，得到一个可用的模型，总步数也不用在开训时定死。

```python
import math
import torch

def cosine_lr(step, max_lr, min_lr, warmup, total):
    if step < warmup:
        return max_lr * (step + 1) / warmup
    if step >= total:
        return min_lr
    p = (step - warmup) / max(1, total - warmup)
    return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * p))

def wsd_lr(step, max_lr, min_lr, warmup, total, decay_frac=0.1):
    decay_start = int(total * (1 - decay_frac))
    if step < warmup:
        return max_lr * (step + 1) / warmup
    if step < decay_start:
        return max_lr
    if step >= total:
        return min_lr
    p = (step - decay_start) / max(1, total - decay_start)
    return max_lr - (max_lr - min_lr) * p

def make_scheduler(opt, max_lr, min_lr, warmup, total, fn=cosine_lr):
    # LambdaLR 返回的是倍率，param_group 的初始 lr 必须设成 max_lr
    return torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: fn(s, 1.0, min_lr / max_lr, warmup, total))

def train(model, opt, sched, batches, ckpt_path=None):
    for x, y in batches:
        loss = torch.nn.functional.mse_loss(model(x), y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        sched.step()
    if ckpt_path:
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(),
                    "sched": sched.state_dict()}, ckpt_path)

def set_lr_manually(opt, step, **kw):
    for g in opt.param_groups:
        g["lr"] = cosine_lr(step, **kw)
```

## step 口径和 resume

`LambdaLR` 构造时就把 lr 设成 `base_lr * fn(0)`，之后每调一次 `sched.step()`，内部的 `last_epoch` 加一。所以顺序必须是 `opt.step()` 在前、`sched.step()` 在后，这样 `fn` 收到的 $s$ 正好是下一次 `opt.step()` 的 0 起下标。顺序写反，PyTorch 会给警告，第一步的 lr 也被跳过了。

手动写 `param_group['lr']` 更直观，在 `opt.step()` 之前按全局 step 算一次赋进去就行。多个 param group 有不同 lr 的时候，比如 embedding 单独一组，`LambdaLR` 的倍率写法天然按组缩放，手动写就得自己记住每组的 base lr。

resume 时 `LambdaLR` 的状态就是 `last_epoch`，存下 `sched.state_dict()`，加载后接着用。手动写法要把全局 step 存进 checkpoint。只存模型的话，lr 会从 warmup 重新开始，Adam 的一阶和二阶矩也没了，loss 常会出现尖峰。梯度累积时 $s$ 按 optimizer step 数，不按 micro-batch 数。加载完想确认对不对，打印 `opt.param_groups[0]['lr']` 和 `sched.last_epoch`，和按全局 step 用纯函数算出来的值对一下就行。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

warmup=2 时第 0 步为最高学习率的一半，第 1 步到最高值；total 及之后应等于 min_lr。这样能发现 warmup 的 step+1 偏移错误。

```python
import math
for schedule in (cosine_lr, wsd_lr):
    assert math.isclose(schedule(0, 1., 0.1, 2, 10), 0.5)
    assert math.isclose(schedule(1, 1., 0.1, 2, 10), 1.)
    assert math.isclose(schedule(10, 1., 0.1, 2, 10), 0.1)
    assert math.isclose(schedule(11, 1., 0.1, 2, 10), 0.1)
print("simple tests passed")
```

## 追问

**warmup 为什么从 $\eta_{\max}/W$ 起，不从 0 起？**
lr 为 0 的那一步参数不动，AdamW 的动量和二阶矩照样被更新，等于浪费一步，还污染了统计量。写成 $(s+1)/W$，或者设一个 `warmup_init_lr` 下限，都可以。

**min_lr 设多少？**
常见取 $\eta_{\max}$ 的 10% 左右，或者更小。衰减到 0 会让最后一段几乎不学，太高的话收尾时 loss 降不下去，要看验证集来定。

**WSD 的衰减段为什么短？**
平台期用大 lr 快速走，loss 高，但一直在往低处挪；衰减段把 lr 降下来，loss 会很快掉一截。衰减段占比、衰减形状（线性、余弦、$1-\sqrt{p}$）都是超参。也因为衰减只在最后，中途改总步数时，余弦的形状依赖 $N$，一改曲线就跳；WSD 在平台期改 $N$ 不影响已经走过的部分，这是它常被用于持续训练的原因。

**batch size 变了，lr 要不要跟着变？**
要。一般按经验缩放（线性或平方根）重调 $\eta_{\max}$，warmup 步数也要按 token 数重新确定，不能直接沿用。

---
id: code-lr-schedule
section: coding
order: 30
level: A
title: 手写 warmup + cosine 学习率：step 从几开始、衰减到 min_lr、WSD 变体
quick: >-
  lr 写成 step 的纯函数：warmup 段线性从 $\eta_{\max}/W$ 涨到 $\eta_{\max}$，之后按余弦从
  $\eta_{\max}$ 降到 $\eta_{\min}$，WSD 则是 warmup 后长平台、最后一小段再衰减。
  用 `LambdaLR` 返回倍率或每步手动写 `param_group['lr']` 都行，关键是 step 计数口径一致、
  warmup 第一步 lr 不为 0、resume 时把 scheduler state 或全局 step 一起存。
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

常见错法有三种。warmup 写成 `max_lr * step / warmup`，而 step 从 0 起，第一步 lr 等于 0，这一步白跑，AdamW 的二阶矩倒是更新了一次。余弦公式里的进度用 `step / total` 而不是 `(step - warmup) / (total - warmup)`，结果 warmup 结束时 lr 已经掉下来一截，训练结束也到不了 min_lr。resume 时只存模型和 optimizer，scheduler 从头开始，又 warmup 一遍。面试官看的是你能不能把 lr 写成 step 的纯函数，并说清 step 的口径。为什么要 warmup 见 `fund-warmup`，AdamW 本身见 `fund-adamw`。

## 公式

设 $W$ 为 warmup 步数，$N$ 为总步数，$s$ 从 0 计数（第 $s$ 次 `optimizer.step()` 用的 lr）：

$$
\eta(s)=\begin{cases}
\eta_{\max}\cdot\dfrac{s+1}{W}, & s \lt W\\[6pt]
\eta_{\min}+\dfrac{1}{2}(\eta_{\max}-\eta_{\min})\Big(1+\cos\big(\pi\cdot\dfrac{s-W}{N-W}\big)\Big), & W\le s \lt N\\[6pt]
\eta_{\min}, & s\ge N
\end{cases}
$$

余弦段来自 SGDR，LLM 预训练一般只用一个周期、不做 restart。WSD（warmup-stable-decay）把余弦换成三段：warmup 后保持 $\eta_{\max}$ 的长平台，最后占总步数一小部分（比如 10%）的区间里降到 $\eta_{\min}$，下面代码用线性衰减。好处是平台期任意一个 checkpoint 都可以拿出来单独跑衰减段得到一个可用模型，总步数也不用在开训时定死。

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

`LambdaLR` 构造时就把 lr 设成 `base_lr * fn(0)`，之后每调一次 `sched.step()`，内部 `last_epoch` 加一。所以顺序必须是 `opt.step()` 在前、`sched.step()` 在后，`fn` 收到的 $s$ 正好是下一次 `opt.step()` 的 0 起下标。顺序写反，PyTorch 会警告，而且第一步的 lr 被跳过。

手动写 `param_group['lr']` 更直观：在 `opt.step()` 之前按全局 step 算一次赋值。多个 param group 有不同 lr（比如 embedding 单独一组）时，`LambdaLR` 的倍率写法天然按组缩放，手动写就要自己记每组的 base lr。

resume 时 `LambdaLR` 的状态就是 `last_epoch`，存 `sched.state_dict()`，加载后继续使用。手动写法要把全局 step 存进 checkpoint。只存模型的话，lr 会从 warmup 重新开始，Adam 的一阶和二阶矩也没了，loss 常会出现尖峰。梯度累积时 $s$ 按 optimizer step 数，不按 micro-batch 数。

## 追问

- **warmup 为什么从 $\eta_{\max}/W$ 起而不是 0？** lr 为 0 的那一步参数不动，但 AdamW 的动量和二阶矩照样被更新，等于浪费一步还污染了统计量。写成 $(s+1)/W$ 或者设一个 `warmup_init_lr` 下限都可以。
- **min_lr 设多少？** 常见取 $\eta_{\max}$ 的 10% 左右或者更小。衰减到 0 会让最后一段几乎不学，太高则收尾时 loss 降不下去，需要看验证集定。
- **WSD 衰减段为什么短？** 平台期用大 lr 快速走，loss 高但在往低处挪；衰减段把 lr 降下来，loss 会很快掉一截。衰减段占比、衰减形状（线性、余弦、$1-\sqrt{p}$）都是超参。
- **中途改总步数怎么办？** 余弦的形状依赖 $N$，改了之后曲线会跳。WSD 在平台期改 $N$ 不影响已经走过的部分，这是它常被用于持续训练的原因。
- **batch size 变了 lr 要不要变？** 一般按经验缩放（线性或平方根）重调 $\eta_{\max}$，warmup 步数也要根据 token 数重新确定，不能直接沿用。
- **resume 后 lr 对不对怎么检查？** 加载完打印 `opt.param_groups[0]['lr']` 和 `sched.last_epoch`，和按全局 step 用纯函数算出来的值对一下。

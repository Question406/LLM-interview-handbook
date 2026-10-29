---
id: code-softcap
section: coding
order: 48
level: A
title: 手写 Gemma-2 的 softcap：tanh 压 scores / logits，和 clip 差在可导
quick: >-
  $\mathrm{softcap}(x,c)=c\cdot\tanh(x/c)$。Gemma-2 对 attention scores 用 $c=50$，对最终 logits 用 $c=30$，都放在 softmax 之前。值域是 $(-c,c)$，两端饱和但导数不为 0；写成 `clamp(-c,c)` 就成了硬截断，范围外的梯度是 0。
tags:
  - Softcap
  - Gemma
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Gemma 2 Technical Report
    url: https://arxiv.org/abs/2408.00118
    type: primary
---

## 题目描述

实现作用于 attention 分数或输出 logits 的平滑幅度限制。与直接截断不同，本题指定一个连续的逐元素变换，使大正数和大负数逐渐接近正负 cap。

### 接口与语义

- `softcap(x,cap)`：cap 为正数，输出定义为逐元素 `cap * tanh(x/cap)`，保留输入张量的形状。
- `logits_capped(logits,cap=30)`：把同一变换应用于 logits。
- `attn_scores_capped(q,k,cap=50)`：q、k 的最后一维长度 D 相同，其余 batch/head 维可广播；先定义缩放内积分数 `q @ k.transpose(-1,-2) / sqrt(D)`，再对每个分数应用上述变换，返回分数矩阵。此接口不执行 softmax，也不添加 mask。

### 示例

```text
softcap([0],3) -> [0]
softcap([-1000,1000],3) -> 约[-3,3]
q与k全为0时，attn_scores_capped(q,k) -> 全零分数矩阵
```

浮点 tanh 对很大输入可能舍入到1，因此允许输出等于正负 cap。

## 解题思路与参考答案

softcap 就是 $c\tanh(x/c)$：小分数几乎不动，大分数被平滑地压到 $(-c,c)$ 以内。和 `clamp` 的区别在可导，`clamp` 是硬截断，超出范围的地方梯度是 0，tanh 两端虽然饱和，导数却不为 0。

要它是因为在深层网络里，$QK^\top/\sqrt{d}$ 偶尔会冲到几百，softmax 的概率几乎全集中到一个位置上。softcap 把分数压进一个有界区间，训练更稳。它可以和 QK-Norm 同时用，Gemma-2 用的是 softcap 加局部/全局 attention 交替，对 attention scores 取 $c=50$，对最终 logits 取 $c=30$。

$$
\mathrm{softcap}(x,c)=c\tanh(x/c).
$$

$x\ll c$ 时 $\tanh(x/c)\approx x/c$，输出约等于 $x$，小分数基本不受影响；$|x|\gg c$ 时输出逼近 $\pm c$。

```python
import torch


def softcap(x, cap):
    return cap * torch.tanh(x / cap)


def attn_scores_capped(q, k, cap=50.0):
    scores = q @ k.transpose(-1, -2) / (q.size(-1) ** 0.5)
    return softcap(scores, cap)


def logits_capped(logits, cap=30.0):
    return softcap(logits, cap)
```

位置要放对。causal 或 padding mask 的 $-\infty$ 要在 cap **之后** 再填。先 cap 再填没问题；先填 $-\infty$ 再 `tanh` 的话，`-inf/c` 还是 `-inf`，`tanh` 得到 -1，乘上 $c$ 变成 $-c$，被 mask 的位置只是分数很小，概率并不为零。正确的顺序是：算 scores → softcap → masked_fill(-inf) → softmax。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

检查零点、正负对称和大输入的幅度上限。上限检查允许等号，因为浮点 tanh 在大输入时会舍入成 1。

```python
x = torch.tensor([-1000.0, -1.0, 0.0, 1.0, 1000.0])
y = softcap(x, 3.0)
assert torch.isfinite(y).all() and (y.abs() <= 3).all()
torch.testing.assert_close(y, -y.flip(0))
assert y[2].item() == 0
print("simple tests passed")
```

## 追问

**最终 logits 为什么也要 cap？**
vocabulary 很大时，个别 logit 可能异常增大，影响 sampling 和 cross entropy loss（CE）的数值稳定性。$c=30$ 是 Gemma-2 用在 logits 上的数，别背成 50。

**和 z-loss 有什么区别？**
z-loss 是往 $\log\sum e^{z}$ 上加惩罚，改的是训练目标；softcap 改的是前向函数本身。

**推理时能去掉吗？**
不能。训练时用了，推理就得留着，否则分布对不上。

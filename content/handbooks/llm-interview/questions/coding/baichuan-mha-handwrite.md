---
id: baichuan-mha-handwrite
section: coding
order: 184
level: A
title: 百川智能二面：手写 multi-head attention 时和 DeepSeek 练习卡差在哪？
quick: >-
  写法和 DeepSeek 那张练习卡一样：算 $QKV$，拆头，做缩放点积加 mask，再把各头拼回去。百川二面的差别在后面连着问 GQA/MHA 的区别和
  DPO/PPO 公式，所以 Attention 要十分钟内写完主干，留时间给后面几题。
tags:
  - Baichuan
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川大模型算法二面-日常实习
    url: 'https://www.nowcoder.com/feed/main/detail/326e80fe4eb14fd58e9712ca2852ec1a'
    type: candidate-first-hand
---

## 题目描述

实现一个不带 bias、dropout 或 KV cache 的 multi-head self-attention 函数。输入是同一段序列的隐藏表示，以及已给定的四个投影矩阵；返回投影后的 attention 输出。

### 接口与张量

`mha(x, wq, wk, wv, wo, n_heads, mask=None)`：x 形状为 `[B,T,C]`，四个权重均为 `[C,C]`，采用 `x @ weight` 的权重布局。C 能被正整数头数整除，每头维度为 `C/n_heads`。每个头的分数为 Q 与 K 的内积除以每头维度的平方根，沿 key 维形成概率，并对 V 加权；拼回 C 维后应用 wo。输出形状仍为 `[B,T,C]`。

mask 为可广播到 `[B,H,T,T]` 的布尔张量，True 表示禁止读取该位置；每个 query 至少有一个可见 key。不传 mask 时不额外施加因果限制。以上形状及 mask 语义是手册重构练习约定。

### 示例

```text
x.shape = [1,2,4]，x 全为 0
wq = wk = wv = wo = 4×4 单位矩阵，n_heads = 2
mha(...) -> 形状 [1,2,4] 的全零张量
```

若传入上三角为 True 的因果 mask，改动第二个 token 不应改变第一个 token 的输出。

## 解题思路与参考答案

手写 multi-head attention 的步骤和 DeepSeek 那张练习卡完全一样：算 $Q,K,V$，拆成多个头，做缩放点积加 mask，最后把各头拼回去，骨架见 `deepseek-mha-handwrite`、`pdd-attention-handwrite`。百川二面的差别在后面：紧接着会问 GQA、DPO/PPO，还有二分求根（见 `baichuan-sqrt-binary-search`、`baichuan-grpo-ppo-dpo`）。所以 Attention 要写得快、写得对，写成 `nn.MultiheadAttention` 一行是不算数的。

最容易卡住的地方是 reshape，比如把 $[B,T,H,d_h]$ 和 $[B,H,T,d_h]$ 搞反，后面的 `view` 就全错了。我的习惯是先把形状写在旁边，再写公式。

## 形状：拆头、缩放、mask、拼回

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

$d_{\mathrm{model}}$ 要能被 $H$ 整除，$d_h=d_{\mathrm{model}}/H$。拆头之后 $Q,K,V$ 都是 $[B,H,T,d_h]$，scores 是 $[B,H,T,T]$。因果 mask 只允许访问下三角；padding mask 里 True/False 的含义要和 `masked_fill(-inf)` 对得上。用 fp16 时把 softmax 转到 fp32 算。调 `view` 之前要保证张量是 `contiguous` 的。

```python
import torch


def mha(x, wq, wk, wv, wo, n_heads, mask=None):
    b, t, c = x.shape
    dh = c // n_heads
    q = (x @ wq).view(b, t, n_heads, dh).transpose(1, 2)
    k = (x @ wk).view(b, t, n_heads, dh).transpose(1, 2)
    v = (x @ wv).view(b, t, n_heads, dh).transpose(1, 2)
    scores = (q @ k.transpose(-2, -1)) * dh**-0.5
    if mask is not None:
        scores = scores.masked_fill(mask, float("-inf"))
    out = torch.softmax(scores.float(), dim=-1).to(x.dtype) @ v
    out = out.transpose(1, 2).contiguous().view(b, t, c)
    return out @ wo
```

改成 GQA 只要把 $K,V$ 的头数降到 $H_{\mathrm{kv}}$，对它们做 `repeat_interleave` 去对齐 $Q$ 的头，softmax 公式不变。缩放不用改，$d_h$ 也别拆两次。

## 同一场连着问 DPO/PPO

DPO 先把每个 token 的 logp 加总成整段回答的 logp，再算

$$
L=-\log\sigma\bigl(\beta(\log\pi_\theta(y_w)-\log\pi_\theta(y_l)-\log\pi_{\mathrm{ref}}(y_w)+\log\pi_{\mathrm{ref}}(y_l))\bigr).
$$

PPO 的目标是 $\min(\rho A,\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A)$，见 `code-ppo-clip`。三题连着问的时候，Attention 十分钟内把主干写完，DPO/PPO 的公式口头写，二分另起一题写。白板时间别耗在 attention 的 dropout 细节上。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先把四个投影矩阵设为单位阵、输入设为零，输出必须全零。再用两 token 的因果 mask，改变未来 token 后，第一个位置的输出应保持不变。

```python
x = torch.zeros(1, 2, 4)
w = torch.eye(4)
torch.testing.assert_close(mha(x, w, w, w, w, 2), x)
x = torch.tensor([[[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0]]])
mask = torch.ones(2, 2, dtype=torch.bool).triu(1)
a = mha(x, w, w, w, w, 2, mask)
changed = x.clone()
changed[:, 1] = 100
b = mha(changed, w, w, w, w, 2, mask)
torch.testing.assert_close(a[:, 0], b[:, 0])
assert torch.isfinite(a).all()
print("simple tests passed")
```

## 追问

**缩放为什么除以 $\sqrt{d_h}$？**
点积的方差随 $d_h$ 变大。不缩放的话，softmax 的概率很容易集中到一个位置上。

**GQA 改公式了吗？**
没改。只改了 K/V 头怎么组织，以及 cache 的体积。

**换成 cross-attention 呢？**
$T_q\neq T_k$，scores 变成 $[B,H,T_q,T_k]$，mask 按 key 侧的 padding 来。

**和 MLA 什么关系？**
MLA 压的是表示的维度，头数没少，见 `arch-mla`。百川如果只问 MHA/GQA，就别主动展开矩阵吸收。

**DPO 的 logp 在哪一层加？**
在序列级求和（或者平均，要和实现保持一致）。每个 token 各算一个 DPO loss 是错的。

## 真题记录

这题来自牛客候选人原帖：百川智能大模型算法日常实习二面，原帖没写面试时间，帖子发布于 2026-02-13，可信度 A。原话是 **“手写 multi-head attention 机制”**；同一场还有 **“手写一下 dpo 和 ppo”**、**“手写梯度下降法的二分”**。

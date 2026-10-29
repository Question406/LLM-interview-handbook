---
id: pdd-attention-handwrite
section: coding
order: 180
level: A
title: 拼多多应用开发：手写 Attention 时要写出哪些形状和 Mask？
quick: >-
  投影 $Q,K,V$，reshape 成 $[B,H,T,d_h]$，算 $QK^\top/\sqrt{d_h}$，softmax 前加因果 /
  padding mask，再乘 $V$ 拼头。边写边口述 broadcast 形状，调一个 `nn.MultiheadAttention` 交差是不够的。
tags:
  - PDD
  - Attention
  - Coding
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 拼多多大模型应用开发一面凉经
    url: 'https://www.nowcoder.com/feed/main/detail/f87fcee060ea404ba99a20245f746e60'
    type: candidate-first-hand
---

## 题目描述

手写一个 multi-head self-attention 函数 `mha(x,wq,wk,wv,wo,n_heads,mask=None)`，返回 attention 输出，不直接调用封装好的 multi-head attention 模块。面经只披露“手写 attention”，以下完整接口为手册重构练习约定。

### 接口、输入与输出要求

输入均为同设备、同浮点类型的 PyTorch 张量：`x` 为 `[B,T,C]`，四个无偏置投影矩阵均为 `[C,C]`，按 `x @ w` 的方向使用。`n_heads=H` 是正整数且整除 C，每头维度 `dh=C/H`。B、T、C 均为正。

每个头应返回缩放点积 attention：查询、键、值来自对应投影；attention 分数为查询与键点积除以 `sqrt(dh)`；概率在 key 维 normalization。各头按原顺序拼接后应用输出投影。输出形状为 `[B,T,C]`。

可选布尔 `mask` 能广播到 `[B,H,T,T]`，**True 表示禁止访问该 key**。本函数不自动加因果 mask，需要时由调用者提供。每个 query 至少能访问一个 key。softmax 使用 float32 计算后转回输入类型；不含 dropout。实现应保留自动求导。

### 示例

```text
输入：x=[[[1,0],[0,1]]]，四个矩阵均为2×2单位阵
n_heads=1，mask=[[False,True],[False,False]]
输出（约）：[[[1,0],[0.330238,0.669762]]]

输入：x为形状[1,2,4]的全零张量，四个矩阵为4×4单位阵，n_heads=2
输出：形状[1,2,4]的全零张量
```

## 解题思路与参考答案

手写 attention 的顺序是投影、拆头、算缩放点积、softmax 前加 mask、乘 $V$、拼头、输出投影，边写边把每一步的形状和 mask 的 broadcast 说出来。

这是拼多多大模型应用开发一面的题，来自牛客候选人原帖，可信度 A。面试时间原帖没写，帖子发布于 2026-03-29，原话就是**“手写 attention”**。常见翻车是调 `nn.MultiheadAttention` 交差，或者因果 / padding 的 True-False 弄反。同一面可能接着写 cross entropy，见 `pdd-ce-handwrite`，两题都要能独立写完。形状和 `deepseek-mha-handwrite` 一样，拼多多这边要的是口述 broadcast。

## 白板顺序与形状

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

`Linear` 得到 $QKV$ → `view/transpose` 到 $[B,H,T,d_h]$ → scores $[B,H,T,T]$ → 加 $M$ → softmax（fp16 升 fp32）→ 乘 $V$ → merge heads → 输出投影。$M$ 常见两种形状，padding 是 $[B,1,1,T]$，因果是 $[1,1,T,T]$，都靠 broadcast 加到 scores 上。因果 mask 把未来位置设成 `-inf`，padding 把 key 侧的 pad 设成 `-inf`，两者可以相加。

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
    return out.transpose(1, 2).contiguous().view(b, t, c) @ wo
```

`view` 之前要 `contiguous`。GQA 只改 $K,V$ 的头数，公式骨架不变。

## 易错点与同面的 cross entropy loss（CE）

bool mask 的 `True` 是「盖住」还是「可见」，要说清楚，并且和 `masked_fill` 的用法一致。整行全被 mask 时 softmax 会出 NaN。应用岗也要能讲 KV cache：逐 token 生成（decode）时每步 $T_q=1$，$K,V$ 沿 $T$ 增长。dropout 不是重点。cross entropy 要用 logsumexp，别先 softmax 再 log，见 `pdd-ce-handwrite`。

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

**mask 是加还是 fill？**
加 $M$（0 / `-inf`）和 `masked_fill` 等价，别又加又 fill 做两次。

**缩放除的是 $d$ 还是 $d_h$？**
头维 $d_h$。除 $d_{\mathrm{model}}$ 会缩得太小。

**batch 里句子长度不同怎么办？**
padding 加 mask，或者用 varlen 实现。白板上用 pad 就行。

**和 FlashAttention 什么关系？**
数学相同。现场写显式矩阵就可以。

**GQA 要改 softmax 吗？**
不用。repeat K/V 头之后还是同一个公式。

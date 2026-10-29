---
id: deepseek-mha-handwrite
section: coding
order: 200
level: S
title: DeepSeek 向算法笔试/面试：手写完整 Multi-Head Attention（含形状与 Mask）
quick: >-
  按投影 $Q,K,V$、拆头、缩放点积、加因果 / padding mask、数值稳定的 softmax、拼头、输出投影的顺序写。代码里交代清
  contiguous/view 的 applicability，再说明 GQA 只是改了 K/V 的头数组织。
tags:
  - DeepSeek
  - Attention
  - Coding
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DeepSeek 大模型算法岗笔试面经分享（练习向整理）
    url: 'https://www.nowcoder.com/discuss/913482312753418240'
    type: secondary
  - title: Attention Is All You Need
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
---

## 题目描述

使用传入的投影矩阵实现 multi-head self-attention，支持调用者指定的 attention mask，不调用现成的 multi-head attention 模块。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `mha(x,wq,wk,wv,wo,n_heads,mask=None)`。x 为[B,T,C]；四个权重均[C,C]，采用 x@W 的右乘约定；C 能被`n_heads`整除。mask 若提供，须可广播到[B,`n_heads`,T,T]，True 表示屏蔽。

### 输出与约束

返回[B,T,C]。每头按 sqrt(C/`n_heads`)缩放点积分数，对可见 key 做 softmax，组合 value 后拼接并右乘 wo。默认无因果 mask、无 bias、无 dropout；需要因果限制时由调用者提供上三角 True 的 mask。保证每 query 至少一个可见 key。

### 示例

```text
B=T=n_heads=1,C=2，x=[[[1,2]]]，wq=wk=wv=wo=2×2单位矩阵
唯一key权重为1，输出 [[[1,2]]]。
```

## 解题思路与参考答案

手写 MHA 按这个顺序来：投影 $Q,K,V$，拆成多头，算缩放点积，加 mask，softmax，乘 $V$，拼头，最后输出投影。数学骨架就是缩放点积加 mask 再加权 $V$，GQA、MLA 都不动这一块。

这题来自公开的练习向整理帖，按 DeepSeek 系算法岗的高频手撕来准备，所以标的是 `realInterview: false`。常见翻车是公式背得出、形状写错，或者把 GQA/MLA 说成改了 softmax。MLA 是另一条压缩轴，见 `arch-mla`；本题先把 MHA 写完。对照的真题手撕见 `baichuan-mha-handwrite`、`pdd-attention-handwrite`。

## 公式与白板检查

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

动笔前过一遍这几件事：$d_{\mathrm{model}}$ 能被 $H$ 整除；$M$ 能 broadcast 到 $[B,H,T_q,T_k]$；因果是下三角可见，padding 的 bool 语义别弄反；fp16 的 softmax 先转 float；cross-attn 时 $T_q\neq T_k$。`view` 之前先 `contiguous`，免得 stride 处理错了、输出悄悄不对。

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
    attn = torch.softmax(scores.float(), dim=-1).type_as(v)
    out = (attn @ v).transpose(1, 2).contiguous().view(b, t, c)
    return out @ wo
```

形状边写边说：$x[B,T,C]$ → 投影后仍是 $[B,T,C]$ → `view` 成 $[B,T,H,d_h]$ → `transpose` 成 $[B,H,T,d_h]$ → scores $[B,H,T,T]$ → 加权 $V$ 后拼回 $[B,T,C]$。

## GQA / MLA：压缩轴不同，softmax 不变

GQA 让 $H_{\mathrm{kv}}\lt H$，K/V 的头少，Q 那边做 `repeat_interleave`，KV cache 从 $O(H d_h)$ 降到 $O(H_{\mathrm{kv}} d_h)$。MLA 是沿表示维压成 latent，RoPE 拆开处理，推理时吸收矩阵，见 `arch-mla`。面试里一句话就够：两者都是为了逐 token 生成（decode）时的带宽，压缩的轴不一样。别在 MHA 代码里假装写了 MLA。

数值上还有一处：mask 之后如果一整行全是 `-inf`，softmax 会变 NaN，比如 padding 全被 mask 的 query，要对这一行单独保护。Dropout 如果要写，打在 attn 权重上，只在训练态开。

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

**为什么要除以 $\sqrt{d_h}$？**
点积的方差和 $d_h$ 成正比，不缩放 softmax 就饱和了。

**mask 加在 softmax 前还是后？**
前。softmax 之后再加，已经分配好的 attention 权重就改不了了。

**GQA 要改 $d_h$ 吗？**
不用。头维仍是 $d_{\mathrm{model}}/H_{\mathrm{q}}$，只是 K/V 的头少了。

**能用 `reshape` 代替 `transpose` 吗？**
不能。`view` 不会交换 $H$ 和 $T$ 的内存含义，必须先 transpose 再 contiguous。

**和 FlashAttention 什么关系？**
数学一样，只是分块做在线 softmax。白板上还是写显式的 scores，并说明生产用融合核。

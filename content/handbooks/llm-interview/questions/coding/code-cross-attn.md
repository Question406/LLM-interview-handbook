---
id: code-cross-attn
section: coding
order: 53
level: A
title: 手写 Cross-Attention：decoder $Q$ 打 encoder 的 $K,V$，cache 缓的是 encoder
quick: "$Q$ 来自 decoder，$K,V$ 来自 encoder，scores 形状是 $[B,H,T_q,T_k]$。这一层不加因果 mask，只 mask encoder 的 padding；encoder 的 $K,V$ 算一次就缓存起来，整个 decode 过程都不变。"
tags:
  - CrossAttention
  - EncoderDecoder
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 题目描述

实现多头交叉注意力：query 来自一段序列，key/value 来自另一段序列，各 query 可读取全部有效 key。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `cross_attn(q,k,v,key_valid=None)`。q 为 [B,H,Tq,D]，k、v 为 [B,H,Tk,D]；Tq 与 Tk 可以不同。`key_valid` 为可选 [B,Tk] 布尔张量，True 表示保留。

### 输出与约束

返回 [B,H,Tq,D]，使用缩放点积注意力，缩放因子为 1/sqrt(D)。不施加因果限制；无有效 key 的 query 输出全零。数值计算应稳定，输入为合法同设备浮点张量。

### 示例

```text
B=H=D=Tq=1，Tk=2
q=[[[[0]]]], k=[[[[0],[0]]]], v=[[[[2],[4]]]]
无 mask 时输出 [[[[3]]]]；key_valid=[[True,False]] 时输出 [[[[2]]]]。
```

## 解题思路与参考答案

Cross-attention 的 $Q$ 来自 decoder，$K,V$ 来自 encoder，所以 K/V 的长度和来源都和当前序列无关。这层只需要 mask 掉 encoder 的 padding，不加因果 mask；encoder 的 $K,V$ 算一次就缓存，decode 全程不变。decoder 自己的自注意力还是要因果的，见 `code-attention`。

比如翻译时 encoder 读完一整句原文，decoder 每生成一个译文 token，都拿新的 $Q$ 去看这同一份 encoder 的 K/V，原文没有「未来」可言，所以不需要上三角 mask。

## 形状

encoder 只跑一次：$X_{\mathrm{enc}}\to K,V$，缓存成 `[B, H, Tk, Dh]`。decoder 每步：$X_{\mathrm{dec}}\to Q$，形状 `[B, H, Tq, Dh]`；输入预填充（prefill，即处理输入并建立缓存）时 $T_q$ 是目标长度，逐 token 生成（decode）时 $T_q=1$。$QK^\top$ 的形状是 `[B, H, Tq, Tk]`。

$$
\mathrm{Cross}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+\mathrm{mask}_{\mathrm{enc}}\Big)V.
$$

```python
import math
import torch

def softmax_stable(x, dim=-1):
    z = x.float() - x.float().amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    return (p / p.sum(dim=dim, keepdim=True)).nan_to_num(0.0).to(x.dtype)

def cross_attn(q, k, v, key_valid=None):
    # q: [B,H,Tq,D]；k,v: [B,H,Tk,D]；key_valid: [B,Tk], True=有效 encoder token
    scores = q @ k.transpose(-1, -2) / math.sqrt(q.size(-1))
    if key_valid is not None:
        scores = scores.masked_fill(~key_valid[:, None, None, :], float("-inf"))
    return softmax_stable(scores, dim=-1) @ v
```

encoder 的 padding 不管在左边还是右边，都靠 `key_valid` 处理。用 GQA 时 encoder 侧的 $H_{\mathrm{kv}}$ 可以更少，先 `repeat_kv` 再算，见 `code-gqa`。多模态里 vision encoder 输出的 token 数就是 $T_k$，decode 时图像那一侧的 cache 全程不变。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

query 长度 1、key 长度 2，专门覆盖交叉注意力长度不同的情况。Q/K 全零时平均得到 3；屏蔽第二个 key 后得到 2，全屏蔽则得到零且不能出现 NaN。

```python
q, k = torch.zeros(1, 1, 1, 1), torch.zeros(1, 1, 2, 1)
v = torch.tensor([2., 4.]).view(1, 1, 2, 1)
torch.testing.assert_close(cross_attn(q, k, v), torch.tensor([[[[3.]]]]))
torch.testing.assert_close(cross_attn(q, k, v, torch.tensor([[True, False]])), torch.tensor([[[[2.]]]]))
out = cross_attn(q, k, v, torch.tensor([[False, False]]))
assert torch.isfinite(out).all()
torch.testing.assert_close(out, torch.zeros_like(out))
print("simple tests passed")
```

## 追问

**encoder 要加 RoPE 吗？**
自注意力那层要。cross-attn 的 $Q$ 用 decoder 的位置，$K$ 用 encoder 的位置，两边的位置空间不一样，所以有的实现在 cross 这层不加 RoPE。

**cache 会随 decode 变吗？**
encoder 的 KV 不变，变的是 decoder 自注意力那份 cache。

**和 prefix LM 有什么区别？**
prefix LM 是同一条序列，前半段双向、后半段因果，只是 mask 不同；cross-attention 面对的是两条序列。

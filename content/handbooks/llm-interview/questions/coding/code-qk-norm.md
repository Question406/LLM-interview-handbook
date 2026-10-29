---
id: code-qk-norm
section: coding
order: 47
level: A
title: 手写 QK-Norm：RMSNorm 必须在 RoPE 之前
quick: >-
  投影得到 $Q,K$ 之后，先对每个 head 的 $d_h$ 维做 RMSNorm，再做 RoPE，最后打 $QK^\top$。顺序反过来的话，norm 会重新缩放已经转过的二维对，把旋转毁掉。Qwen2.5 / 部分 Llama 变体用它压 attention logits 的尺度，$V$ 通常不 norm。
tags:
  - QK-Norm
  - RoPE
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Query-Key Normalization for Transformers
    url: https://arxiv.org/abs/2302.05442
    type: primary
---

## 题目描述

实现对 attention 的 Q 和 K 分别 normalization 后再进行 RoPE 旋转的接口。此题明确采用 rotate-half 布局：最后一维的前半、后半相互配对，而不是相邻 even/odd 维配对。

### 接口与张量

`qk_norm_rope(q,k,q_norm,k_norm,cos,sin)` 接收同形状 `[B,H,T,Dh]` 的 q、k，Dh 为偶数。`q_norm` 和 `k_norm` 是沿最后一维工作的 RMSNorm 模块；cos/sin 可广播到输入形状，包含每个位置的旋转系数。返回 `(q_out,k_out)`，形状各与输入相同。

RMSNorm 不减均值，分母为最后一维平方均值加 eps 后的平方根，并乘可学习权重。旋转对 `[x1,x2]` 两半的定义为 `x*cos + [-x2,x1]*sin`。normalization 与旋转的先后次序属于题目要求。

### 示例

```text
q=[1,2,3,4]（其余维度均为1），cos全为1、sin全为0
q_out -> q_norm(q)
仅调用apply_rope_half，cos全为0、sin全为1时：
[1,2,3,4] -> [-3,-4,1,2]
```

输入保证形状相容，练习只要求有限输入上的结果与 backpropagation。

## 解题思路与参考答案

QK-Norm 的顺序是先 norm 再转：$Q,K$ 投影出来以后，先对每个 head 的 $d_h$ 维做 RMSNorm，再做 RoPE，然后才打 $QK^\top$。顺序反过来，norm 会重新缩放已经转过的二维对，旋转就被毁了。

为什么要加它？普通 MHA 的 $QK^\top/\sqrt{d}$ 在深网络里还是可能漂。QK-Norm 让每个 query、key 向量的模都在 $\sqrt{d_h}$ 这个量级，logits 就稳得多。Qwen2.5 和部分 Llama 变体用它来压 attention logits 的尺度。写的时候和 `code-rmsnorm`、`code-rope` 拼在一起：

$$
Q=\mathrm{RoPE}(\mathrm{RMSNorm}(X W_Q)),\quad
K=\mathrm{RoPE}(\mathrm{RMSNorm}(X W_K)),\quad
V=X W_V.
$$

RMSNorm 的轴是 $d_h$，权重形状 `[Dh]`。可以所有 head 共享一份，也可以每个 head 一份，先写共享的。

```python
import torch
import torch.nn as nn


class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps, self.weight = eps, nn.Parameter(torch.ones(dim))

    def forward(self, x):
        z = x.float()
        y = z * torch.rsqrt(z.pow(2).mean(-1, keepdim=True) + self.eps)
        return self.weight * y.to(x.dtype)


def apply_rope_half(x, cos, sin):
    x1, x2 = x.chunk(2, -1)
    return x * cos + torch.cat((-x2, x1), -1) * sin


def qk_norm_rope(q, k, q_norm, k_norm, cos, sin):
    # q,k: [B,H,T,Dh]；先 norm 再转
    q, k = q_norm(q), k_norm(k)
    return apply_rope_half(q, cos, sin), apply_rope_half(k, cos, sin)
```

decode 时新 token 只对自己的 $q_t,k_t$ 做 norm 和 RoPE。cache 里存的是已经转过的 $K$，别再 norm 一遍。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

cos=1、sin=0 时旋转是恒等变换，输出应等于单独 RMSNorm。再把 cos=0、sin=1，直接检查 rotate-half 的符号与两半顺序。

```python
q, k = torch.tensor([[[[1.0, 2.0, 3.0, 4.0]]]]), torch.ones(1, 1, 1, 4)
qn, kn = RMSNorm(4), RMSNorm(4)
cos, sin = torch.ones(1, 4), torch.zeros(1, 4)
a, b = qk_norm_rope(q, k, qn, kn, cos, sin)
torch.testing.assert_close(a, qn(q))
torch.testing.assert_close(b, kn(k))
torch.testing.assert_close(
    apply_rope_half(q, sin, cos), torch.tensor([[[[-3.0, -4.0, 1.0, 2.0]]]])
)
print("simple tests passed")
```

## 追问

**$V$ 为什么不 norm？**
logits 的尺度由 $Q,K$ 决定。$V$ 是被加权的内容，再 norm 会把值通路的幅度掐掉。

**和 QK clip、softcap 有什么关系？**
都是在压 logits。softcap 加在 scores 上，见 `code-softcap`；QK-Norm 改的是向量本身。

**用 LayerNorm 行不行？**
RMSNorm 就够了，少算一个均值。写成 LN 也能跑，但和常见的 checkpoint 对不上。

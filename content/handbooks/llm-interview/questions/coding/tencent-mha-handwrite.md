---
id: tencent-mha-handwrite
section: coding
order: 212
level: A
title: 腾讯混元一面：手写 Multi-Head Attention 要交代哪些形状？
quick: >-
  $QKV$ 投影后拆成 $[B,H,T,d_h]$，scores 是 $[B,H,T,T]$，加因果 / padding mask 再 softmax，乘 $V$ 后拼头。混元常把它和括号生成连着问，形状和 `contiguous` 比会调库更关键。
tags:
  - Tencent
  - Hunyuan
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

## 题目描述

实现 PyTorch 模块 `MHA(d,h)`，其 `forward(x,pad=None)` 返回带因果限制的多头自注意力输出。候选人记录只披露手写 MHA，以下类名、参数名和掩码规则为手册重构练习约定。

`d`、`h` 是正整数且 d 能被 h 整除。模块持有 `qkv=nn.Linear(d,3*d,bias=False)` 和 `o=nn.Linear(d,d,bias=False)` 两个投影层，供调用者设置和训练权重。`x` 为浮点张量 `[B,T,d]`，B、T 为正，输入与参数设备和类型相符。

输出形状为 `[B,T,d]`：每头维度为 d/h，注意力为缩放点积注意力，归一化在 key 维进行。位置 t 只能访问位置不大于 t 的 key。可选 `pad` 为 `[B,T]` 布尔张量，**True 表示有效 key**；其余 key 在所有 query 中均不可见。不要求将 padding query 的输出清零。保证每个 query 至少存在一个未屏蔽的历史 key。

softmax 应以 float32 计算再转换回投影张量类型；不包含偏置或 dropout，支持自动求导。不能直接用封装好的 MHA 替代手写运算。

### 示例

```text
设置：d=2，h=1，qkv的Q、K、V三个权重块和o权重均为2×2单位阵
输入：x=[[[1,0],[0,1]]]，pad=None
输出（约）：[[[1,0],[0.330238,0.669762]]]

相同设置，pad=[[True,False]]
输出：[[[1,0],[1,0]]]
```

## 解题思路与参考答案

先把形状链说清楚，$[B,T,D]\to[B,H,T,d_h]\to[B,H,T,T]$，再拼回 $[B,T,D]$；中间在 softmax 前加因果和 padding mask，拼头前记得 `contiguous`。混元一面要的就是形状、mask 语义和 `contiguous`，调一个 `F.scaled_dot_product_attention` 交差，库名说得再对也拿不到分。

这是腾讯混元大模型日常实习一面的题，来自牛客候选人原帖，可信度 A，原话是**“手写 Multi-Head Attention”**。同场常接着考括号生成，十分钟内要先画张量再写主干。骨架和 `code-attention` / `deepseek-mha-handwrite` 相同，但这场绑定混元，先保证能把形状链口述完再拼回。

## 形状与 mask 先画出来

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

动笔前过一遍：$d_{\mathrm{model}}$ 能被 $H$ 整除，$d_h=D/H$。$Q,K,V$ 投影后 `view(B,T,H,d_h).transpose(1,2)` 得到 $[B,H,T,d_h]$，scores 是 $[B,H,T,T]$。因果 mask 常用上三角 `True` 表示「看不见」，`masked_fill` 成 $-\infty$；padding 如果是 `True=valid`，就对 key 维用 `~mask[:,None,None,:]` broadcast。True/False 和加减别弄反，softmax 之后再置零会破坏归一化。Cross-attn 时 $T_q\neq T_k$，别写死成方阵。拼头时写 `transpose(1,2).contiguous().view(B,T,D)`，少了 `contiguous`，`view` 要么报错，要么发生没被及时发现的错位。fp16 的 softmax 升 fp32 再写回，同时避免一行全 $-\infty$ 出 `NaN`。

## 短实现：十分钟主干

```python
import math, torch, torch.nn as nn

class MHA(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        assert d % h == 0
        self.h, self.dh = h, d // h
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.o = nn.Linear(d, d, bias=False)

    def forward(self, x, pad=None):  # pad: [B,T] True=valid
        B, T, D = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dh).unbind(2)
        q, k, v = [t.transpose(1, 2) for t in (q, k, v)]
        s = q @ k.transpose(-1, -2) / math.sqrt(self.dh)
        s = s.masked_fill(torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), 1), float("-inf"))
        if pad is not None:
            s = s.masked_fill(~pad[:, None, None, :], float("-inf"))
        y = (torch.softmax(s.float(), dim=-1).to(q.dtype) @ v)
        return self.o(y.transpose(1, 2).contiguous().view(B, T, D))
```

如果追问 GQA，就只把 $K,V$ 的头数改成 $H_{\mathrm{kv}}$，$Q$ 按组共享，softmax 公式不动；MLA 再压到 latent，见 `arch-mla`。和括号题连着问时，Attention 先交主干，细节口头补。

## 简单测试怎么写

把参考实现与以下测试按顺序放进 solution.py，运行 python3 solution.py。数值测试使用同一 PyTorch 环境，浮点数用带容差的比较；通过后输出 simple tests passed。

用两个 head、三个 token 的小模型检查输出形状和因果性。改变最后一个 token 不应改变前两个位置的输出。

```python
torch.manual_seed(7)
model = MHA(4, 2).eval()
x = torch.randn(1, 3, 4)
y = x.clone()
y[:, 2] += 10
assert model(x).shape == x.shape
torch.testing.assert_close(model(x)[:, :2], model(y)[:, :2])
print("simple tests passed")
```

## 追问

**mask 为什么必须在 softmax 前加？**
softmax 之后再置零就不归一化了；填 $-\infty$ 才能让被屏蔽位置的概率严格为 0。

**`contiguous` 为什么必要？**
`transpose` 之后内存不连续，`view` 需要连续布局，否则形状对了值是错的。

**GQA 改哪里？**
只改 $K,V$ 头数的组织，缩放点积不动。混元一面先讲形状，后提库。

**一行全被 mask 怎么办？**
softmax 前检查有没有有限的 logit，免得 `NaN` 传进输出投影。

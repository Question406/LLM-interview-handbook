---
id: tencent-mha-handwrite
section: coding
order: 212
level: A
title: 腾讯混元一面：手写 Multi-Head Attention 要交代哪些形状？
quick: >-
  $QKV$ 投影后拆成 $[B,H,T,d_h]$，scores 为 $[B,H,T,T]$，加因果 / padding mask 再
  softmax，乘 $V$ 后拼头。混元常和括号生成连问，形状与 `contiguous` 比调用库更关键。
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

## 真题记录

- 公司：腾讯 · 混元
- 岗位：大模型日常实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手写 Multi-Head Attention”**

错法：调用 `F.scaled_dot_product_attention` 交差。混元一面要的是形状、mask 语义和 `contiguous`，不是库名。同场常接着括号生成，十分钟内必须先画张量再写主干。骨架与 `code-attention` / `deepseek-mha-handwrite` 相同，但这场绑定混元，先保证能口述完 $[B,T,D]\to[B,H,T,d_h]\to[B,H,T,T]$ 再拼回。

## 形状与 mask 必须先画

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

检查清单：$d_{\mathrm{model}}$ 整除 $H$，$d_h=D/H$。$Q,K,V$ 投影后 `view(B,T,H,d_h).transpose(1,2)` 得到 $[B,H,T,d_h]$；scores 为 $[B,H,T,T]$。因果 mask 常用上三角 `True` 表示「看不见」，`masked_fill` 成 $-\infty$；padding 若 `True=valid`，则对 key 维 `~mask[:,None,None,:]` broadcast。True/False 与加减不要反：softmax 后再置零会破坏归一化。Cross-attn 时 $T_q\neq T_k$，不要写死方阵。拼头后 `transpose(1,2).contiguous().view(B,T,D)`：没有 `contiguous`，`view` 会报错或 silently 错位。fp16 softmax 升 fp32 再回写，避免一行全 $-\infty$ 出 `NaN`。

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

若追问 GQA：只改 $K,V$ 头数为 $H_{\mathrm{kv}}$，对 $Q$ 按组共享，softmax 公式不动。MLA 再压到 latent，见 `arch-mla`。和括号题连问时，Attention 先交主干，细节放口头。

## 追问

- **mask 为何必须在 softmax 前？** 后置零不归一化；$-\infty$ 才能让被屏蔽位置概率严格为 0。
- **`contiguous` 为什么必要？** `transpose` 后内存不连续，`view` 需要连续布局，否则形状对了值错。
- **GQA 改哪？** 只改 $K,V$ 头数组织，不改缩放点积。混元一面先形状后库。
- **一行全 mask 怎么办？** softmax 前检查有限 logit，避免 `NaN` 传进输出投影。
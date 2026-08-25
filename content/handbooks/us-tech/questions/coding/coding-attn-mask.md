---
id: coding-attn-mask
section: coding
order: 34
level: A
title: 白板：因果、padding、文档边界合成一张注意力 mask
quick: >-
  三个 keep 条件同时真才允许看：因果 $j\le i$、key 不是 pad、query 与 key 同一 `doc_id`。合成加性
  bias，形状 `[B, 1, T, S]`；decode 是 `[B, 1, 1, S]`。非法位填 $-\infty$，不要填 $0$，不要写成 HTML 比较符。
tags:
  - Coding
  - Attention Mask
  - Packed Sequences
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: FlashAttention (varlen / cu_seqlens API)
    url: https://github.com/Dao-AILab/flash-attention
    type: primary
  - title: Attention is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 题怎么来的

OpenAI Transformer debug 和 Meta packing 训练都会问 mask 漏了一层会怎样。只写因果：pad
位置仍吃质量，后一篇文档会读前一篇。只写 padding：未来 token 泄漏。三件要 **按位与** 成一张 keep，再变成加性
$-\infty$。文档 packing 的 `cu_seqlens` 路径见 `coding-packed-lm`；滑窗是第四个条件，见
`coding-swa-mask`。公式里比较只用 $\le$、$\lt$，不要写看起来像标签的字符。

## 三个 keep，一个 bias

Query 位 $i$、key 位 $j$（可以是绝对 `position_ids`，packed 行内则是列下标）。允许注意力当且仅当：

$$
(j\le i)\ \wedge\ \mathrm{valid}(j)\ \wedge\ \mathrm{doc}(i)=\mathrm{doc}(j).
$$

$\mathrm{valid}(j)$ 来自 padding：右 pad 时 $j$ 超过真实长度则假；左 pad 时前缀 pad 假。Query 侧若也有
pad，那些行的 logits 本来就会被 ignore，但 key 侧必须挡，否则有效 query 会看进 pad 的
$k$。$\mathrm{doc}$ 是文档 id；单文档常数，条件永远真。

实现上构造 bool `keep`，形状能广播到 scores `[B, H, T, S]`：常见写成 `[B, 1, T, S]`。然后

$$
\mathrm{bias}=\begin{cases}0 & \text{keep}\\ -\infty &
\text{otherwise.}\end{cases}
$$

加到 $QK^\top/\sqrt{D}$ 之后、softmax 之前。填 $0$ 等于没 mask。Decode：$T=1$，bias `[B, 1,
1, S]`，$i$ 取当前绝对位置，不要用 $0$ 去和 $j$ 比因果。

ALiBi 是另一张加性表，和这张 **相加**（非法位已经是 $-\infty$，再加斜率无所谓），见 `coding-alibi`。不要用乘法把两张
mask 混成 $0/1$ 再当 logits。

```python
import torch

def compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k):
    # q_pos: [T], k_pos: [S]
    # key_valid: [B, S] True=非 pad
    # doc_q: [B, T], doc_k: [B, S]
    causal = k_pos[None, :] <= q_pos[:, None]          # [T, S]
    pad = key_valid[:, None, None, :]                    # [B, 1, 1, S]
    same = doc_q[:, None, :, None] == doc_k[:, None, None, :]  # [B, 1, T, S]
    keep = causal[None, None] & pad & same
    bias = torch.zeros(keep.shape)
    return bias.masked_fill(~keep, float("-inf"))


def decode_attn_bias(s_len, key_valid, doc_ids):
    # 新 query 在列 s_len-1；doc_ids: [B, S]
    q_pos = torch.tensor([s_len - 1])
    k_pos = torch.arange(s_len)
    doc_q = doc_ids[:, s_len - 1 : s_len]
    return compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_ids)
```

`cu_seqlens` 把不同样本切成独立序列时，**不必**再物化跨样本的 pad mask；文档边界若已变成「一条 varlen
序列一篇文档」，`same doc` 也可以省。稠密 `[B, T, S]` 只是白板契约。全行 $-\infty$ 会让 softmax 变
NaN，ignore 掉的 query 行要在 CE 侧 mask，或保证至少有一个 keep（自己看自己）。

## 漏哪一层，现象不一样

漏因果：训练 loss 好看，生成却像看未来，或和 prefix LM 搞混。漏 padding：pad id 的 $k$ 参与归一化，短句被拉向 pad
向量，batch 里长度差越大越歪。漏文档边界：下一篇的答案抄上一篇，packing
越狠「数据泄漏」越像能力。这三件事不要用同一张「attention_mask=`[B, S]`」糊弄：那张表往往只编码 padding，SDPA 还要另开
`is_causal`。

FlashAttention 的 dense mask 接口吃 bool 或 additive；varlen 接口用 cu 切样本，因果在 kernel
内按局部下标做。白板先写稠密三件与，再提生产路径不物化 $T\times S$。比较写 $\le$、$\lt$，不要写看起来像标签的尖括号包字母。

## 追问

- **为什么比较写 $\le$ 不写尖括号标签？** 构建器会把 尖括号包住字母 一类当 HTML。下标用 $1:t-1$，比较用 $\le$、$\lt$。
- **query 的 pad 要不要进 keep？** 挡 key 是正确性；query 行全 $-\infty$ 会 NaN。Pad query 的损失本来 ignore，softmax 可跳过或先保证对角
  keep。
- **decode 还要文档 id 吗？** 要。生成落在第二篇时，不能让 key 扫到第一篇，除非训练就允许跨文档。
- **和滑窗一起？** `keep` 再与 $i-W \lt j$。四件仍是一张 bias，见 `coding-swa-mask`。

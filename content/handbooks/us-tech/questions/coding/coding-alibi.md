---
id: coding-alibi
section: coding
order: 28
level: A
title: 白板：ALiBi 斜率加到 scores 上，decode 用 cache 长度当 query 位
quick: >-
  每个 head 一个正斜率 $m_h$，因果下给 $q_i^\top k_j$ 加 $m_h(j-i)$。距离越远越负。Decode 的 $i$ 是
  cache 下标，key 是 $0..S-1$，bias 形状 `[1, H, 1, S]`。不旋 $q,k$，也不加到 $V$ 上。
tags:
  - Coding
  - ALiBi
  - Position Bias
  - HuggingFace
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Train Short, Test Long — Attention with Linear Biases Enables Input Length Extrapolation
    url: https://arxiv.org/abs/2108.12409
    type: primary
  - title: BLOOM — A 176B-Parameter Open-Access Multilingual Language Model
    url: https://arxiv.org/abs/2211.05100
    type: secondary
  - title: Hugging Face ALiBi implementation notes
    url: https://huggingface.co/docs/transformers/en/model_doc/bloom
    type: secondary
---

## 题怎么来的

Press et al. 的 ALiBi 是 BLOOM / MPT 一类模型的位置方案：没有位置 embedding，也没有
RoPE，把线性偏置直接加在注意力 logits 上。HuggingFace 实现岗和「手写 MHA」follow-up 会问斜率怎么来、decode
时距离怎么算。Llama 默认是 RoPE，见 `coding-rope`；本题不要把两种位置编码叠在同一套 $q,k$ 上，除非评委明确给了混合架构。

## 斜率乘相对距离

Head $h$ 的斜率 $m_h>0$。Query 位 $i$、key 位 $j$，在因果已经成立（$j\le i$）时：

$$
\mathrm{score}_{h,i,j}=\frac{q_{h,i}^\top k_{h,j}}{\sqrt{D}}+m_h(j-i).
$$

$j-i\le 0$，所以偏置非正：越远的 key 越被压。几何斜率：head 数是 $2$ 的幂时，$m_h=1/2^{h\cdot 8/H}$（8
头就是 $1/2,1/4,\ldots$）。非 2 幂时 HuggingFace 用「先填最近 2 幂，再插值」，白板先写 2 幂，提一句读实现。

偏置形状要对 scores `[B, H, T, S]` 广播。Prefill：`[1, H, T, S]`，其中 $T=S$，$i,j$ 都是
`arange`。Decode：$T=1$，$i=$ 当前 cache 下标（长度 $S$ 时 $i=S-1$ 若 $S$ 已含新
token），$j=0..S-1$，bias `[1, H, 1, S]`。**不要**用 $i=0$ 去减 $j$，那样最近的 key 反而最负。

ALiBi 加在 **scores**，softmax 之前。不改 $q,k$ 的内容，不碰 $V$。未来位置仍要
$-\infty$，否则线性偏置只是让未来「比较负」，不是禁止。

```python
import torch

def alibi_slopes(n_heads):
    ratio = 2 ** (-8 / n_heads)
    return ratio ** torch.arange(1, n_heads + 1, dtype=torch.float32)


def alibi_score_bias(q_pos, s_len, slopes):
    # q_pos: [T]; slopes: [H] -> [1, H, T, S]
    k_pos = torch.arange(s_len)
    dist = (k_pos[None, :] - q_pos[:, None]).float()  # j - i
    causal = k_pos[None, :] <= q_pos[:, None]
    bias = slopes[:, None, None] * dist[None, :, :]
    bias = bias.masked_fill(~causal[None, :, :], float("-inf"))
    return bias.unsqueeze(0)


def decode_alibi(cache_len, slopes):
    s = cache_len + 1
    q_pos = torch.tensor([cache_len])
    return alibi_score_bias(q_pos, s, slopes)
```

`cache_len` 与 RoPE 那题同一约定：新 token 的绝对下标，见 `coding-rope-cache`。单测：固定
$q,k$，ALiBi 只改 softmax 权重，不改 $V$ 本身；距离相同的 $(i,j)$ 跨 prefill / decode 必须同一偏置。

## 外推和 RoPE 的对比

ALiBi 的卖点是训练短、测试长：偏置随距离线性走，没有 cos/sin 表的 `max_seq` 越界。它 **不是** 免费的无限上下文：窗口外的
key 仍在 softmax 里吃质量，只是很小；和硬滑窗 `coding-swa-mask` 不同。BLOOM 训练长度和推理长度仍要在评测里报清楚。

GQA / MQA 时斜率按 **query head** 数生成，每个 $h_q$ 一条 $m_h$；KV head 被若干 $q$ 共享，但 bias
仍在 $QK^\top$ 的 head 维上，形状跟 `[B, H_q, T, S]` 走。不要给 $H_{\mathrm{kv}}$ 建一套更短的斜率再
repeat 错轴，repeat 规则见 `coding-gqa-repeat`。

斜率可以不进优化器：论文是固定几何序列。改成可学会换外推行为，那就不是原版 ALiBi。head 数不是 $2$ 的幂时 HuggingFace 用「先填最近 $2$ 幂再插值」，白板先写 $2$ 幂，提一句去读实现。

## 追问

- **为什么是 $m(j-i)$ 不是 $m|i-j|$ 再另乘因果？** 因果下两者差一个符号约定。必须 $j\le i$ 时偏置 $\le 0$。把绝对值加到未来位置上会让非法 key 变正。
- **decode 用 $S$ 还是 $S-1$？** 和「这一步的 $K$ 有没有已经 concat 进去」焊死。concat 之后
  $S_{\mathrm{new}}=S_{\mathrm{old}}+1$，query 位是 $S_{\mathrm{new}}-1$。
- **能和 RoPE 同时用吗？** 公开 BLOOM 不用 RoPE。叠两套位置信号要有训练依据，白板默认二选一。
- **斜率要不要学？** 论文是固定几何序列，不进优化器。改成可学会换外推行为，那就不是原版 ALiBi。

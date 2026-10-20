---
id: code-beam-search
section: coding
order: 55
level: A
title: 手写 Beam Search 一步：累计 logprob、flatten top-k、回指父 beam
quick: "每步把 $K$ 条 beam 的累计 logprob 加到 $[B,K,V]$ 的 log-softmax 上，flatten 成 $[B,KV]$ 取 top-$K$。下标整除 $V$ 得父 beam，模 $V$ 得新 token。"
tags:
  - BeamSearch
  - Decoding
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Generation strategies (Hugging Face)
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: primary
---

和 greedy / sampling 对比着考。greedy 是 $K=1$ 的 beam。常见误区是：每条 beam 各自 argmax（那是 $K$ 路独立贪心，不会交叉）；或在 fp32 中连乘概率，导致数值下溢。蚂蚁原题用树来讲，见 `ant-beam-search-pytorch-tree`；本题写向量化的一步。

## 一步

已有 `beam_logp` `[B,K]` 和本步 `logp` `[B,K,V]`：

$$
\mathrm{cand}_{b,k,v}=\mathrm{beam}_{b,k}+\log p_k(v),\qquad
\text{对 } KV \text{ 个候选取 top }K.
$$

```python
import torch

def beam_step(logp, beam_logp, beam_size):
    # logp: [B, K, V]；beam_logp: [B, K]
    cand = beam_logp.unsqueeze(-1) + logp
    B, K, V = cand.shape
    scores, idx = cand.reshape(B, K * V).topk(beam_size, dim=-1)
    prev, tok = idx // V, idx % V
    return scores, prev, tok
```

`prev` 用来 gather 每条新 beam 的 KV cache / 前缀 token。结束条件：出现 EOS 的 beam 冻结分数，继续扩没结束的；最后在结束的 beam 里取分数最高的。长度惩罚（GNMT）：

$$
\mathrm{score}=\frac{\sum_t\log p_t}{(5+T)^\alpha/(6)^\alpha}.
$$

$\alpha=0.6$ 常见。不除长度会偏向短句。

## 追问

- **和 sampling？** beam 是 MAP 近似，多样差；sampling 跟训练分布。对话生成现在多用 sample。
- **diverse beam？** 把 $K$ 分成小组，组间加相异惩罚。手写先把普通 beam 写对。
- **和 KV cache？** $K$ 条序列各有一份 cache。父 beam 被两条子节点共用时要 CoW，见 `code-paged-kv-cow`。

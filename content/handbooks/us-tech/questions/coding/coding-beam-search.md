---
id: coding-beam-search
section: coding
order: 12
level: A
title: 白板：beam search vs greedy vs sampling，长度惩罚
quick: >-
  Greedy 每步 $\arg\max$，beam 保留 $k$ 条前缀按累计 log-prob 扩展，sampling 从 $\pi$ 里抽。比长度要用
  $\mathrm{len}^\lambda$ 惩罚，短句 raw log-prob 天生更大。$k=1$ 就是 greedy。
tags:
  - Coding
  - Beam Search
  - Decoding
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Google's Neural Machine Translation System
    url: https://arxiv.org/abs/1609.08144
    type: primary
  - title: Generation strategies (Hugging Face)
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: secondary
---

## 题怎么来的

解码三件套：greedy、beam、sampling。Anthropic / Apple 会让你对比，而不是默写 `generate` 参数。翻译、代码补全常 beam；聊天常用温度 + nucleus，见 `coding-topk-nucleus`。长度惩罚来自 GNMT（Wu et al.）：不惩罚的话短句横扫。

## 三条路差在决策，不差在模型

Greedy：每步取当前条件概率最大的 token。$k=1$ 的 beam。快，容易死循环、重复。

Sampling：从 $\pi_T$ 或 nucleus 里抽。多样，无搜索保证。温度、top-k、top-p 改的是每步分布，不是搜索宽度。

Beam：$k$ 条活前缀。每步把每条扩到词表，累计

$$
s(y_{1:t})=s(y_{1:t-1})+\log\pi(y_t\mid y_{1:t-1}),
$$

在 $k\cdot V$ 个候选里取 top-$k$。分数必须在 **log 域加**，概率连乘会下溢。EOS 进 finished，不再扩展；没写 EOS 的留在活跃集。最终先比 finished；全部顶到 `max_len` 仍无 EOS 才回退活跃 beam。

```python
import torch

def beam_expand(logp, scores, k, eos_id):
    # logp: [k, V], scores: [k]
    cand = scores[:, None] + logp
    topv, topi = torch.topk(cand.reshape(-1), k)
    vsz = logp.size(1)
    parent = torch.div(topi, vsz, rounding_mode="floor")
    token = topi % vsz
    done = token == eos_id
    return parent, token, topv, done


def length_penalty(logp_sum, length, alpha=0.6):
    # GNMT: ((5 + len) / 6) ** alpha
    lp = ((5.0 + length) / 6.0) ** alpha
    return logp_sum / lp


def pick_finished(finished, alpha=0.6):
    if not finished:
        return None
    best = max(finished, key=lambda x: length_penalty(x[0], x[1], alpha))
    return best
```

`parent` 用来复制 token 前缀和 reorder KV cache。Cache 不按 parent gather，子节点会读错历史。Batch 内各样本的 beam 独立，pad 位置不要扩展。

## 长度惩罚：短句的 log-prob 和更大

$\sum\log\pi$ 随长度变负，短句往往分数更高。GNMT：

$$
\mathrm{score}(y)=\frac{1}{\bigl((5+|y|)/6\bigr)^\alpha}\sum_t\log\pi(y_t\mid y_{1:t-1}),
$$

$\alpha\in[0.6,1]$ 常见。$\alpha=0$ 等于不惩罚。也可以在 EOS 后停止扩展，避免「再补几个 token 刷分」。重复 n-gram 屏蔽、坏 token mask 加在打分之前。

和 sampling 一起用（beam 里每步先 nucleus）会改分布，不再是经典 beam。面试先写标准 beam；产品上聊天很少 beam，翻译 / 结构化输出才值。Apple 端侧 $k>1$ 等于 decode 带宽乘 $k$，GQA 再乘回去见 `meta-llama-gqa`。

## 追问

- **为什么不用概率相乘？** 长序列下溢成 0。log 加法稳定，和 CE 的 log-softmax 一致。
- **最终为什么不看活跃集合？** 没写 EOS 的前缀和完成句不可比。无完成句才回退。
- **$k$ 越大一定越好？** 不一定。大 $k$ 更偏短、更匀质；还要长度惩罚和多样性约束。带宽随 $k$ 涨。

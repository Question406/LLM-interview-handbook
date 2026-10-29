---
id: openai-attention-sink
section: openai
order: 22
level: A
title: OpenAI：滑窗 / streaming attention 为什么开头几个 token 不能扔
quick: >-
  流式生成时可以保留最初几个 attention sink，再加最近窗口，避免驱逐句首后 attention 分布突然变化。StreamingLLM 默认保留
  4 个 sink，显存保持在 $O(k+W)$；中间事实已被丢掉，长距离检索仍需要其他记忆。
tags:
  - OpenAI
  - Attention
  - Streaming
  - KV cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Efficient Streaming Language Models with Attention Sinks
    url: 'https://arxiv.org/abs/2309.17453'
    type: primary
  - title: Mistral 7B (sliding window attention)
    url: 'https://arxiv.org/abs/2310.06825'
    type: primary
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: 'https://arxiv.org/abs/2104.09864'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

对长度 $T$ 的流式生成，我会保留最初 $k$ 个 attention sink，再保留最近 $W$ 个 token 的 KV。比如问题只依赖最近两句，满 attention 训练的模型删掉句首后却立刻输出异常，这通常不能只用“忘了早期事实”解释：那些位置承担了稳定 attention 分布的作用。

StreamingLLM（Xiao et al.）系统展示了这个现象。很多 sink 是 `bos` 或没有多少词义的占位，关键在位置一直可见。第 $t$ 个 query 的 attention 是

$$
a_t = \mathrm{softmax}\bigl(q_t K_{0:t}^\top / \sqrt{d_k}\bigr),\qquad \sum_s a_{t,s}=1.
$$

softmax 要让总和为 1，没有额外“off”logit 时，当前 query 用不到的 attention 质量仍得落到某个 key。训练中位置 0 几乎对所有 query 可见、梯度稳定，前几列就承担了这个作用。attention 图里，深层及头的后半可看到初始 token 占很大质量，中间位置较淡。

从 cache 删除 $0..t-W$ 后，这些质量重新分给窗口里的 key，$v$ 的加权和随之改变，哪怕最近上下文足够，perplexity 也可能异常。StreamingLLM 默认保留 $k=4$ 个初始 sink，第一个尤其关键，再加最近 $W$ 个 KV，中间丢弃，显存由 $O(T)$ 变为 $O(k+W)$。

这个设计维持局部生成稳定，中间事实既然不在 cache，就无法再读出第 100 万个 token 的内容。长距离检索需要长窗训练、RAG 或其他记忆。Mistral 在训练时就用 SWA，窗口外的可见性假设不同，窗口内也可能有局部 sink；开始设计前要先问 checkpoint 是满 attention 训练还是窗口训练。

位置处理也要明确。按本题给定的实现约定，留下的 key 使用原绝对位置做 RoPE；重新编成 $0..W-1$ 会改变相对差 $m-n$，即使 shape、normalization 和范数正常，输出也对不齐。sink 的 $K,V$ 沿时间维放在窗口前，key 长 $k+W$，decode query 长 1。sink、窗口和当前 token 按时间顺序拼好，就能沿用因果 mask。

pin 系统提示不能替代保留初始 sink：$k=4$ 即使没有系统提示也有效，长系统提示被保留而位置 0 被丢弃仍可能出问题。给 softmax 常驻 sink logit、让质量流向“虚无”的 off-by-one 一类变体，改变的是函数，需与 StreamingLLM 的 cache 驱逐方案分开讲。这是公开系统题。

## 追问

**只留 $k=1$ 行吗？**
第一个通常是主 sink，论文用 4 更稳，具体仍要看 attention 图。

**能和 RoPE 外推一起用吗？**
可以。sink 管驱逐后的分布，RoPE 基频管距离编码，位置处理先保证一致。

**很长的 prefill 怎么处理？**
保留初始 sink 和尾部窗口，中间 KV 可以不保存；这与 PagedAttention 的块分配分开处理。

**为什么不等于长上下文训练？**
中间内容已经不可见，只维持局部 attention 的稳定，无法恢复被删的事实。

相关：`openai-kv-cache-impl`、`openai-long-ctx-train`、`openai-rope-offset`、[[coding-rope-cache]]（代码里按绝对位置查 cos/sin 表）

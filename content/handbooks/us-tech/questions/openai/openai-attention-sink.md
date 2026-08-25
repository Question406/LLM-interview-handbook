---
id: openai-attention-sink
section: openai
order: 22
level: A
title: OpenAI：滑窗 / streaming attention 为什么开头几个 token 不能扔
quick: >-
  Softmax 必须把质量和归一成 1，没有「不看」选项时，多余质量会堆到一直可见的开头 token 上，它们变成
  attention sink。滑窗推理若把 sink 和中间历史一起丢掉，分布被重写，PPL 崩。StreamingLLM 的修法是保留少量
  sink（常是 4 个）加最近窗口，并且不要重编号 RoPE。
tags:
  - OpenAI
  - Attention
  - Streaming
  - KV cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Streaming Language Models with Attention Sinks
    url: https://arxiv.org/abs/2309.17453
    type: primary
  - title: Mistral 7B (sliding window attention)
    url: https://arxiv.org/abs/2310.06825
    type: primary
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

Serving 想做无限长对话：KV cache 不能随 $T$ 线性涨到爆。直觉是滑窗——只留最近 $W$ 个 $K,V$。对 **训练时看得到全文** 的模型，这个直觉是错的。StreamingLLM（Xiao et al.）把现象钉死：丢掉句首几个 token 之后，即使窗口里还有很多最近上下文，困惑度也会炸。OpenAI 的推理岗会把它和 KV cache 实现放在一起问，cache 形状见 `openai-kv-cache-impl`。

这不是「开头语义更重要所以不能扔」。很多 sink 是 `bos` 或几乎没有词义的占位。扔它们，扔的是 softmax 的垃圾桶。

## 为什么质量和会涌向位置 0

第 $t$ 个 query 的注意力是

$$
a_t = \mathrm{softmax}\bigl(q_t K_{0:t}^\top / \sqrt{d_k}\bigr),\qquad \sum_s a_{t,s}=1.
$$

当前 token 并不需要把质量认真分给所有历史。没有额外的「off」logit 时，用不掉的质量必须落到某个 key 上。训练里位置 0 几乎对每个 query 可见，梯度也稳定，于是前几列变成全局的 dump。注意力图上你会看到：深层、头的后半，初始 token 吃掉很大一块质量，中间 token 反而淡。

滑窗若从 cache 里删掉 $0..t-W$，等于突然拿走 dump。softmax 把那块质量重新分给窗口内还在的 key，相对强度全变，$v$ 的加权和不是「略少一点历史」，是 **另一种分布**。所以失败模式不是「早期事实忘了」，是 **立刻胡言**，哪怕问题只依赖最近两句。

StreamingLLM 的修法很土，也因此好记：

- cache 里永远留 $k$ 个 sink（论文默认 $k=4$，第一个尤其关键）；
- 再留最近 $W$ 个 token 的 KV；
- 中间的全部丢掉。

显存从 $O(T)$ 变成 $O(k+W)$。这不是把窗口训到无限长，也不是针在干草堆里还能抄出第 100 万个 token 的事实。它是 **流式生成不崩**。真要长距离检索，还得靠训练长窗、RAG 或其它记忆，见 `openai-long-ctx-train`。

和 **训练时就用滑窗**（Mistral 的 SWA）不是同一件事。那种模型从没假设能看见无限过去，窗口外本来就没有 dump 到句首的契约；即便如此，窗口内仍可能出现局部 sink。面试先问：这个 checkpoint 是满注意力训的，还是窗口训的。

## 位置编号不要跟着窗口重写

丢掉中间 KV 之后，剩下的 key 仍应带着 **原来的绝对位置** 去做 RoPE。若把窗口重新编成 $0..W-1$，相对差 $m-n$ 全变，和 `openai-rope-offset` 同一类 silently wrong：shape 对、softmax 仍归一、输出范数正常，只是和「不重编号」对不齐。StreamingLLM 明确保留初始位置下标。

实现上 sink 的 $K,V$ 沿时间维拼在窗口前面，attention 的 key 长度是 $k+W$（decode 一步时 query 长为 1）。因果性：sink 在过去，窗口是最近过去，当前 token 在末尾，不需要新发明一种 mask，只要 concat 顺序对。

错法：把 sink 理解成「重要 prompt 要 pin 住」。系统提示当然可以 pin，但 StreamingLLM 的 $k=4$ 即使不是系统提示也有效；反过来，只 pin 长系统提示而丢掉真正的位置 0，照样可能崩。另一个变体是给 softmax 加一个常驻的 sink logit（off-by-one 一类），让质量可以倒向「虚无」。那是改函数，不是改 cache 驱逐。可以说，但要标明不是 StreamingLLM 原文的驱逐策略。

## 追问

- **$k=1$ 够不够？** 往往第一个 token 已经是主 sink，论文用 4 更稳。要看注意力图，不要口头保证。
- **能和外推 RoPE 一起用吗？** 能，但是两件事：sink 管驱逐后分布还合不合法；RoPE 基频管距离编码。先保证不重编号。
- **prefill 很长怎么滑？** 仍然保留 sink + 尾部窗口；中间 prefill 的 KV 可以不留。这和 paged attention 的块分配正交。
- **为什么说不是长上下文训练？** 中间事实已经不在 cache 里，模型不可能读到。它只保证局部生成的注意力还像训练时那样有垃圾桶。

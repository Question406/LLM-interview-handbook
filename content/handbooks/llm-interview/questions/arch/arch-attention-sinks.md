---
id: arch-attention-sinks
section: arch
order: 20
level: A
title: Attention Sink 是什么？滑动窗口长上下文为什么不能简单删除最早 token？
quick: >-
  Attention sink 指部分模型会给开头少数 token 持续分配较大的 attention
  权重，哪怕它们没什么语义。滑动窗口直接把它们删掉，softmax normalization
  的范围变了，近期窗口里的权重跟着变，输出可能崩。流式方案因此固定保留少量 sink token，其余只缓存最近的窗口。
tags:
  - Long Context
  - Attention
  - KV Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: StreamingLLM / attention sinks
    url: 'https://arxiv.org/abs/2309.17453'
    type: legacy-reference
---

Attention sink 是指很多模型会把一部分 attention 权重固定压在开头几个 token 上，首 token、BOS 或特殊符号就算没什么语义，也会反复吸走较高的 attention mass。滑动窗口如果按 FIFO 把它们删了，softmax normalization 的范围突然变化，近期窗口里的权重也跟着变，输出就可能崩。所以流式方案会固定留下这几个 sink token，再对近期 token 做滑动缓存。

常有人以为开头 token 不能删，是因为它们语义最重要。实际情况往往相反，留着它们是为了稳住 attention 分布。无限流式输入下 KV cache 不能无限涨，这个问题才会冒出来。

## 为什么删了会崩

标准 attention 是

$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d}}\right)V.
$$

softmax 在整段可见的 key 上归一。许多 decoder 会把一部分质量沉在位置 $0$ 附近，相当于给分布加了一个稳定的偏置。StreamingLLM 观察到，即便这些位置几乎不带信息，去掉它们也会让后续步的 attention 形状突变。这和 RoPE 的相对旋转 $\langle R_m q,R_n k\rangle$ 依赖 $n-m$ 并不矛盾：sink 是模型学出来的分配习惯，跟位置编码本身无关。

## 工程上怎么做：留 sink，滑窗口

常见做法是固定保留开头 $s$ 个 sink token（或者专门训练的 sink），再只缓存最近 $w$ 个 token 的 KV，cache 就从 $O(T)$ 变成 $O(s+w)$。用专门 sink 符号的话，要和训练、位置编码策略匹配；推理时硬插一个训练没见过的 sink，效果不稳定。窗口内仍按因果 mask 算。sink 和窗口之间的中间历史被丢掉了，长程事实别指望 sink 记住，该检索就检索。

sink 是否存在、留多少、伤不伤任务质量，都要拿长流 eval 来定。不同模型、不同层沉在开头的程度不一样。它也和 MoE 路由无关，别和专家负载混在一起谈。

## 追问

**它和滑动窗口 attention 是一回事吗？**
不是。窗口 attention 在训练时就限制了可见范围；sink 是推理期的 eviction 策略，补的是一个按全上下文训出来的模型被截断之后的稳定性。

**和 KV quantization、GQA 谁先做？**
压缩和共享头省的是每个 token 的字节，sink 省的是 token 个数，两者可以叠加。但先要确认丢掉中间 token 对任务能不能接受。

**针-in-haystack 过了就算行？**
不够。还要看长对话、工具轨迹里指代是否仍然稳定，以及 sink 数量对延迟的边际收益。

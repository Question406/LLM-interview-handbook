---
id: arch-attention-sinks
section: arch
order: 20
level: A
title: Attention Sink 是什么？滑动窗口长上下文为什么不能简单删除最早 token？
quick: >-
  有些模型会持续给开头少数 token 分配注意力质量，即使它们语义信息很少。直接裁掉这些“锚点”可能让 softmax 分布失稳；streaming
  方案常保留少量 sink token 再滑动近期窗口。
tags:
  - Long Context
  - Attention
  - KV Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: StreamingLLM / attention sinks
    url: 'https://arxiv.org/abs/2309.17453'
    type: legacy-reference
---

陷阱是把 Attention Sink 说成「开头 token 语义最重要，所以不能删」。现象往往相反：首 token / BOS / 特殊符号即使语义贡献小，也可能反复吸走较高 attention mass。无限流式输入里 KV cache 不能无限涨，朴素 FIFO 丢掉这些锚点后，softmax 分母突然少了一块长期质量，近期窗口内的分数会被拧歪，输出可能崩溃。

## 现象与公式直觉

标准注意力

$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d}}\right)V.
$$

softmax 在整段可见 key 上归一。许多 decoder 会把一部分质量「沉」在位置 $0$ 附近，相当于给分布一个稳定偏置。StreamingLLM 的观察是：即便这些位置内容几乎无信息，去掉它们也会让后续步的注意力形状突变。这和 RoPE 的相对旋转 $\langle R_m q,R_n k\rangle$ 依赖 $n-m$ 不矛盾——sink 是分配习惯，不是位置编码本身。

## 工程策略：留 sink，滑窗口

常见做法：固定保留开头 $s$ 个 sink token（或专门训练的 sink），再只缓存最近 $w$ 个 token 的 KV。Cache 从 $O(T)$ 变成 $O(s+w)$。若用专门 sink 符号，需要和训练、位置编码策略匹配：推理时硬插一个训练没见过的 sink，效果不稳定。窗口内仍按因果 mask；sink 与窗口之间的「中间历史」被丢弃，长程事实不能指望 sink 记住，该检索就检索。

别过度泛化：是否存在、保留多少、是否伤任务质量，都要做长流 eval。不是所有模型、所有层都同样「沉」在开头。它也不是 MoE 路由问题，不要和专家负载混谈。

## 追问

- **和滑动窗口注意力是一回事吗？** 窗口注意力在训练就限制可见范围；sink 是推理期 eviction 策略，补的是「已经按全上下文训出来的模型」被截断后的稳定性。
- **和 KV quantization / GQA 谁先做？** 压缩和共享头省的是每 token 字节；sink 省的是 token 个数。两者可叠，但先确认丢掉中间 token 对任务是否可接受。
- **针-in-haystack 过了就算行？** 不够。要看长对话、工具轨迹里指代是否仍稳，以及 sink 数量对延迟的边际收益。

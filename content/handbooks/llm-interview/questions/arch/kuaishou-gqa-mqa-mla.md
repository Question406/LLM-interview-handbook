---
id: kuaishou-gqa-mqa-mla
section: arch
order: 142
level: A
title: 快手：除了 MHA，GQA / MQA / MLA 原理是什么？Decoder 的 QKV 从哪来？
quick: >-
  假设 attention 有 32 个 query heads。MHA 通常也有 32 组 K/V；GQA 可以让每 4 个 query heads
  共享一组 K/V，只存 8 组；MQA 则共享一组。
tags:
  - Kuaishou
  - GQA
  - KV Cache
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 快手日常实习大模型算法面经
    url: 'https://www.nowcoder.com/feed/main/detail/9d24592752804d2790557f81230df62d'
    type: candidate-first-hand
---

## 回答思路

> **问题与场景：** 假设 attention 有 32 个 query heads。
>
> **做法与原因：** Decode 时要不断读取历史 K/V，减少 KV heads 可以降低这部分 cache 与读取成本。
>
> **检查与取舍：** 我会用 KV heads、序列长度、batch 和 dtype 算 cache，再比较质量与实际 latency。

## 可以这样回答

假设 attention 有 32 个 query heads。MHA 通常也有 32 组 K/V；GQA 可以让每 4 个 query heads 共享一组 K/V，只存 8 组；MQA 则共享一组。

Decode 时要不断读取历史 K/V，减少 KV heads 可以降低这部分 cache 与读取成本。但 query heads 仍在，也不是整个模型的计算和显存都按相同比例下降。

我会用 KV heads、序列长度、batch 和 dtype 算 cache，再比较质量与实际 latency。MLA 使用不同的压缩表示，需要单独核算，不能只给它套一个 GQA head 数。

## 技术备查

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“问 kv cache 相关”**；**“decoder 的 qkv 输入分别来自哪”**；**“除了 MHA 还知道哪些(GQA MQA MLA)讲原理”**

GQA、MQA、MLA 省的都是 KV cache。MQA 和 GQA 减少 KV 的头数，MLA 沿表示维把 KV 压成低维 latent。decode 往往卡在读 KV 的带宽上，$T^2$ 的训练 FLOPs 不是这一步的瓶颈，所以别把它们说成「少算一点 attention」。回答时我会先讲 QKV 从哪来，再讲各自压的是哪条轴。

## Decoder 的 Q、K、V

autoregressive 走一步：当前隐状态 $h_t$ 乘 $W_Q$ 得到 $q_t$；历史的 $k_{1:t-1},v_{1:t-1}$ 已经在 KV cache 里，这一步只算 $k_t,v_t$ 并追加进去。Encoder-decoder 的 cross-attn 不一样，$q$ 来自 decoder，$k/v$ 来自 encoder 的记忆，cache 的是 encoder 那一侧，不会随 decode 步数增长。RoPE 加在 $q,k$ 上，$(R_t q_t)^\top(R_s k_s)=q_t^\top R_{s-t}k_s$；cache 里存旋转前还是旋转后的值，实现必须和推理一致。

## 三种省 cache 的切法

MHA 每个头都有独立的 KV，每个 token 大约存 $2 n_h d_h$，质量最好，cache 也最大。MQA 让所有 Q 头共享一对 KV，$n_{\mathrm{kv}}=1$，cache 最小，头之间的独立性也最差。GQA 取中间，$1\lt n_{\mathrm{kv}}\lt n_h$，几个 Q 头共享一组 KV，LLaMA / Qwen 常用这个中间点。

MLA（DeepSeek）换了一条轴，主要沿表示维压，不光是砍头数。隐状态先投到低维的 $c_t^{KV}=W^{DKV}h_t$，$d_c\ll n_h d_h$，RoPE 需要的部分再拆出一段短的 $k^R$。推理时用矩阵吸收，不必还原出全长的 K/V。它和 GQA 压的轴不同，见 `arch-mla`。

FFN 那一侧用 SwiGLU 还是 MoE，和 KV 布局互不相干：专家路由不会让 decode 的 cache 变小。

## 追问

**省的是计算还是字节？**
主要是字节。Prefill 仍然接近 $O(T^2 d)$；decode 省的是每一步读 cache 的字节数。

**GQA 能和 MLA 叠在一起吗？**
能设计组合，因为两者的轴不同。但 head、latent、RoPE 的维度都要重新定义，没法当两个开关随手一起打开。

**MQA 质量为什么容易掉？**
所有头抢同一份 $k,v$，表达容量不够。GQA 用分组把这部分容量买了回来。

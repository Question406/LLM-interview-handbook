---
id: jd-transformer-philosophy
section: arch
order: 190
level: A
title: 京东应用开发：Transformer 的优劣和「哲学」怎么讲，还关注过别的架构吗？
quick: >-
  哲学上，Transformer 用内容相关的软对齐：每个位置拿 query 去匹配所有 key 再加权 value，「对齐谁和谁」交给 attention
  去学，不用手写。优势是全局交互、训练可并行，代价是二次复杂度和位置外推。提 SSM / 线性 attention
  时要说清，它们换的是长序列效率，推理能力不会因此自动变强。
tags:
  - JD
  - Transformer
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 京东大模型应用开发 实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b'
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型应用开发实习
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“你对 Transformer 架构的优劣势及哲学理解是什么？关注过其他架构吗？”**

Transformer 的哲学一句话就够：用内容相关的软对齐，替代 RNN 的逐步压缩或者硬对齐。每个位置用 query 去匹配 keys，再对 values 加权，「对齐谁和谁」变成了可学习的 attention。别的架构我会提 SSM、线性 attention 和 MoE，但会说清它们各自换的是什么，不会说成 Mamba 全面取代。

举个例子，用户问「上周那单退货现在到哪了」。Transformer 可以在同一个窗口里把订单号、物流 token 和指代对上，不必像 RNN 那样把早先出现的订单号压进一个固定向量。可如果把整页无关的客服话术都塞进上下文，二次 attention 就会分散到噪声上。这时该做的是检索和状态外置，先换 Mamba 解决不了问题。电商应用岗的痛点也常在检索和工具，骨干倒在其次。

## 优势、代价和适用场景

$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d}}\right)V.
$$

优势是训练可并行，长程依赖不用经过一个固定的隐状态，生态也完整（RoPE、SwiGLU、MoE、KV cache）。代价是 $O(T^2 d)$ 的复杂度，逐 token 生成（decode）时要大量读取 KV 缓存，位置外推可能损失质量，对噪声上下文也敏感。所以它适合序列不太长、需要全局交互、又想吃现有预训练生态的场景。上下文到了几十万 token、推理要求极低延迟时，才值得认真看 SSM / 线性 attention；它们换来的是长序列效率，推理能力不会自动变强。

## 提其他架构，怎么说才不像背名词

Mamba 和线性 attention 把 $Q(K^\top V)$ 或递推状态做成近线性，换的是 throughput。MoE 把 FFN 稀疏化，$\sum_{i\in\mathrm{top}k} g_i E_i(x)$，换的是激活参数，attention 仍然可以是 dense。把「关注过其他架构」答成「Mamba 全面取代」是红旗，说关注过就行，别编没跑过的数字。被追问位置编码时，讲清 RoPE 的 $q^\top R_{n-m}k$、插值、窗口 attention 各自补的都是外推，attention 本身还在。

## 追问

**Decoder-only 和 Encoder-Decoder 的哲学一样吗？**
一样，都是软对齐。decoder-only 把「条件」也放进同一条因果序列，工程上更简单，代价是没了 cross-attention 那份显式记忆。

**为什么应用岗也问这个？**
考的是你会不会把上下文当垃圾桶。我会答到检索、工具和状态外置，不去背 Mamba 论文。

**MoE 算另一种哲学吗？**
算「算力分配」上的哲学，对齐方式没变，对齐靠的还是 attention。

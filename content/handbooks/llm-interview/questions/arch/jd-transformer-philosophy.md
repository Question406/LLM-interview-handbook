---
id: jd-transformer-philosophy
section: arch
order: 190
level: A
title: 京东应用开发：Transformer 的优劣和「哲学」怎么讲，还关注过别的架构吗？
quick: >-
  优势是全局交互与可并行训练；代价是二次复杂度和位置外推。哲学上它把「对齐谁和谁」变成可学习注意力，而不是手写对齐。其他架构提
  SSM / 线性注意力时，要说清它们换的是长序列效率，不是自动更强推理。
tags:
  - JD
  - Transformer
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东大模型应用开发 实习面经
    url: https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型应用开发实习
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“你对Transformer架构的优劣势及哲学理解是什么？关注过其他架构吗？”**

错法：把「哲学」答成空话，或把 Mamba 说成全面取代。哲学上一句就够：用内容相关的软对齐，替代 RNN 逐步压缩或硬对齐。每个位置用 query 去匹配 keys，再对 values 加权，把「对齐谁和谁」变成可学习注意力。
## 优势、代价、适用

$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d}}\right)V.
$$

训练可并行、长程依赖不必过固定隐状态、生态（RoPE、SwiGLU、MoE、KV cache）完整。代价是 $O(T^2 d)$、decode 吃 KV 带宽、位置外推不免费、对噪声上下文敏感。适用：序列不太长、需要全局交互、要吃现有预训练生态。上下文到几十万 token、推理要极低延迟时，才认真看 SSM / 线性注意力；它们换的是长序列效率，不是自动更强推理。

电商应用岗的痛点常是检索和工具，不是先换骨干。例如用户问「上周那单退货现在到哪了」：Transformer 可以在同一窗口对齐订单号、物流 token 和指代，不必像 RNN 把早期订单号压进固定向量。但若把整页无关客服话术都塞进上下文，二次注意力会分散到噪声上，这时该做检索和状态外置，而不是先换 Mamba。

## 其他架构怎么提才不像背名词

Mamba / 线性注意力：把 $Q(K^\top V)$ 或递推状态换成近线性，换吞吐。MoE：FFN 稀疏化，$\sum_{i\in\mathrm{top}k} g_i E_i(x)$，换的是激活参数，注意力仍可以是 dense。把「关注过其他架构」答成「Mamba 全面取代」是红旗；关注过即可，不要编没跑过的数字。追问位置编码时，说清 RoPE $q^\top R_{n-m}k$、插值、窗口注意力各自补的是外推，不是换掉注意力本身。

## 追问

- **Decoder-only 和 Encoder-Decoder 哲学一样吗？** 都是软对齐；decoder-only 把「条件」也放进同一条因果序列，工程更简单，交叉注意力的显式记忆没了。
- **为什么应用岗也问这个？** 考你会不会把上下文当垃圾桶。我会答到检索、工具、状态外置，不背 Mamba 论文。
- **MoE 算另一种哲学吗？** 算「算力分配」哲学，不是另一种对齐。对齐仍是注意力。

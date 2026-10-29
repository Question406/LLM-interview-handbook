---
id: ali-attention-math
section: arch
order: 11
level: S
title: 淘天校招：Transformer Attention 的本质是什么？（数学角度）
quick: "Attention 是内容寻址的软检索：用 query 去匹配 keys 得到一组权重，再对 values 加权求和，公式是 $\\mathrm{softmax}(QK^\\top/\\sqrt{d})V$。权重非负且和为 1，输出是 values 的凸组合，所以它在当前窗口里做的是软组合。"
tags:
  - Alibaba
  - Attention
  - 淘天
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

从数学上看，Attention 是一次内容寻址的软检索：用 query 去匹配所有 key 得到权重，再对 value 加权求和。淘天校招的白板上，我会先写公式，再讲直觉，最后接到 Agent 场景里窗口的局限（`ali-attention-agent-limit`）。

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V.
$$

## 公式说了什么

设序列长 $T$，$Q,K,V\in\mathbb{R}^{T\times d_k}$，那么 $QK^{\top}\in\mathbb{R}^{T\times T}$，形状是 $T\times T$，常有人说成 $d\times d$。softmax 沿 key 维做，权重非负且和为 1，所以输出是 values 的凸组合，每个位置拿到的是多个位置的加权混合，并没有硬选某一个。漏掉 softmax normalization，或者把它说成「全连接」，都是常见的错。

除以 $\sqrt{d_k}$ 是为了不让点积随维度变大，否则 softmax 进入饱和区，梯度消失。训练时用因果 mask 保证位置 $t$ 看不到未来：在 softmax 之前给未来位置加 $-\infty$，事后再去删权重是不对的。

直觉上，每个位置投影出 Q/K/V 三份：Q 是「我要找什么」，K 是「我能被怎样匹配」，V 是「我提供什么内容」。举个例子，句子里 "it" 的 query 会给 "the cat" 更高的权重，于是 "it" 的新表示主要由 "cat" 的 value 贡献。这和 RAG、工具检索在「寻址」思想上相通，机制却不一样：Attention 在当前序列内、可微、没有显式索引；检索增强生成（RAG）在外部语料上，过程可审计（`ali-rag-eval`）。

## 多头、KV cache、复杂度

多头是并行地在多个子空间里做 attention，每头有独立的 $W^Q,W^K,W^V$，最后拼回 $d_{\mathrm{model}}$，光把 $d$ 切成几段还不够。推理时 KV cache 缓存的是已经算过的 $K,V$，$T\times T$ 的 attention 矩阵不缓存。朴素实现的复杂度是 $O(T^{2}d)$。GQA/MQA 减的是 KV 头数，从而减 cache 带宽，cache 体积变成 $O(n_{\mathrm{kv}}Td_h)$，「Q 打 K、加权 V」这件事没变，见 `ali-arch-hotspots`。线性 attention 和 SSM 换掉的是那个二次项，「用内容选 value」的思想还在。

## 接到 Agent 时别停在公式

公式描述的是窗口内的软组合。多轮工具 JSON 一长，softmax 的权重会被大量噪声位置稀释，早先的约束（「别改价」）会被最新的 observation 盖住。所以我会这样收尾：Attention 解决的是当前上下文里的内容寻址，跨会话、要审计、要权限控制的状态必须放到模型外面。

通义方向常接着问 RoPE 的相对性。位置信息在旋转里，没有放在加性 bias 上，外推是另一个问题。

## 追问

**为什么要除以 $\sqrt{d_k}$？**
点积的方差随 $d_k$ 增大。不缩放的话 softmax 趋近 one-hot，梯度几乎为零。

**KV cache 存 attention 矩阵吗？**
不存。decoding 第 $t$ 步只需要新的 $q_t$ 和历史的 $K,V$。

**它和点积检索有什么差别？**
打分方式一样，都是 query-key 打分再加权 value。差别在于 Attention 可微、在序列内、带因果 mask，也没有倒排索引。

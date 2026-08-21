---
id: ali-attention-math
section: alibaba
order: 11
level: S
title: 淘天校招：Transformer Attention 的本质是什么？（数学角度）
quick: 用 query 去匹配 keys 得到权重，再对 values 加权求和，是内容寻址的软检索/软组合。$\mathrm{softmax}(QK^\top/\sqrt{d})V$。
tags:
  - Alibaba
  - Attention
  - 淘天
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

陷阱是把 Attention 说成「全连接」或漏掉 softmax 归一化，或把 $QK^{\top}$ 形状说成 $d\times d$。本质是内容寻址的软检索/软组合：用 query 匹配 keys 得到权重，再对 values 加权求和。淘天校招白板要先写公式再讲直觉，再接到 Agent 窗口局限（`ali-attention-agent-limit`）。

## 公式与凸组合

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V.
$$

设序列长 $T$，则 $Q,K,V\in\mathbb{R}^{T\times d_k}$，$QK^{\top}\in\mathbb{R}^{T\times T}$。softmax 沿 key 维，权重非负且和为 1，输出是 values 的凸组合，不是硬选一个位置。缩放 $\sqrt{d_k}$ 避免点积随维度增大、softmax 进入饱和（梯度消失）。训练用因果掩码保证位置 $t$ 看不到未来；掩码是加 $-\infty$ 再 softmax，不是事后把权重删掉。

每个位置投影为 Q/K/V：Q 是「我要找什么」，K 是「我能被怎样匹配」，V 是「我提供什么内容」。句子里 “it” 的 query 会给 “the cat” 更高权重，于是 “it” 的新表示主要由 “cat” 的 value 贡献。这和 RAG/工具检索在「寻址」思想上类似，但机制不同：Attention 在当前序列内、可微、无显式索引；RAG 在外部语料上、可审计（`ali-rag-eval`）。

## 多头、KV cache、复杂度

多头是并行多个子空间，不是简单把 $d$ 切段就完事：每头有独立 $W^Q,W^K,W^V$，再拼回 $d_{\mathrm{model}}$。推理时 KV cache 缓存的是已算过的 $K,V$，**不是**缓存 $T\times T$ 注意力矩阵。朴素实现复杂度 $O(T^{2}d)$。GQA/MQA 减的是 KV 头数从而减 cache 带宽，见 `ali-arch-hotspots`。线性注意力/SSM 换的是这条二次项，不是换掉「用内容选 value」的思想。

## 接到 Agent 时别停在公式

公式说的是窗口内软组合。多轮工具 JSON 一长，softmax 质量被噪声位置稀释，早先约束（「别改价」）会被最新 observation 盖住。所以白板收口应是：Attention 解决的是 **当前上下文里的内容寻址**；跨会话、可审计、可权限的状态必须外置。通义方向常接着问 RoPE 相对性——位置信息在旋转里，不在加性 bias 上，外推另说。GQA 把 KV 头共享，改的是 cache 体积 $O(n_{\mathrm{kv}}Td_h)$，不改「Q 打 K、加权 V」这件事。

## 追问

- **为什么除 $\sqrt{d_k}$？** 点积方差随 $d_k$ 增大；不缩放则 softmax 趋近 one-hot，梯度几乎为零。
- **Cache 存注意力矩阵吗？** 不存。解码第 $t$ 步只需新 $q_t$ 与历史 $K,V$。
- **和点积检索的差别？** 同一套「query–key 打分再加权 value」；差别是可微、在序列内、带因果掩码，没有倒排索引。

---
id: ali-attention-math
section: alibaba
order: 11
level: S
title: 淘天校招：Transformer Attention 的本质是什么？（数学角度）
quick: 用 query 去匹配 keys 得到权重，再对 values 加权求和，是内容寻址的软检索/软组合。softmax(QKᵀ/√d)V。
tags:
  - Alibaba
  - Attention
  - 淘天
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>用 query 去匹配 keys 得到权重，再对 values 加权求和，是内容寻址的软检索/软组合。softmax(QKᵀ/√d)V。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>把每个位置的表示投影为 Q/K/V：Q 表示“我要找什么”，K 表示“我能被怎样匹配”，V 表示“我提供什么内容”。缩放点积注意力输出是 values 的凸组合，本质是基于内容的软查找。</p>
<p>面试加分：提到因果掩码、多头并行子空间、以及与 RAG/工具检索在“寻址”思想上的类比（但机制不同）。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>

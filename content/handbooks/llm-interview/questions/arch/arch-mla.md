---
id: arch-mla
section: arch
order: 10
level: S
title: MLA 主要解决什么？和 GQA 有什么本质差别？
quick: >-
  MLA 通过低维 latent 压缩 K/V 相关信息来降低 KV Cache；GQA 则减少 KV head 数做 head sharing。二者都瞄准
  decode memory/bandwidth，但压缩轴不同。
tags:
  - MLA
  - DeepSeek
  - KV Cache
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>MLA 通过低维 latent 压缩 K/V 相关信息来降低 KV Cache；GQA 则减少 KV head 数做 head sharing。二者都瞄准 decode memory/bandwidth，但压缩轴不同。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>GQA 的思路是减少独立 K/V heads：H_kv↓。MLA 更接近把输入投到低维 latent c_t，缓存 latent，再通过可吸收/重构的投影参与 attention。</p><p>为什么不能“随便压成一个小向量”？因为 attention score 和 value aggregation 仍需要保留足够 query-dependent 信息；压缩维度太小会成为信息瓶颈。DeepSeek MLA 还把 RoPE 相关部分单独处理，并利用矩阵 absorption 减少 inference 时显式恢复大 K/V 的开销。</p><p>面试若追问 matrix absorption：核心是将相邻线性映射提前合并到 query/output projections，使低维 latent 可直接参与等价计算，而不是每 token 先 decode 回完整 K/V 再 attention。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>MLA 与 low-rank KV compression 的本质关系？</summary><div class="follow-answer"><p>都利用 K/V 表示可能存在低维结构；MLA 把这种低维 latent 直接纳入 attention parameterization 和 inference computation。</p></div></details><details class="followup"><summary>GQA 和 MLA 可以同时有吗？</summary><div class="follow-answer"><p>概念上是不同轴的设计，可以组合，但具体实现需要重新定义 head/latent projections；不是简单开两个 flag。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2412.19437" target="_blank" rel="noopener noreferrer">↗ DeepSeek-V3</a></div>

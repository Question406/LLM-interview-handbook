---
id: sys-online-softmax
section: systems
order: 18
level: S
title: FlashAttention 的 Online Softmax 怎么在分块后仍保持精确？
quick: >-
  每一行维护当前最大值 m 和归一化和 l。读到新 block 后更新 m′=max(m,m_block)，并把旧分子/分母按 exp(m−m′)
  重标定，再累加新 block；因此无需 materialize 全部 attention matrix。
tags:
  - FlashAttention
  - Softmax
  - 真实面经
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: 2025 美团大模型面经
    url: 'https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0'
    type: legacy-reference
  - title: FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>普通 attention 的瓶颈不仅是 FLOPs，还在于把 N×N score/probability 写回 HBM。FlashAttention 把 Q/K/V 分块，尽量在片上 SRAM 内完成计算，并通过 online softmax 合并每个 block 的结果。</p><ol><li>对已处理 block 保存行最大值 <b>m</b>、归一化和 <b>l</b> 与累积输出；</li><li>新 block 的最大值为 m<sub>b</sub>，令 m′=max(m,m<sub>b</sub>)；</li><li>把旧累计量乘 exp(m−m′)，新 block 按 exp(score−m′) 计算后再相加；</li><li>最后用累计分子除以 l，得到与整行 softmax 等价的精确结果。</li></ol><p>FlashAttention 不是近似 attention；核心是减少 HBM I/O，而非改变数学目标。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0" target="_blank" rel="noreferrer">2025 美团大模型面经</a><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noreferrer">FlashAttention</a></div></div>

---
id: sys-flash
section: systems
order: 6
level: S
title: FlashAttention 为什么更快？是不是近似 Attention？
quick: >-
  FlashAttention 是 exact attention。核心是 IO-aware tiling：避免完整 T×T attention matrix
  反复写入/读取 HBM，用片上 SRAM 分块并用 online softmax 维护精确结果。
tags:
  - FlashAttention
  - Attention
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>FlashAttention 是 exact attention。核心是 IO-aware tiling：避免完整 T×T attention matrix 反复写入/读取 HBM，用片上 SRAM 分块并用 online softmax 维护精确结果。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>标准实现逻辑上会 materialize S=QKᵀ、P=softmax(S) 等大矩阵。即使 FLOPs 不变，HBM traffic 会非常高。FlashAttention 把 Q/K/V 分块搬到 SRAM，边计算边维护每行 softmax 的 running max 和 normalization sum。</p><p>两个 block 的 softmax 可以通过新 max m=max(m_old,m_new) 重新缩放旧 partial sum，保证数值稳定且 exact。</p><p>所以 FlashAttention 主要降低 IO 与 intermediate memory，不是 sparse/linear approximation；长 sequence 下 T² intermediate 更大，收益通常更明显。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Online softmax 怎么保证 exact？</summary><div class="follow-answer"><p>维护每行 running maximum m 和 Σexp(score−m)，新 block 来时用 exp(m_old−m_new_global) 对旧和重新缩放，再累加新 block。</p></div></details><details class="followup"><summary>为什么 backward 也能省 memory？</summary><div class="follow-answer"><p>不保存完整 attention matrix，反向重新计算部分 scores/softmax statistics，用额外 compute 换 HBM memory。</p></div></details></div>
          <div class="pitfalls"><div class="mini-title">易错点</div><ul><li>说 FlashAttention 是近似 softmax 或改变 attention 结果。</li></ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noopener noreferrer">↗ FlashAttention</a></div>

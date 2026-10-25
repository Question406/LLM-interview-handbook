---
id: sys-flash
section: systems
order: 6
level: S
title: FlashAttention 为什么更快？是不是近似 Attention？
quick: "FlashAttention 计算精确的 attention，主要靠减少显存读写提速。它把 Q/K/V 分块搬进片上 SRAM，边算边用 online softmax 维护统计量，因此不用把完整 $T\\times T$ attention matrix 反复写回 HBM。"
tags:
  - FlashAttention
  - Attention
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>FlashAttention 计算精确的 attention，主要靠减少显存读写提速。它把 Q/K/V 分块搬进片上 SRAM，边算边用 online softmax 维护统计量，因此不用把完整 $T\times T$ attention matrix 反复写回 HBM。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>FlashAttention 快在少搬数据。标准实现会把 $S=QK^\top$、$P=\mathrm{softmax}(S)$ 这些大矩阵实际存下来，FLOPs 即使相同，也要反复读写 HBM。它把 Q/K/V 分块搬到 SRAM，边算边维护每行 softmax 已见到的最大值和归一化和。</p><p>新 block 到来时，先求新的最大值 $m=\max(m_{\mathrm{old}},m_{\mathrm{new}})$，再按这个最大值重新缩放旧的部分和。这样新旧 block 的统计量用同一标度相加，数值稳定，结果也与整行 softmax 等价。</p><p>因此它减少了 IO 和中间显存，仍保留精确 attention 的结果；sparse 或 linear attention 才会改变计算形式。序列越长，$T^2$ 中间量越大，这部分节省通常越明显。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Online softmax 怎么保证 exact？</summary><div class="follow-answer"><p>维护每行 running maximum $m$ 和 $\sum\exp(\mathrm{score}-m)$。新 block 来时用 $\exp(m_{\mathrm{old}}-m_{\mathrm{new\_global}})$ 对旧和重新缩放，再累加新 block。</p></div></details><details class="followup"><summary>为什么 backward 也能省 memory？</summary><div class="follow-answer"><p>不保存完整 attention matrix，反向时重新计算部分 scores 和 softmax 统计，用额外 compute 换 HBM memory。</p></div></details></div>
          <div class="pitfalls"><div class="mini-title">易错点</div><ul><li>说 FlashAttention 是近似 softmax 或改变 attention 结果。</li></ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noopener noreferrer">↗ FlashAttention</a></div>

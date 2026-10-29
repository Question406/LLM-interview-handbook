---
id: sys-flash
section: systems
order: 6
level: S
title: FlashAttention 为什么更快？是不是近似 Attention？
quick: >-
  普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。FlashAttention
  将计算分块，并在更快的片上存储里组织中间结果，减少这些往返。
tags:
  - FlashAttention
  - Attention
  - 口述改写 2026-10-28
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。</p>
<p><strong>做法与原因：</strong> Online softmax 让分块计算仍能组合成同一个 attention 结果；这不是把 attention 改成稀疏近似，也不意味着所有二次计算都消失。</p>
<p><strong>检查与取舍：</strong> 我会按序列长度、head dimension、dtype 和硬件测耗时与显存，并检查输出及 gradients。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。FlashAttention 将计算分块，并在更快的片上存储里组织中间结果，减少这些往返。</p>
<p>Online softmax 让分块计算仍能组合成同一个 attention 结果；这不是把 attention 改成稀疏近似，也不意味着所有二次计算都消失。浮点执行顺序不同，结果可能有数值误差。</p>
<p>我会按序列长度、head dimension、dtype 和硬件测耗时与显存，并检查输出及 gradients。速度提升依赖具体工作负载，不能背一个固定倍数。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>FlashAttention 计算精确的 attention，主要靠减少显存读写提速。它把 Q/K/V 分块搬进片上 SRAM，边算边用 online softmax 维护统计量，因此不用把完整 $T\times T$ attention matrix 反复写回 HBM。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>FlashAttention 快在少搬数据。标准实现会把 $S=QK^\top$、$P=\mathrm{softmax}(S)$ 这些大矩阵实际存下来，FLOPs 即使相同，也要反复读写 HBM。它把 Q/K/V 分块搬到 SRAM，边算边维护每行 softmax 已见到的最大值和 normalization 和。</p><p>新 block 到来时，先求新的最大值 $m=\max(m_{\mathrm{old}},m_{\mathrm{new}})$，再按这个最大值重新缩放旧的部分和。这样新旧 block 的统计量用同一标度相加，数值稳定，结果也与整行 softmax 等价。</p><p>因此它减少了 IO 和中间显存，仍保留精确 attention 的结果；sparse 或 linear attention 才会改变计算形式。序列越长，$T^2$ 中间量越大，这部分节省通常越明显。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Online softmax 怎么保证 exact？</summary><div class="follow-answer"><p>维护每行 running maximum $m$ 和 $\sum\exp(\mathrm{score}-m)$。新 block 来时用 $\exp(m_{\mathrm{old}}-m_{\mathrm{new\_global}})$ 对旧和重新缩放，再累加新 block。</p></div></details><details class="followup"><summary>为什么 backward 也能省 memory？</summary><div class="follow-answer"><p>不保存完整 attention matrix，反向时重新计算部分 scores 和 softmax 统计，用额外 compute 换 HBM memory。</p></div></details></div>
          <div class="pitfalls"><div class="mini-title">易错点</div><ul><li>说 FlashAttention 是近似 softmax 或改变 attention 结果。</li></ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noopener noreferrer">↗ FlashAttention</a></div>

</details>

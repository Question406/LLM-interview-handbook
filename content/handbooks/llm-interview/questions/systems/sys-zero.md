---
id: sys-zero
section: systems
order: 2
level: S
title: ZeRO-1/2/3 分别 Shard 什么？和 FSDP 什么关系？
quick: >-
  ZeRO-1 分片 optimizer states；ZeRO-2 再分片 gradients；ZeRO-3 再分片 parameters。FSDP 和
  ZeRO-3 思路非常接近：参数按 data-parallel ranks 分片，需要时 all-gather，梯度 reduce-scatter。
tags:
  - ZeRO
  - FSDP
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ ZeRO
    url: 'https://arxiv.org/abs/1910.02054'
    type: legacy-reference
  - title: ↗ 腾讯混元面经
    url: 'https://www.nowcoder.com/feed/main/detail/42fba762c2374372bcae72245f45f942'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>ZeRO-1 分片 optimizer states；ZeRO-2 再分片 gradients；ZeRO-3 再分片 parameters。FSDP 和 ZeRO-3 思路非常接近：参数按 data-parallel ranks 分片，需要时 all-gather，梯度 reduce-scatter。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Stage</th><th>参数 P</th><th>梯度 G</th><th>Optimizer O</th></tr></thead><tbody><tr><td>普通 DP</td><td>复制</td><td>复制</td><td>复制</td></tr><tr><td>ZeRO-1</td><td>复制</td><td>复制</td><td>分片</td></tr><tr><td>ZeRO-2</td><td>复制</td><td>分片</td><td>分片</td></tr><tr><td>ZeRO-3</td><td>分片</td><td>分片</td><td>分片</td></tr></tbody></table></div><p>理想情况下，跟参数相关的内存从 P+G+O 降到大约 (P+G+O)/N。但实际还有 activation、临时 all-gather buffer、碎片、通信 overlap 用的 buffer。</p><p>ZeRO-3 在某层 forward 前要 all-gather 所需参数，backward 后 reduce-scatter gradients。所以 memory 下去，communication 上来。FSDP 也做类似的 full-shard，只是 wrap 粒度、prefetch、mixed precision、CPU offload 这些实现上会有差别。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么不能只用 TP 替代 ZeRO？</summary><div class="follow-answer"><p>TP 解决的是单层上计算和参数怎么切，但 optimizer、gradient replica 和 data parallel 的内存是另一维问题。两者经常组合。</p></div></details><details class="followup"><summary>ZeRO-3 为什么可能慢？</summary><div class="follow-answer"><p>频繁 parameter all-gather、通信没法完全 overlap、layer wrap 太碎、网络慢、CPU offload，这些都会让它变慢。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/1910.02054" target="_blank" rel="noopener noreferrer">↗ ZeRO</a><a href="https://www.nowcoder.com/feed/main/detail/42fba762c2374372bcae72245f45f942" target="_blank" rel="noopener noreferrer">↗ 腾讯混元面经</a></div>

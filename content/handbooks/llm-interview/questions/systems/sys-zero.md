---
id: sys-zero
section: systems
order: 2
level: S
title: ZeRO-1/2/3 分别 Shard 什么？和 FSDP 什么关系？
quick: "ZeRO-1 分片 optimizer states，ZeRO-2 再分 gradients，ZeRO-3 再分 parameters，逐级减少数据并行里的状态副本。FSDP 的 full-shard 思路接近 ZeRO-3：用到参数时 all-gather，梯度通过 reduce-scatter 分片，代价是更多通信。"
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

<div class="quick"><div class="mini-title">30 秒回答</div><p>ZeRO-1 分片 optimizer states，ZeRO-2 再分 gradients，ZeRO-3 再分 parameters，逐级减少数据并行里的状态副本。FSDP 的 full-shard 思路接近 ZeRO-3：用到参数时 all-gather，梯度通过 reduce-scatter 分片，代价是更多通信。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Stage</th><th>参数 P</th><th>梯度 G</th><th>Optimizer O</th></tr></thead><tbody><tr><td>普通 DP</td><td>复制</td><td>复制</td><td>复制</td></tr><tr><td>ZeRO-1</td><td>复制</td><td>复制</td><td>分片</td></tr><tr><td>ZeRO-2</td><td>复制</td><td>分片</td><td>分片</td></tr><tr><td>ZeRO-3</td><td>分片</td><td>分片</td><td>分片</td></tr></tbody></table></div><p>这张表说明每一级新分片了什么。ZeRO-3 在理想情况下，把参数相关的内存从 P+G+O 降到约 (P+G+O)/N，N 是数据并行卡数。实际还要加 activation、临时 all-gather buffer、碎片，以及通信 overlap 用的 buffer，所以这个值并非最终峰值。</p><p>ZeRO-3 在某层 forward 前，先 all-gather 收齐需要的参数，backward 后再 reduce-scatter gradients。这样每卡少存副本，却增加了通信。FSDP 也采用类似的 full-shard 思路，具体差别在 wrap 粒度、prefetch、mixed precision 和 CPU offload 等实现。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么不能只用 TP 替代 ZeRO？</summary><div class="follow-answer"><p>TP 负责切开单层计算与参数；optimizer、gradient replica 和 data parallel 的状态副本仍需另外处理。因此 TP 和 ZeRO 经常一起使用。</p></div></details><details class="followup"><summary>ZeRO-3 为什么可能慢？</summary><div class="follow-answer"><p>每层频繁做 parameter all-gather，通信又无法完全 overlap 时，计算就要等。Layer wrap 太碎、网络慢或 CPU offload 的搬运也会增加耗时，所以省显存后仍要量 step time。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/1910.02054" target="_blank" rel="noopener noreferrer">↗ ZeRO</a><a href="https://www.nowcoder.com/feed/main/detail/42fba762c2374372bcae72245f45f942" target="_blank" rel="noopener noreferrer">↗ 腾讯混元面经</a></div>

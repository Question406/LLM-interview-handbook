---
id: fund-warmup
section: fundamentals
order: 8
level: A
title: Warmup 为什么有用？
quick: 训练初期 optimizer moments、激活/梯度统计与参数适配尚未稳定，大 LR 容易产生巨大更新；warmup 让 LR 从小到目标值逐步增加。
tags:
  - Optimization
  - Training
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>训练初期 optimizer moments、激活/梯度统计与参数适配尚未稳定，大 LR 容易产生巨大更新；warmup 让 LR 从小到目标值逐步增加。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>大 batch 会减少 gradient noise，使有效 step 更“硬”；深层 Transformer、Adam moments 尚未建立时尤其容易不稳。Warmup 不是理论必需的固定仪式，最佳长度与 initialization、optimizer、batch、architecture 相关。</p><p>Post-training/RL 中 warmup 也可避免初始 reward/advantage scale 尚未稳定时 policy 立即大幅 drift。</p></div>

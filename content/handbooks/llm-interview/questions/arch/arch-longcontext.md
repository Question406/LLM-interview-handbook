---
id: arch-longcontext
section: arch
order: 5
level: A
title: Position Interpolation、NTK-aware scaling、YaRN 大致在做什么？
quick: >-
  它们都在调整 RoPE 长位置的 position/frequency 映射：PI 压缩位置到训练区间，NTK-aware 方法更细地缩放频率，YaRN
  对不同频率与温度做更平滑的扩展。
tags:
  - Long Context
  - RoPE
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>它们都在调整 RoPE 长位置的 position/frequency 映射：PI 压缩位置到训练区间，NTK-aware 方法更细地缩放频率，YaRN 对不同频率与温度做更平滑的扩展。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Position Interpolation 最直接：把长 context 的 position index 按比例缩回训练时范围，减少完全 OOD 的相位，但会压缩近距离分辨率。</p><p>NTK-aware scaling 不是所有频率统一缩放，而是希望更合理保留不同尺度的相对位置行为；YaRN 进一步在频率区间上做分段/插值，并考虑 attention temperature。</p><p>面试重点通常不是背具体公式，而是能解释：<b>为什么简单改 max_position_embeddings 不够，以及这些方法都在重新定义长位置下的旋转频率。</b></p></div>

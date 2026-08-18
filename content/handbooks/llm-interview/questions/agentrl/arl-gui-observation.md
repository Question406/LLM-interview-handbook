---
id: arl-gui-observation
section: agentrl
order: 15
level: A
title: Browser / GUI Agent 的 Observation 应怎么表示？
quick: >-
  通常组合 screenshot/vision、DOM/accessibility tree、structured element metadata 与
  action history。纯截图泛化强但定位难；纯 DOM 高效但可能缺视觉状态；混合表示更实用。
tags:
  - GUI Agent
  - Observation
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>通常组合 screenshot/vision、DOM/accessibility tree、structured element metadata 与 action history。纯截图泛化强但定位难；纯 DOM 高效但可能缺视觉状态；混合表示更实用。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>关键 tradeoff：token/vision cost、可定位性、动态页面一致性、跨平台泛化。Element IDs 若每次 DOM 更新都变化，会让 action grounding 不稳定。</p><p>训练时还要明确 environment observation 不属于 policy loss；如果使用视觉 encoder，则 observation 作为 state input。Eval 应包含动态加载、弹窗、scroll、视觉-only 信息和 accessibility tree 缺失场景。</p></div>

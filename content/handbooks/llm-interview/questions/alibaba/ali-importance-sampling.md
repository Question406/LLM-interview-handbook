---
id: ali-importance-sampling
section: alibaba
order: 5
level: A
title: GRPO/PPO 为何需要重要性采样？新旧策略差很大时还有用吗？
quick: 因为用旧策略采样的轨迹估计新策略目标，需要 ρ 校正。差太大时 ρ 方差爆炸、clip 频繁触发，估计质量变差，应更频繁同步采样策略或缩小更新。
tags:
  - Alibaba
  - GRPO
  - PPO
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>因为用旧策略采样的轨迹估计新策略目标，需要 ρ 校正。差太大时 ρ 方差爆炸、clip 频繁触发，估计质量变差，应更频繁同步采样策略或缩小更新。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>On-policy 方法实际几乎总是“近似 on-policy”：用 <code>π_old</code> rollout，用 <code>π_θ</code> 更新。重要性比把贡献校正回当前策略。</p>
<p>当新旧策略差很大：</p>
<ul>
<li>ρ 极端值增多，方差上升；</li>
<li>clip 大量生效，有效更新变少；</li>
<li>估计偏差/方差同时恶化，训练不稳。</li>
</ul>
<p>工程应对：缩短 sync 间隔、减小学习率/clip 范围、监控 KL 与 ρ 分布、必要时重采样。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>

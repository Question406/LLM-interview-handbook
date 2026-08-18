---
id: ali-multineg-then-grpo
section: alibaba
order: 8
level: S
title: 淘天面经：单正多负 DPO 后，能否再接 GRPO？分类场景为何 DPO 常更稳？
quick: >-
  多负 DPO 主要学“正优于各负”，不保证学全负样本两两排序。DPO 压尖后可接 GRPO 做 on-policy
  探索，但要防分布过尖导致采样退化。分类/偏好清晰时 DPO 往往更稳、更省。
tags:
  - Alibaba
  - DPO
  - GRPO
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>多负 DPO 主要学“正优于各负”，不保证学全负样本两两排序。DPO 压尖后可接 GRPO 做 on-policy 探索，但要防分布过尖导致采样退化。分类/偏好清晰时 DPO 往往更稳、更省。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>淘天 Agent 公开面经原题方向：</p>
<ul>
<li><b>多负 DPO：</b>目标是拉高 chosen、压低各 rejected；并不自动得到 rejected 之间的精细序。若要序，需要更完整的 ranking/listwise 目标或额外约束。</li>
<li><b>接续 GRPO：</b>可以，用来在可验证奖励上恢复探索；但若 DPO 后 entropy 过低，group 样本多样性不足，A 信号变弱，需要调温度/约束或回退数据。</li>
<li><b>分类场景：</b>标签边界清晰、偏好噪声低时，DPO 这类离线偏好目标通常比 on-policy RL 更稳、成本更低；GRPO 更吃 verifier 与采样质量。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a></div>

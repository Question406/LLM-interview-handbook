---
id: ali-agent-final-reward
section: alibaba
order: 23
level: S
title: Agent RL 只靠最终结果奖励够不够？多步工具轨迹如何 credit？
quick: 经常不够。长 horizon 下要过程奖励、关键决策步加权、失败可恢复轨迹，或 action-level 优化，否则成功归因模糊。
tags:
  - Alibaba
  - Agent RL
  - Credit
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>经常不够。长 horizon 下要过程奖励、关键决策步加权、失败可恢复轨迹，或 action-level 优化，否则成功归因模糊。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>淘天原题方向与手册 Agent RL 章一致：final reward 广播方差大。</p>
<p>实践组合：</p>
<ul>
<li>任务成功 + 成本/步数惩罚；</li>
<li>关键 tool 参数正确性过程分；</li>
<li>对 irreversible action 单独约束；</li>
<li>用评测集区分“偶然成功”与“稳健策略”。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a></div>

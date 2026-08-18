---
id: arl-trajectories
section: agentrl
order: 1
level: S
title: 为什么只训练成功 Agent Trajectories 不够？
quick: >-
  成功 teacher trajectories 只覆盖“正确 state distribution”。Student 一旦犯错进入 OOD
  state，就没有 recovery behavior，形成 imitation learning 的 compounding error。
tags:
  - Agent Data
  - Imitation Learning
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>成功 teacher trajectories 只覆盖“正确 state distribution”。Student 一旦犯错进入 OOD state，就没有 recovery behavior，形成 imitation learning 的 compounding error。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>理想 Agent 数据不应只有 perfect demos，而应覆盖：</p><ul><li><b>Clean success：</b>高质量标准轨迹；</li><li><b>Inefficient success：</b>最终成功但绕路，用于效率 preference；</li><li><b>Near-miss：</b>只在一个关键 step 犯错；</li><li><b>Recovery：</b>犯错后发现并修复；</li><li><b>Irrecoverable failure：</b>应该 stop/ask user；</li><li><b>Clarification：</b>正确 action 是向用户索取信息。</li></ul><p>Teacher policy π_T 往往不会进入 student π_S 常犯的 bad states。Deployment 时一个早期错误会改变后续 observation，造成 state distribution shift；因此 on-policy data、error injection、recovery trajectories 和 RL 都很重要。</p><p>失败 trajectory 也不能直接整条 SFT，因为会模仿错误 action。更合理的是做 preference、局部 step labeling、截取 failure 前的 positive prefix、或把 recovery suffix 作为训练目标。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>如何构造 Hard Negative Trajectory？</summary><div class="follow-answer"><p>从成功轨迹复制，只替换一个关键 action，然后真实执行环境得到后续 failure；保持其他因素相同，credit 更干净。</p></div></details><details class="followup"><summary>如何从失败轨迹提取可训练数据？</summary><div class="follow-answer"><p>找 first-error step；prefix 可保留，错误 action 做 rejected，若后续有 recovery 则 recovery action 可做 positive。</p></div></details></div>

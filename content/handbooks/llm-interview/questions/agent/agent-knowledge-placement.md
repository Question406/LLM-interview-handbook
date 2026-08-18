---
id: agent-knowledge-placement
section: agent
order: 15
level: S
title: Skill、RAG、Memory、Weights、Tool：知识到底放哪？
quick: >-
  实用划分：通用稳定能力→weights；外部事实/高频更新知识→RAG；用户/任务历史→memory；可复用程序性方法→skill；外部行动能力→tool。边界由更新频率、隐私、可审计性、token
  cost 与是否需要 side effects 决定。
tags:
  - System Design
  - Skill
  - Memory
  - RAG
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>实用划分：通用稳定能力→weights；外部事实/高频更新知识→RAG；用户/任务历史→memory；可复用程序性方法→skill；外部行动能力→tool。边界由更新频率、隐私、可审计性、token cost 与是否需要 side effects 决定。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>载体</th><th>适合内容</th><th>核心 tradeoff</th></tr></thead><tbody><tr><td>Weights</td><td>通用、稳定、需自动泛化的能力</td><td>更新贵、不可审计、召回无需 context</td></tr><tr><td>RAG</td><td>外部事实、文档证据、常更新知识</td><td>需要 retrieval，受上下文限制</td></tr><tr><td>Memory</td><td>用户/任务历史与长期状态</td><td>隐私、冲突、写入错误</td></tr><tr><td>Skill</td><td>程序性 how-to / workflow knowledge</td><td>路由、版本、安全与 context cost</td></tr><tr><td>Tool</td><td>查询/执行外部能力</td><td>权限、副作用、runtime failure</td></tr></tbody></table></div><p>真正系统常混合：Skill 说明 procedure → 调 RAG 找 policy → 调 Tool 执行 → Memory 记录结果；常用 Skill 再通过 SFT/RL 蒸馏进 weights。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候把 RAG 内容蒸馏进 weights？</summary><div class="follow-answer"><p>内容稳定、高频、泛化价值大、检索成本高且许可允许时；但要保留外部证据需求与更新问题。</p></div></details><details class="followup"><summary>Skill 能不能看成 procedural memory？</summary><div class="follow-answer"><p>可以作为外部化 procedural memory 的一种；区别在于 Skill 往往更显式、版本化、可执行/共享。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

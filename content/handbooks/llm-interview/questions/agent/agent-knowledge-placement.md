---
id: agent-knowledge-placement
section: agent
order: 15
level: S
title: Skill、RAG、Memory、Weights、Tool：知识到底放哪？
quick: "稳定、通用的能力放进模型权重；更新频繁的外部事实用 RAG 检索；用户与任务历史存入 memory；可复用的操作方法写成 skill；查询或执行外部操作通过 tool。选择时看更新成本、隐私、可审计性、上下文开销和操作副作用。"
tags:
  - System Design
  - Skill
  - Memory
  - RAG
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>稳定、通用的能力放进模型权重；更新频繁的外部事实用 RAG 检索；用户与任务历史存入 memory；可复用的操作方法写成 skill；查询或执行外部操作通过 tool。选择时看更新成本、隐私、可审计性、上下文开销和操作副作用。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>载体</th><th>适合内容</th><th>核心 tradeoff</th></tr></thead><tbody><tr><td>Weights</td><td>通用、稳定、需自动泛化的能力</td><td>更新贵、不可审计、召回无需 context</td></tr><tr><td>RAG</td><td>外部事实、文档证据、常更新知识</td><td>需要检索，并受上下文容量限制</td></tr><tr><td>Memory</td><td>用户/任务历史与长期状态</td><td>隐私、冲突、写入错误</td></tr><tr><td>Skill</td><td>操作方法与工作流程</td><td>路由选择、版本、安全和上下文开销</td></tr><tr><td>Tool</td><td>查询/执行外部能力</td><td>权限、副作用和执行失败</td></tr></tbody></table></div><p>实际系统通常组合使用：Skill 说明步骤，RAG 找相关政策，Tool 执行操作，Memory 记录结果。常用 Skill 也可以通过 SFT/RL 蒸馏进模型权重。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候把 RAG 内容蒸馏进 weights？</summary><div class="follow-answer"><p>内容稳、用得勤、泛化价值大、检索贵且许可允许时可以蒸进 weights；外部证据和更新问题仍要留着。</p></div></details><details class="followup"><summary>Skill 能不能看成 procedural memory？</summary><div class="follow-answer"><p>可以看作存放在模型外部的操作记忆。Skill 通常把步骤写得更明确，也能管理版本、执行和共享。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

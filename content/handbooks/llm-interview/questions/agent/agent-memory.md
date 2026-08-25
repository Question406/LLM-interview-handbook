---
id: agent-memory
section: agent
order: 11
level: S
title: Agent Memory 应如何分类和更新？
quick: >-
  可以分成 working/short-term、episodic、semantic、procedural。Memory 不能无脑
  append。每条记录要带 timestamp、source、confidence、scope；冲突用新鲜度、用户显式修正和 source trust
  来处理。
tags:
  - Memory
  - Agent
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>可以分成 working/short-term、episodic、semantic、procedural。Memory 不能无脑 append。每条记录要带 timestamp、source、confidence、scope；冲突用新鲜度、用户显式修正和 source trust 来处理。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Memory</th><th>内容</th><th>例子</th></tr></thead><tbody><tr><td>Working / short-term</td><td>当前任务状态</td><td>已检查 DB，下一步看 Redis</td></tr><tr><td>Episodic</td><td>发生过的经历</td><td>上次部署失败的完整轨迹</td></tr><tr><td>Semantic</td><td>提炼事实</td><td>项目使用 PostgreSQL 16</td></tr><tr><td>Procedural</td><td>怎么做</td><td>事故排查标准流程；可与 Skill 重叠</td></tr></tbody></table></div><p>一条 memory 可以写成 m=(content,timestamp,source,confidence,scope)。新旧打架时，用户显式更正通常优先级最高；再看时间新不新、来源可不可信、以及当时的 scope。</p><p>比如用户明确说「以后不要用 Python」，就该把旧偏好作废，而不是两条矛盾记录一起检索回来让模型猜。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候应该忘记？</summary><div class="follow-answer"><p>过期事实、低置信推断、违反 retention policy 的敏感信息，以及已经被新事实取代的重复 memory，这些该忘。</p></div></details><details class="followup"><summary>Memory 写入由模型决定安全吗？</summary><div class="follow-answer"><p>最好是模型提出候选，runtime/policy 再按类型、敏感度、confidence 决定要不要持久化。关键用户偏好可以要求显式确认。</p></div></details><details class="followup"><summary>Memory poisoning 怎么防？</summary><div class="follow-answer"><p>要区分 trusted/untrusted source，还要有写入 schema、sanitization、provenance、冲突检测、敏感字段权限，以及检索时按 trust 加权。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

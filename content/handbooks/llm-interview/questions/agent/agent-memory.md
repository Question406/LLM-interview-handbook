---
id: agent-memory
section: agent
order: 11
level: S
title: Agent Memory 应如何分类和更新？
quick: >-
  可分 working/short-term、episodic、semantic、procedural。Memory 不能无脑 append；每条记录应带
  timestamp、source、confidence、scope，并用 freshness、显式修正和 source trust 处理冲突。
tags:
  - Memory
  - Agent
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>可分 working/short-term、episodic、semantic、procedural。Memory 不能无脑 append；每条记录应带 timestamp、source、confidence、scope，并用 freshness、显式修正和 source trust 处理冲突。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Memory</th><th>内容</th><th>例子</th></tr></thead><tbody><tr><td>Working / short-term</td><td>当前任务状态</td><td>已检查 DB，下一步看 Redis</td></tr><tr><td>Episodic</td><td>发生过的经历</td><td>上次部署失败的完整轨迹</td></tr><tr><td>Semantic</td><td>提炼事实</td><td>项目使用 PostgreSQL 16</td></tr><tr><td>Procedural</td><td>怎么做</td><td>事故排查标准流程；可与 Skill 重叠</td></tr></tbody></table></div><p>一条 memory 可以建模为 m=(content,timestamp,source,confidence,scope)。当新旧冲突，explicit user correction 往往优先级最高；其次考虑时间新鲜度、来源可信度与上下文 scope。</p><p>例如用户明确说“以后不要用 Python”，应该 invalidate 旧偏好，而不是把两个矛盾记录都检索回来让模型猜。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候应该忘记？</summary><div class="follow-answer"><p>过期事实、低置信推断、违反 retention policy 的敏感信息、重复/被新事实 supersede 的 memory。</p></div></details><details class="followup"><summary>Memory 写入由模型决定安全吗？</summary><div class="follow-answer"><p>最好模型提出 candidate，runtime/policy 依据类型、敏感度、confidence 决定是否持久化；关键用户偏好可要求显式确认。</p></div></details><details class="followup"><summary>Memory poisoning 怎么防？</summary><div class="follow-answer"><p>区分 trusted/untrusted source、写入 schema、sanitization、provenance、冲突检测、敏感字段权限和 retrieval-time trust weighting。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

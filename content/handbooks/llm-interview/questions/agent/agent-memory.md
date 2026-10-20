---
id: agent-memory
section: agent
order: 11
level: S
title: Agent Memory 应如何分类和更新？
quick: "Memory 可分为当前任务状态、过去经历、事实知识和操作方法。每条记忆记录时间、来源、可信程度和适用范围。不要只追加新记录；遇到冲突，要依据用户明确更正、信息新旧和来源可信度，更新或废弃旧记录。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>Memory 可分为当前任务状态、过去经历、事实知识和操作方法。每条记忆记录时间、来源、可信程度和适用范围。不要只追加新记录；遇到冲突，要依据用户明确更正、信息新旧和来源可信度，更新或废弃旧记录。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>Memory</th><th>内容</th><th>例子</th></tr></thead><tbody><tr><td>Working / short-term</td><td>当前任务状态</td><td>已检查 DB，下一步看 Redis</td></tr><tr><td>Episodic</td><td>发生过的经历</td><td>上次部署失败的完整轨迹</td></tr><tr><td>Semantic</td><td>提炼事实</td><td>项目使用 PostgreSQL 16</td></tr><tr><td>Procedural</td><td>怎么做</td><td>事故排查标准流程；可与 Skill 重叠</td></tr></tbody></table></div><p>一条 memory 可以写成 m=(content,timestamp,source,confidence,scope)。新旧记录冲突时，通常优先采用用户明确更正，再检查时间、来源可信度和适用范围。</p><p>比如用户明确说「以后不要用 Python」，就该把旧偏好作废，而不是两条矛盾记录一起检索回来让模型猜。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候应该忘记？</summary><div class="follow-answer"><p>过期事实、可信度低的推断、超出保留期限的敏感信息，以及已经被新事实取代的旧记忆，都应删除或作废。</p></div></details><details class="followup"><summary>Memory 写入由模型决定安全吗？</summary><div class="follow-answer"><p>让模型提出候选记忆，再由运行程序和策略检查类型、敏感程度与可信度，决定是否持久化。关键用户偏好可以要求明确确认。</p></div></details><details class="followup"><summary>Memory poisoning 怎么防？</summary><div class="follow-answer"><p>区分可信和不可信来源，验证写入 schema，清理异常内容并记录来源。再做冲突检测、控制敏感字段权限，检索时也根据来源可信度加权。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

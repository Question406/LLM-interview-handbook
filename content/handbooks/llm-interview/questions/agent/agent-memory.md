---
id: agent-memory
section: agent
order: 11
level: S
title: Agent Memory 应如何分类和更新？
quick: 假设用户说“这次报告用英文”，不能立即把它保存成“这个用户永远只用英文”。Memory 首先要区分当前任务信息与长期偏好。
tags:
  - Memory
  - Agent
  - 口述改写 2026-10-28
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 假设用户说“这次报告用英文”，不能立即把它保存成“这个用户永远只用英文”。</p>
<p><strong>做法与原因：</strong> 我会给记录附上来源、时间和适用范围。</p>
<p><strong>检查与取舍：</strong> 验证时不只测模型是否记住，也要测它能否纠正旧信息、避免跨用户读取，以及在证据不足时不擅自概括。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>假设用户说“这次报告用英文”，不能立即把它保存成“这个用户永远只用英文”。Memory 首先要区分当前任务信息与长期偏好。</p>
<p>我会给记录附上来源、时间和适用范围。稳定偏好需要足够证据才长期保存；会变化的事实要能更新或过期；当前任务状态则随着任务结束处理。敏感内容还要有明确授权和删除方式。</p>
<p>验证时不只测模型是否记住，也要测它能否纠正旧信息、避免跨用户读取，以及在证据不足时不擅自概括。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>Memory 可以分成当前任务状态、过去的经历、提炼的事实和操作方法四类，每条记下时间、来源、可信程度和适用范围。更新时别只追加新记录：遇到冲突，按用户明确更正、信息新旧和来源可信度，更新或废弃旧记录。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>我会把 Memory 分四类：当前任务状态、发生过的经历、提炼出的事实、做事的方法。每条都带上时间、来源、可信度和适用范围，更新时要处理冲突，光往后追加不够。</p><div class="table-wrap"><table><thead><tr><th>Memory</th><th>内容</th><th>例子</th></tr></thead><tbody><tr><td>Working / short-term</td><td>当前任务状态</td><td>已检查 DB，下一步看 Redis</td></tr><tr><td>Episodic</td><td>发生过的经历</td><td>上次部署失败的完整轨迹</td></tr><tr><td>Semantic</td><td>提炼事实</td><td>项目使用 PostgreSQL 16</td></tr><tr><td>Procedural</td><td>怎么做</td><td>事故排查标准流程；可与 Skill 重叠</td></tr></tbody></table></div><p>一条 memory 可以写成 m=(content,timestamp,source,confidence,scope)。新旧记录冲突时，一般先看用户有没有明确更正，再看时间、来源可信度和适用范围。</p><p>比如用户明确说了「以后不要用 Python」，就把旧偏好作废。两条矛盾的记录要是一起检索回来，模型只能去猜用哪条。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候应该忘记？</summary><div class="follow-answer"><p>过期的事实、可信度低的推断、超过保留期限的敏感信息，还有已经被新事实取代的旧记忆，都应该删掉或作废。</p></div></details><details class="followup"><summary>Memory 写入由模型决定安全吗？</summary><div class="follow-answer"><p>让模型提出候选记忆，再由运行程序和策略检查类型、敏感程度和可信度，决定要不要持久化。关键的用户偏好可以要求用户明确确认。</p></div></details><details class="followup"><summary>Memory poisoning 怎么防？</summary><div class="follow-answer"><p>区分可信和不可信的来源，校验写入的 schema，清理异常内容并记下来源。再做冲突检测、控制敏感字段的权限，检索时也按来源可信度加权。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

</details>

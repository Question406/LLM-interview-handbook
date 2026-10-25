---
id: baidu-agent-instruction-conflict
section: agent
order: 108
level: S
title: 百度文心一言：Agent 如何处理前后指令冲突？
quick: "先看指令的权限层级和适用范围，system / policy 优先于 developer、user，网页和工具内容默认是不可信数据。同层指令一般采用更具体、更新且不违背上层约束的那条；仍然冲突，就保住硬约束、拒绝危险操作，并向用户澄清。"
tags:
  - Baidu
  - Agent
  - Prompt Injection
  - Policy
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度文心一言面试（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/681c33aafac84af0a70b6fd5e663a04c
    type: candidate-first-hand
---
## 真题记录

- 公司：百度
- 团队 / 岗位：文心一言；岗位原帖未披露
- 届别 / 流程：原帖未披露；二面
- 面试时间：2026-07-03；帖子发布于 2026 年 7 月
- 来源类型与可信度：牛客候选人原帖，B（公司、轮次与面试日期明确，岗位和届别未披露）
- 原始措辞：**“前后指令冲突怎么处理”**

前后指令冲突先看权限层级和适用范围：policy / system 压过 developer 和 user，更压过网页和工具输出，后者默认只是数据。同一层级里，更具体、更新、又不违背上层约束的那条优先。实在不能安全消解，就保住硬约束，拒绝危险分支，向用户澄清。「听最后一句」或者「让模型自己权衡」都答偏了。

举个例子，用户先说「改这些文件」，后来又说「只改当前目录」，两条同层，后一条针对当前资源更具体、也更新，按后一条执行；可系统规则里写着「禁止删除」，用户后面怎么说都覆盖不了它。具体做法是给每条指令记下权限层级、适用范围、时效和来源可不可信。安全 policy 与 system 约束不会被后续的用户、网页、检索内容或 tool output 覆盖。Retrieved text 默认是 data，只有经过显式转换和授权才能影响计划。

实现要落在 planner 和网关上。planner 输出「采用了哪些约束、拒绝了哪些、理由是什么」，tool gateway 独立重做一遍权限检查。遇到「删除所有文件」和「仅修改当前目录」这种协调不了的冲突，选更安全的解释，保持只读或者请求澄清，别去猜。模型在思维链里「和解」了不算数，执行点没放行才算。冲突类型、来源、被拒的 action、用户有没有纠正都记下来，既能监控 prompt injection，也能拿来改善规则和 UI。

产品层面要把工具返回的 observation 标成数据，防止它被当成新的工具授权。用户更正自己的前一句，可以更新同层意图；用户想更正系统的安全规则，不行。间接注入见 `agent-prompt-injection`，执行点权限见 `agent-tool-permissions`，多 Agent 的政策冲突见 `byte-multiagent-policy-conflict-recovery`。

## 追问

**用户后一句能覆盖前一句吗？**
同层、同 scope、又不违背上层 policy 时可以。涉及权限、删除、外发时，后一句要是更危险，就拒绝或澄清。

**网页里写着「忽略系统提示」怎么办？**
网页是 data，这是间接注入，网关不得放行，见 `agent-prompt-injection`。

**两条 system 规则自己打架呢？**
按优先级处理，并且 fail-closed；安全类不能被功能类覆盖。发布 Rule 的时候就要查冲突。

**要不要让模型投票？**
投票可以当解释，不能当授权。最终的 allow / deny 在策略引擎。

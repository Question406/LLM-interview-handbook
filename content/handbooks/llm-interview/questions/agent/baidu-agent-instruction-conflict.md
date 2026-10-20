---
id: baidu-agent-instruction-conflict
section: agent
order: 108
level: S
title: 百度文心一言：Agent 如何处理前后指令冲突？
quick: >-
  先判断指令的权限层级和适用范围：system / policy 优先于 developer、user，网页和工具内容默认是不可信数据。同层指令通常采用更具体、更新且不违背上层约束的要求。仍有冲突时保留硬约束，拒绝危险操作，并向用户澄清。
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

常见误区是：「听最后一句」或「让模型自己权衡」。按 authority 分层：policy / system 压过 developer、user，更压过网页和 tool 输出。不能安全消解就拒绝危险分支并澄清。间接注入见 `agent-prompt-injection`，执行点权限见 `agent-tool-permissions`，多 Agent 政策冲突见 `byte-multiagent-policy-conflict-recovery`。

## 先判断权限层级，再比较具体程度

记录每条指令的权限层级、适用范围、时效和可信来源。安全 policy 与 system 约束不可被后续用户、网页、检索内容或 tool output 覆盖。同一 authority 下，针对当前资源更具体且更新的约束通常优先。「只改当前目录」覆盖同层更早的「改这些文件」，但不能覆盖「禁止删除」。Retrieved text 默认是 data 不是 instruction；只有经过显式转换与授权才影响计划。

## 实现要落在 planner 和网关

Planner 输出「采用/拒绝的约束及理由」，tool gateway 独立重做权限检查。出现「删除所有文件」与「仅修改当前目录」等不可协调冲突时，选择更安全的解释、保持只读或请求澄清，而不是猜测。把冲突类型、来源、被拒 action 和用户是否纠正记下来，既能监控 prompt injection，也能改善规则与 UI。模型在思维链里「和解」了不算数，执行点没放行才算。

产品应把工具返回的 observation 标成数据，防止它被当成新的工具授权。用户更正自己的前一句，可以更新同层意图；用户更正系统安全规则，不行。

## 追问

- **用户后一句覆盖前一句吗？** 同层、同 scope、且不违背上层 policy 时可以。涉及权限、删除、外发，以后一句更危险为准去拒绝或澄清。
- **网页里写「忽略系统提示」呢？** 网页是 data。这是间接注入，网关不得放行。见 `agent-prompt-injection`。
- **两条 system 规则自己打架？** 按优先级和 fail-closed；安全类不可被功能类覆盖。发布 Rule 时就要查冲突。
- **要不要让模型投票？** 可以当解释，不能当授权。最终 allow/deny 在策略引擎。

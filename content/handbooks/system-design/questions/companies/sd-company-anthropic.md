---
id: sd-company-anthropic
section: companies
order: 32
level: A
title: Anthropic：设计文档评审与可恢复服务（原帖待核）
quick: 仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。
companies:
  - anthropic
tags:
  - System Design
  - 设计练习
  - 二手摘要
  - 原帖待核
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-25T00:00:00.000Z
sources:
  - title: Anthropic题卡摘要：现场设计文档评审
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/onsite-design-doc-review
    type: secondary
---

## 题目描述

围绕 Anthropic 既有二手资料涉及的设计文档评审与可恢复服务选择一个设计场景练习。输入是题型摘要而非完整原帖题面；请先提出范围与规模假设，输出核心接口、数据模型、一次请求路径、两项关键取舍和故障恢复方案。当前题卡只提供练习路线；公司归属、具体轮次与完整题干仍需后续通过 Chrome 核对原帖。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。

### 证据等级与入口

以下链接来自仓库2026-10-18采集的站内题卡摘要，本轮没有重新读取原帖。来源类型：候选人报告的二手摘要。入口：[现场设计文档评审](?book=us-tech&section=anthropic&question=p3a-anthropic-onsite-design-doc-review)。

### 建议怎么练

先练从已有设计发现风险，而不是从空白画一套新系统。沿请求和状态变化检查失败窗口，为每条风险写触发条件、用户影响、证据或待测假设，再比较最小修订与整体重做的成本。

### 具体场景与 constraints

文档声称“超时整体重试即可可靠”，可以用响应丢失后重复执行的路径质疑。提出幂等、准入和持久任务状态，再设计能复现这个故障的验证。原摘要没有提供面试官给出的真实设计文档。

### 完成后的自查

用`sd-interview-plan`安排一次45分钟练习。检查是否明确了成功确认、idempotency key、权限、数据版本、超时后最终结果以及容量假设。记录没回答好的两处，再回基础模块补；不要把一篇帖子或二手题卡数量当作公司题目频率。


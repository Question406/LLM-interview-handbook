---
id: sd-company-meta
section: companies
order: 33
level: A
title: Meta：AI Agent 与代码审查工作流（原帖待核）
quick: 仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。
companies:
  - meta
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
  - title: Meta题卡摘要：AI-enabled Agent系统
    url: >-
      https://www.1point3acres.com/interview/problems/company/meta/system-design-ai-enabled-agent-system
    type: secondary
---

## 题目描述

围绕 Meta 既有二手资料涉及的 AI Agent 与代码审查工作流选择一个设计场景练习。输入是题型摘要而非完整原帖题面；请先提出范围与规模假设，输出核心接口、数据模型、一次请求路径、两项关键取舍和故障恢复方案。当前题卡只提供练习路线；公司归属、具体轮次与完整题干仍需后续通过 Chrome 核对原帖。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。

### 证据等级与入口

以下链接来自仓库2026-10-18采集的站内题卡摘要，本轮没有重新读取原帖。来源类型：候选人报告的二手摘要。入口：[AI-enabled Agent 系统](?book=us-tech&section=meta&question=p3a-meta-system-design-ai-enabled-agent-system)。

### 建议怎么练

先定义任务成功如何判断，再设计工具权限、状态机与可恢复执行。代码审查结论应绑定具体 commit，并附复现证据；工单分流应有人工接管与错误修正。对比单 Agent 和并行子任务时使用同预算的质量与成本衡量。

### 具体场景与 constraints

PR 推送新 commit 后，旧审查结果不应不加检查就发布到新代码。仓库注释和检索文本不能提升执行器权限。代码审查这一具体练习和默认不 merge 等约定属于手册补充，未核实为候选人完整题干。

### 完成后的自查

用`sd-interview-plan`安排一次45分钟练习。检查是否明确了成功确认、idempotency key、权限、数据版本、超时后最终结果以及容量假设。记录没回答好的两处，再回基础模块补；不要把一篇帖子或二手题卡数量当作公司题目频率。


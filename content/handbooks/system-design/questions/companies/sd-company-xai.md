---
id: sd-company-xai
section: companies
order: 35
level: A
title: xAI：通知、限流与 RAG 系统（原帖待核）
quick: 仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。
companies:
  - xai
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
  - title: xAI题卡摘要：新帖通知粉丝
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/notification-system-design
    type: secondary
  - title: xAI题卡摘要：限流器设计
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/rate-limiter-design
    type: secondary
  - title: xAI题卡摘要：RAG系统设计
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/rag-system-design
    type: secondary
---

## 题目描述

围绕 xAI 既有二手资料涉及的通知、限流与 RAG 系统选择一个设计场景练习。输入是题型摘要而非完整原帖题面；请先提出范围与规模假设，输出核心接口、数据模型、一次请求路径、两项关键取舍和故障恢复方案。当前题卡只提供练习路线；公司归属、具体轮次与完整题干仍需后续通过 Chrome 核对原帖。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。

### 证据等级与入口

以下链接来自仓库2026-10-18采集的站内题卡摘要，本轮没有重新读取原帖。来源类型：候选人报告的二手摘要。入口：[新帖通知粉丝](?book=us-tech&section=xai&question=p3a-xai-notification-system-design)；[限流器设计](?book=us-tech&section=xai&question=p3a-xai-rate-limiter-design)；[RAG 系统设计](?book=us-tech&section=xai&question=p3a-xai-rag-system-design)。

### 建议怎么练

通知先讲业务事件持久化、分页 fanout、收件人去重和偏好校验；限流先讲租户与全局资源的不同约束；RAG 先讲文档权限、索引新鲜度和引用。不要把一个内存限流函数的实现等同于完整分布式系统设计。

### 具体场景与 constraints

一条新帖扇出过程中 worker 崩溃，恢复从可检查的分页进度继续，已写通知按事件和收件人去重。供应商 push 超时的效果不能简单承诺严格一次；应用内记录、外部投递与用户已读分别建模。

### 完成后的自查

用`sd-interview-plan`安排一次45分钟练习。检查是否明确了成功确认、idempotency key、权限、数据版本、超时后最终结果以及容量假设。记录没回答好的两处，再回基础模块补；不要把一篇帖子或二手题卡数量当作公司题目频率。


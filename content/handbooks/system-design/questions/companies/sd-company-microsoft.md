---
id: sd-company-microsoft
section: companies
order: 34
level: A
title: Microsoft AI：分布式爬虫：调度、去重与恢复（原帖待核）
quick: 仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。
companies:
  - microsoft
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
  - title: Microsoft AI题卡摘要：MAI分布式爬虫
    url: >-
      https://www.1point3acres.com/interview/problems/company/microsoft/web-crawler-system-design
    type: secondary
---

## 题目描述

围绕 Microsoft AI 既有二手资料涉及的分布式爬虫：调度、去重与恢复选择一个设计场景练习。输入是题型摘要而非完整原帖题面；请先提出范围与规模假设，输出核心接口、数据模型、一次请求路径、两项关键取舍和故障恢复方案。当前题卡只提供练习路线；公司归属、具体轮次与完整题干仍需后续通过 Chrome 核对原帖。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

仓库已有一亩三分地二手题卡可用于选题；尚未逐条核对候选人原帖，先按主题练习，不把补充细节当成已确认真题。

### 证据等级与入口

以下链接来自仓库2026-10-18采集的站内题卡摘要，本轮没有重新读取原帖。来源类型：候选人报告的二手摘要。入口：[MAI 分布式爬虫](?book=us-tech&section=microsoft&question=p3a-microsoft-web-crawler-system-design)。

### 建议怎么练

从按域管理 frontier 开始，说明域级礼貌限速、下载解析、URL 与内容分别去重以及索引发布。抓取任务用租约恢复，投递与索引更新使用稳定标识避免重复效果。抓取范围、刷新周期和动态渲染需求先澄清。

### 具体场景与 constraints

同一域名有一万个待抓 URL，也不能让一百台 worker 同时无节制请求。URL 规范化必须保留会改变内容的参数，不能把 utm 之外的业务参数一律删除。练习规模与时间安排都是手册假设。

### 完成后的自查

用`sd-interview-plan`安排一次45分钟练习。检查是否明确了成功确认、idempotency key、权限、数据版本、超时后最终结果以及容量假设。记录没回答好的两处，再回基础模块补；不要把一篇帖子或二手题卡数量当作公司题目频率。


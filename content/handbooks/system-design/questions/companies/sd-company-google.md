---
id: sd-company-google
section: companies
order: 28
level: A
title: Google：欺诈检测、实时推荐、视频去重与内容审核
quick: 既有原帖记录明确披露了这些系统设计方向；按业务错误代价、延迟和 data feedback loop 准备，具体架构与规模是手册练习扩展。
companies:
  - google
tags:
  - System Design
  - 设计练习
  - 已存原帖核对记录
  - 公司练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-25T00:00:00.000Z
sources:
  - title: Google：骨骼电面
    url: 'https://www.1point3acres.com/interview/thread/1161213'
    type: secondary
  - title: Google MLE面试凉经
    url: 'https://www.1point3acres.com/interview/thread/1157141'
    type: secondary
  - title: 狗家MLE挂经
    url: 'https://www.1point3acres.com/interview/thread/1159435'
    type: secondary
  - title: Google ML Design
    url: 'https://www.1point3acres.com/interview/thread/1150617'
    type: secondary
---

## 题目描述

根据仓库已有的一亩三分地原帖核对记录，选择一个 Google 场景练习：欺诈检测及冷启动与不平衡；实时推荐与延迟/准确率；大规模短视频模糊去重；违规内容检测及模型成本。输出所选场景的目标、数据与标签、在线路径、监控和故障处理。原帖没有完整流量数字与接口，练习需要先提出假设并标明。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

既有原帖记录明确披露了这些系统设计方向；按业务错误代价、延迟和 data feedback loop 准备，具体架构与规模是手册练习扩展。

### 现有证据能确认到哪里

仓库2026-10-22的核对记录：1161213披露欺诈检测、cold start 和不平衡；1157141披露实时推荐、监控迭代与延迟/准确率；1159435披露大规模短视频模糊去重、高并发、申诉 calibration、embedding 维度与延迟量化；1150617披露违规内容检测及 LLM 与便宜模型的成本取舍。本轮未重新打开原帖。

### 选一个场景走完

例如欺诈检测：先定义拦截、放行、复核的误判成本和延迟，检查特征在交易发生时是否可用；离线按时间切分，线上在成本与人审约束下设阈值，保留申诉与后验标签。模型失效时采用经业务批准的保守策略。具体流程是备考扩展，不能归给面试官。

### 如何迁移到另外几题

推荐重点是曝光反馈与冷启动；去重重点是候选召回、相似度阈值、近重复 cluster 与误判申诉；审核重点是政策版本与人工容量。embedding 维度变化应测质量、内存、throughput 和端到端延迟，不能仅凭维度翻倍就断言时延翻倍。

### 下一步练习

先读`sd-recommendation`、`sd-fraud-moderation`、`sd-feature-platform`，再用45分钟完整作答。保留“原帖只披露主题”“作者回答”“手册建议”的 attribution；不依据这几篇帖子推断公司题目频率。


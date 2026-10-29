---
id: sd-recommendation
section: ml
order: 20
level: A
title: 推荐系统：从业务目标到召回、排序和反馈
quick: 假设点击率上涨，但用户很快退出或退货。先明确推荐希望改善的长期结果，再决定点击能否作为合适训练信号。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Google：Rules of Machine Learning
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: primary
  - title: Feast：Point-in-time joins
    url: 'https://docs.feast.dev/getting-started/concepts/point-in-time-joins'
    type: primary
---

## 题目描述

设计短视频推荐系统，首页每次返回20条候选，支持新用户与新视频。手册练习假设端到端 p95目标200ms，需兼顾观看、负反馈与多样性。请输出数据与标签定义、训练与验证切分、在线推荐路径、冷启动与降级，以及灰度和监控方案。不得把点击率单独当作所有业务目标的替代。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设点击率上涨，但用户很快退出或退货。
>
> **做法与原因：** 系统可以分候选召回、排序和业务约束，记录当时曝光了什么、位置和后续反馈。
>
> **检查与取舍：** 我会结合离线回放与受控线上实验，检查质量、覆盖、延迟和重要用户群。

## 可以这样回答

假设点击率上涨，但用户很快退出或退货。先明确推荐希望改善的长期结果，再决定点击能否作为合适训练信号。

系统可以分候选召回、排序和业务约束，记录当时曝光了什么、位置和后续反馈。没被展示的商品不能简单当作用户不喜欢，exposure bias 需要单独处理。

我会结合离线回放与受控线上实验，检查质量、覆盖、延迟和重要用户群。单一排名指标提高不等于业务整体更好。

## 技术备查

## 参考答案与设计讨论

先定义用户动作与标签时点，再把召回、排序、重排、特征服务和 feedback loop 连起来；离线提升需要线上验证。

![推荐系统：从业务目标到召回、排序和反馈：核心数据流](/system-design/recommendation.svg)

图展示核心数据流；权限、状态和故障恢复以正文约定为准。

### 澄清目标与样本

先问产品目标是观看时长、满意度还是交易，负反馈和创作者生态有哪些护栏。曝光日志需要记录候选、位置、策略与实际展示，训练标签按观测窗口成熟；没曝光的物品不能直接当成用户不喜欢。时间切分并防止同内容近重复泄漏。

### 在线与离线路径

内容与行为进入批流特征，训练产出带版本模型和索引。请求侧先用多个召回器取候选，查特征后排序，再按多样性、安全与已看规则重排；最终记录真实曝光。新用户用上下文和热门探索，新物品用内容特征进入受控探索。

### 深挖与验证

估算候选量、特征点查耗时和模型成本，按延迟预算裁剪；超时使用允许的轻量路径，并记录降级。看分用户群与内容群的质量、覆盖率、延迟和特征缺失，在线随机实验评估收益与长期护栏。

### 例子与关联

新视频没有互动，也能通过内容相似与小流量探索取得反馈，不能永久被热门分数压住。完整专题见[推荐系统](?book=us-tech&section=design&question=design-recsys)、[广告排序](?book=us-tech&section=design&question=design-ads-rank)和[特征平台](?book=us-tech&section=design&question=design-feature-store)；这些是教学练习，不按公司高频题标记。


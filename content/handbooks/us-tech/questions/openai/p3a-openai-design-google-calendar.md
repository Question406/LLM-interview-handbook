---
id: p3a-openai-design-google-calendar
section: openai
order: 645
level: A
title: "OpenAI：日历系统：多视图查询与跨设备同步"
quick: "保存事件的原始时区和重复规则，在可见时间窗口里展开实例，单次改动作为例外覆盖。跨设备用版本或增量游标同步，先约定夏令时和编辑重复系列的范围。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · design-google-calendar"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-google-calendar
    type: secondary
---

## 题目

设计一个类似 Google Calendar 的系统：用户能创建事件，并按日、周、月、年浏览。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

日历可以保存原始时区和重复规则，等用户打开某个视图时，只展开可见窗口里的实例；单次修改和删除用例外记录覆盖。这样不用把无限重复的事件提前存成无数行。

这里的练习支持单次和重复事件、日周月年视图、跨设备同步、时区和单次例外，暂时不做会议室等资源的复杂调度。开场先确认是否需要邀请参与人、忙闲查询，以及跨时区、夏令时和重复系列编辑的范围。

比如用户创建「每周一 10:00，America/New_York」的例会，数据库只存一条 series。3 月夏令时切换后，服务按纽约本地时间展开那一周，所以仍在当地 10:00 开会，UTC 时间则比前一周早一小时。如果这周单独改到 11:00，就用例外覆盖这一实例。每周重复不能简单地加固定秒数。

数据上，series 保存本地开始时刻、IANA 时区、重复规则和例外列表，`event_instance` 关联原始 occurrence id。删除某一次要留 tombstone，才能区分「尚未展开」和「已经删除」。日历 API 负责读写规则库，范围索引和缓存加速查询，所有变更进入增量变更流，客户端用 cursor 补同步；也可以用版本号同步。

并发编辑用 etag 拒绝覆盖。「仅这一次」「这次及以后」「整个系列」分别处理，年视图可以只返回摘要，减少展开和传输成本。验证时看跨设备传播延迟、视图查询 P99、重复展开开销和时区错误。

## 追问

**参与人分布在不同时区怎么办？**
保留原始时区，展示时转换成各用户的时区。「全天」事件按日期建模；如果存成 UTC 午夜，其他时区可能显示成跨两天。

**「这次及以后」怎样编辑？**
把原 series 截止到这一次之前，再从这一次新建 series 保存新规则。已有例外按日期归到对应的那一半。

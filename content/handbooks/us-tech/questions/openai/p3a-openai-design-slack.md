---
id: p3a-openai-design-slack
section: openai
order: 643
level: A
title: "OpenAI：Slack：频道、私信、多设备和大群"
quick: "消息先持久化，再确认发送成功，推到设备是另一层确认。每条消息用稳定 id 和会话内 seq，离线设备按游标补取、重复推送按 id 去重，大频道采用推拉结合。"
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
  - title: "1Point3Acres · OpenAI · design-slack"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-slack
    type: secondary
---

## 题目

设计一个类似 Slack 的企业聊天系统，涵盖消息、通知、跨设备投递和扩展。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

聊天消息先写持久日志，写成功后才确认「已发送」，再异步推给在线设备。给消息稳定 id 和会话内 seq，设备离线后按游标补取，就能把持久化与投递分别处理。

练习范围是企业私信、频道、多设备、离线补取和大频道，只要求频道内有序。先确认是否需要线程回复、搜索和已读回执，不要求全局有序。

比如 Alice 在 #eng 发「部署好了」，客户端带幂等键调用会话 API。服务把消息追加到按 conversation 分片的持久日志，分配 seq=1042，落盘后回复 Alice。fanout 再推给 Bob 的手机和笔记本；笔记本离线、`device_cursor` 停在 1040，下次上线就补取 1041 和 1042。

数据库可以保存 `message(conversation, seq, id, sender, body)`、membership 和 `device_cursor`。重试同一个幂等键返回同一条消息，推送重复则按 id 去重。搜索索引和通知异步消费日志，避免阻塞消息落库。成员退群后，旧链接和缓存也要重新鉴权。

大群按活跃度推拉结合，可以只推通知、让客户端拉正文，避免每条消息同步写进百万个设备队列。热点会话可以单独分区，但要保留会话内排序契约。验证时看持久确认延迟、设备消息缺口恢复时间和热点分片负载。

## 追问

**多地域部署怎么保顺序？**
每个频道选权威区域，或使用一致写路径。网络分区时要取舍可用性和顺序，全球总序会有延迟成本。

**手机和电脑怎么同步已读？**
给用户保存「读到哪个 seq」的游标，一台设备推进后，再广播给该用户的其他设备。它记录用户已读进度，`device_cursor` 记录每台设备投递到了哪里。

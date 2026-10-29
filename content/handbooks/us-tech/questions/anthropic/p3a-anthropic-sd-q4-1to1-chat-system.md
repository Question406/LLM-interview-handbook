---
id: p3a-anthropic-sd-q4-1to1-chat-system
section: anthropic
order: 622
level: A
title: "Anthropic：单设备一对一聊天：投递、在线状态与离线队列"
quick: "我会先把每条消息写进持久会话日志，再通过 WebSocket 实时推送；离线后按 cursor 补取。presence 只是心跳推算的在线状态，消息保存和已送达、已读都要有各自的依据。"
companies:
  - anthropic
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · sd-q4-1to1-chat-system"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/sd-q4-1to1-chat-system
    type: secondary
---

## 题目

设计一个只支持私聊的 1 对 1 聊天系统，不包括群聊和频道。题卡提到面试中要比较 Kafka 和 Redis。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

持久消息日志保证用户离线后能补取消息，WebSocket 负责在线连接。在线状态（presence）是用心跳和超时算出来的近似值，不是绝对事实，不能拿它决定消息是否需要保存。

比较消息中间件时，按需求逐项看：是否需要重放、持久性要求多高、延迟要求多低。另外，"已送达"和"已读"是两个不同的事件。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

只做 1 对 1，每个用户只有一台设备，支持在线状态和离线消息。顺序只保证会话内有序，不为群聊过度设计。

开始回答时复述这些范围，问面试官是否需要已读回执和消息撤回。

我会先持久保存消息，再尝试实时投递，这样接收方短暂离线也能补回来。范围先限定在单设备、1 对 1 私聊，只保证会话内有序，不扩展到群聊和频道；是否要已读回执、撤回，需要先问清楚。

比如 Alice 给 Bob 发消息，消息服务找到两人的 `conversation_pair`，追加到会话日志并分配 seq，写成功才回“已发送”。投递服务发现 Bob 的 presence 尚未过期，连接在网关 3，就把消息推过去。Bob 客户端收到后 ack，服务端推进 `delivery_cursor` 并告诉 Alice received；等 Bob 打开会话，再单独上报 read。

连接网关维护用户到 socket 的映射，消息数据包括 `message(seq, id, from, to)`，每对用户的 `conversation_pair` 唯一。`presence(last_heartbeat, expires_at)` 只能近似表示在线，sent、received、read 要分别记录。旧心跳可能让已经断开的用户看起来在线，所以持久化不能取决于 presence。

推送失败时消息还在日志里，Bob 重连后按 cursor 拉取，重复消息按 id 去重。比较 Kafka 和 Redis 时，我会先说明各自承担什么角色：要耐久消费者和日志重放的消息流适合 Kafka，低延迟的 presence 和路由表适合 Redis。

容量估算看连接数对应的内存和心跳频率，验证时看持久确认、端到端接收和离线补取的时延，再看误判在线的比例。

### 面试追问与参考回答

**用 Kafka 还是 Redis？**
按角色选，而不是二选一。需要日志重放和耐久消费者的消息流适合 Kafka；低延迟的 presence 和路由表适合 Redis。

**Bob 的网络闪断了几秒，这期间的消息会丢吗？**
不会。消息在推送之前已经写进会话日志，推送失败只影响实时性；Bob 重连后报告自己的 `delivery_cursor`，服务端把之后的消息补给他。

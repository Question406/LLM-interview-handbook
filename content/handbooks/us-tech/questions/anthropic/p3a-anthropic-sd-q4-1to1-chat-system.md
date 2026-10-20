---
id: p3a-anthropic-sd-q4-1to1-chat-system
section: anthropic
order: 622
level: A
title: "Anthropic：单设备一对一聊天：投递、在线状态与离线队列"
quick: "1 对 1 聊天用持久消息日志保证离线补取，WebSocket 管理在线连接，presence 只是基于心跳超时的近似。"
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

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

持久消息日志保证用户离线后能补取消息，WebSocket 负责在线连接。在线状态（presence）是用心跳和超时算出来的近似值，不是绝对事实，不能拿它决定消息是否需要保存。

比较消息中间件时，按需求逐项看：是否需要重放、持久性要求多高、延迟要求多低。另外，"已送达"和"已读"是两个不同的事件。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

只做 1 对 1，每个用户只有一台设备，支持在线状态和离线消息。顺序只保证会话内有序，不为群聊过度设计。

开始回答时复述这些范围，问面试官是否需要已读回执和消息撤回。

### 一套可展开的参考答案

**1. 架构与关键路径。** 连接网关维护"用户 → socket"的映射。消息服务先把消息持久写入会话日志；投递服务再查接收方是否在线、连在哪个网关。不在线就留在消息库里，等对方按 cursor 补取。

**2. 数据模型和状态变化。**

- `conversation_pair`：每对用户唯一。
- `message(seq, id, from, to)`
- `delivery_cursor`
- `presence(last_heartbeat, expires_at)`

sent、received、read 分别记录，不能用"对方在线"代替"已送达"。

**3. 走一遍一条消息。** Alice 给 Bob 发消息，消息服务找到两人的 `conversation_pair`，把消息追加到会话日志并分配 seq，写成功后回给 Alice "已发送"。投递服务查到 Bob 的 presence 未过期、连在网关 3 上，于是把消息推过去。Bob 的客户端收到后回 ack，服务端推进 Bob 的 `delivery_cursor` 并把 received 告诉 Alice；Bob 打开会话时再上报 read。

**4. 失败、重复与恢复。**

- 连接其实已经失效时推送会失败；接收方重连后从 cursor 拉取未收到的消息。
- 重复消息按 id 去重。
- presence 是超时近似，服务端不能因为一次旧心跳就认定用户在线，从而丢掉本该保存的离线消息。

**5. 容量和验证指标。** 监控发送的持久确认时延、端到端接收时延、离线补取时延和"误判在线"的比例。每个连接占用的内存和心跳频率决定了网关的规模。

### 面试追问与参考回答

**用 Kafka 还是 Redis？** 按角色选，而不是二选一。需要日志重放和耐久消费者的消息流适合 Kafka；低延迟的 presence 和路由表适合 Redis。

**Bob 的网络闪断了几秒，这期间的消息会丢吗？** 不会。消息在推送之前已经写进会话日志，推送失败只影响实时性；Bob 重连后报告自己的 `delivery_cursor`，服务端把之后的消息补给他。

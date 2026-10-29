---
id: drustz-29605cc7aa95ae81a0
section: openai
order: 25
level: A
title: Design Slack
quick: original-structured-preparation-guide · Design Slack
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/design-slack
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Design Slack：从私聊到十万人大频道

## 证据边界

当前锁定条目的公开摘要明确写了六个题眼：私聊、频道、多设备投递、通知、规模化以及大频道/分片。用户本地保存的同题面经进一步记录：先讨论 DM，再讨论 channel；小频道采用 push，大频道考虑 pull；面试官继续追问能否统一成 pull、多设备 inbox 是否膨胀、数据库怎样扩展。另一个公开同题族给出 2 至 100K 成员以及小会话与大频道不同的延迟预算。下面因此是一份可用于面试的独立中文设计稿，不是会员正文的复制。100K、200ms/500ms 只作为容量演练参数；若面试官没有给出这些数字，应先确认频道上限、历史消息保留期、是否需要全文搜索、线程/表情/编辑删除是否在范围内。核心目标限定为：用户可发 DM 和频道消息，在多个在线设备实时收到消息，离线后可补齐历史并获得合适的推送通知；单个频道内尽量保持可解释的顺序，系统允许至少一次投递，但客户端展示不能重复。

## 完整需求、接口与请求流程

建议先写四个接口：`POST /conversations/{id}/messages` 接收 `client_message_id`、正文与附件引用；`GET /conversations/{id}/messages?after_seq=` 补拉历史；`POST /conversations/{id}/read` 推进用户已读游标；WebSocket 订阅实时事件。例：小频道 C 有 80 人，用户手机以 `client_message_id=m7` 发“今晚发布”。网关鉴权并检查成员资格，消息服务用该idempotency key去重，在 C 的有序日志追加服务器 `message_id` 和 `channel_seq=901`；提交成功后才回应发送者。异步 fan-out 把轻量事件送到在线成员所在的 WebSocket gateway，并为离线且满足通知规则的成员生成移动推送。某成员的笔记本断网后携 `after_seq=897` 重连，服务从日志返回 898 至 901，客户端按 `message_id` 去重，再把 read cursor 推到 901。超大公告频道不复制完整消息给十万人，只广播“C 已更新到 901”的提示，设备随后按游标拉取。这样 push 指实时信号，pull 指正文读取，两者并不矛盾。

## 架构与关键取舍

持久层以 conversation 为逻辑分区保存 append-only message log，频道元数据和 membership/role 单独存储；写入路由按 `conversation_id` 到单主分区，在该分区分配递增序号，避免用全局序号制造瓶颈。WebSocket gateway 只维护连接，connection registry 保存 `user_id → device sessions`，消息不应永久塞在每个 session inbox。小频道采用 fan-out-on-write：日志提交后向每个成员的短期 inbox/连接事件流写引用，低延迟且读便宜。成员数跨过阈值后采用 fan-out-on-read：只写一份频道日志和少量更新信号，读请求按用户游标取正文，避免一条消息产生十万次持久写。阈值由写频率、活跃成员比例和延迟成本动态决定，不必硬编码。通知服务消费已提交事件，结合免打扰、@mention、在线状态和未读状态决定是否推送；presence/typing 是可丢失的临时状态，不能与消息真相共用一致性要求。搜索、未读计数、分析均由日志异步派生，失败不阻塞发消息。

## 容量、复杂度与故障测试

先用变量估算：峰值消息率 M、平均小频道成员 S、超大频道活跃读者 A。小频道 fan-out 成本约 `O(S)`，大频道写入保持 `O(1)`，代价转为活跃读者的 `O(A)` 拉取；历史分页按 `(conversation_id, seq)` 索引近似 `O(log N + page_size)`。分片首先按 conversation，热点频道再把“持久顺序日志”与“下游投递”拆开：单分区仍决定顺序，下游可按用户或区域并行；盲目把同一频道随机分片会丢掉顺序。必须测试：发送者超时重试不会生成两条消息；日志已提交但 fan-out worker 崩溃可从 offset 重放；WebSocket 断线、跨设备重复到达、设备长期离线后游标过旧；成员被移出频道后不能再补拉；编辑/删除与原消息乱序到达；十万人频道突发 @channel 不形成通知风暴；热分片、缓存失效、区域故障以及 push provider 限流。监控写入提交延迟、端到端投递 p95/p99、重复/缺口率、重连补拉量、每条消息 fan-out 放大倍数和通知抑制率。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/design-slack)
- [相关来源](https://www.1point3acres.com/bbs/thread-1174549-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

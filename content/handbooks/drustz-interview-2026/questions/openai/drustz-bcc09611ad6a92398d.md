---
id: drustz-bcc09611ad6a92398d
section: openai
order: 141
level: A
title: Chatbot Development
quick: original-structured-preparation-guide · Chatbot Development
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
      https://www.1point3acres.com/interview/problems/e7a36cff-619e-4b81-b325-fd12dae70bd1
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Chatbot Development：可扩展事件驱动 ChatApp

> 内容定位：标题更接近“从零开发”而非“重构旧函数”。本地同题族资料确认 AwayBot、MeetBot、TacoBot 和跨 bot 状态交互；以下接口是原创实现约定。

## 练习版需求

实现 `ChatApp.register(bot)`、`ChatApp.send(user, text)` 和 `ChatApp.messages()`。系统至少支持三类能力：AwayBot 管理/查询离开状态，MeetBot 创建会议并把参与者标为忙碌，TacoBot 处理赠送与余额。新增 bot 只能通过注册完成，不修改 ChatApp 主流程。

与直接遍历 bot 不同，本题用事件总线隔离协作：

```text
UserMessage  -> CommandParsed -> MeetingCreated -> PresenceChanged
                           \-> TacoGranted
BotReply     -> append to channel log
```



例如 `/meet @bob` 由 MeetBot 消费并发布 `MeetingCreated`；PresenceProjection 监听该事件更新 Alice/Bob 状态，AwayBot 无需依赖 MeetBot 类。

## 实现方案

EventBus 保存 `event_type -> ordered subscribers`。`send` 生成 `request_id`，把事件放入 FIFO 队列；循环取出事件，先持久化需要审计的事实，再调用其订阅者，把新事件追加到队尾。每个状态更新 handler 以 `(request_id, handler_id)` 做幂等去重。bot 只返回事件，不直接写全局日志，因此单元测试可以传 fake bus、fake clock 和 fake meeting-link provider。

若要异步化，可以让 handler 返回 awaitable，但同一 channel 内仍应按 sequence number 提交结果；跨 channel 才并行。失败事件进入 dead-letter/error log，避免半条命令静默消失。

## 复杂度与边界

若一次用户操作最终产生 `E` 个事件，各事件平均有 `S` 个订阅者，则时间为 `O(E·S)`，队列与本次派生事件占 `O(E)`；历史占 `O(H)`。必须测试事件环、同一请求重放、两个 bot 同时写同一状态、订阅顺序、用户与 bot 同名、handler 超时、频道隔离和历史持久化。若需求不允许 bot 输出再次触发命令，应从类型层区分 `UserMessage` 与 `BotReply`，而不是只靠文本前缀猜来源。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/e7a36cff-619e-4b81-b325-fd12dae70bd1)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-f904ddca2fac4e3c82
section: openai
order: 48
level: A
title: Message Event Aggregation in a 5-Minute Sliding Window
quick: >-
  original-structured-preparation-guide · Message Event Aggregation in a
  5-Minute Sliding Window
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
      https://www.1point3acres.com/interview/problems/a4cd6a8e-afaa-5155-9e02-d089c0210493
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 5 分钟滑动窗口中的消息事件聚合

> 公开 OJ 描述已与当前 UUID 精确对应；旧的 system-design 题目清单已移除。

## 清晰的问题模型

每个事件包含：

```text
timestamp, user_id, chat_id, event_type
```



`event_type` 为 `message`、`react` 或 `end_chat`。对每条事件，在闭区间 `[t-300, t]` 内输出：

1. 同一 `chat_id` 的 `message` 数量；
2. 当前用户的活跃 chat 数。

`(user_id, chat_id)` 在窗口内最新的状态事件是 `react` 时算活跃，最新是 `end_chat` 时不活跃。时间戳可能乱序；同 timestamp 按原输入顺序，最终结果也按原输入顺序返回。`n ≤ 200000`。

## 离线排序 + 滑动窗口

先给事件附原下标，再按 `(timestamp, original_index)` 排序；处理结果写回原下标。

```text
message_times[chat] = 窗口内 message 时间 deque
state_events[(user,chat)] = 窗口内 react/end_chat deque
active_count[user] = 当前活跃 chat 数
```



每次处理时间 `t`：

1. 从各全局驱逐队列中删除 timestamp `< t-300` 的事件；注意 `t-300` 仍在闭区间内；
2. message 事件加入该 chat 的 deque；
3. react/end_chat 加入对应 pair 的状态 deque；加入前后比较“最新状态是否为 react”，据此更新 `active_count[user]`；
4. 写回该事件的 chat message 数与用户 active count。

驱逐状态事件时，同样比较该 pair 驱逐前后的活跃布尔值。每个事件使用唯一 `(timestamp, original_index)` 标识，确保同 timestamp 顺序稳定。

## 复杂度

排序 `O(n log n)`；滑窗维护总计 `O(n)`；空间 `O(n)`。

## 边界

闭区间端点、同 timestamp 原顺序、pair 的最后状态过期后是否回到更早仍在窗内的状态、只有 `message` 没有状态事件、重复输入，以及输出必须还原原顺序。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a4cd6a8e-afaa-5155-9e02-d089c0210493)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

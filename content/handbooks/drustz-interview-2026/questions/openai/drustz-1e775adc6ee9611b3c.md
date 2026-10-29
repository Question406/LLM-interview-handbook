---
id: drustz-1e775adc6ee9611b3c
section: openai
order: 167
level: A
title: Design a Simple iOS Application
quick: original-structured-preparation-guide · Design a Simple iOS Application
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
      https://www.1point3acres.com/interview/problems/e8fe101f-5f9a-4562-b204-ce991fded895
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 简单 iOS 登录与聊天应用

## 题目要做什么

设计一个支持当前主流 iOS 设备的应用，至少包含：

- 注册与登录；
- 发送聊天消息；
- 接收聊天消息；
- 代码结构、主要模块和关键伪代码；
- 实现中可能遇到的挑战以及解决方法。

## 推荐架构

```text
App
├── AuthSession / RootView
├── Features/Auth
│   ├── LoginView
│   ├── RegisterView
│   └── AuthViewModel
├── Features/Chat
│   ├── ChatView
│   └── ChatViewModel
└── Data
    ├── APIClient
    ├── AuthRepository
    ├── ChatRepository
    └── KeychainStore
```



使用 SwiftUI + MVVM 时，登录成功后把 token 写入 Keychain，由 `AuthSession` 决定显示认证页还是聊天页。

## 消息流程

发送消息时可以做 optimistic update：

1. 为本地消息生成客户端 UUID，并立即插入列表；
2. 调用服务端发送接口；
3. 成功后用服务端 ID 和时间戳更新本地消息；
4. 失败时标为可重试，而不是静默删除。

接收消息根据后端能力选择 WebSocket、SSE 或轮询。必须处理重复消息、乱序和重连。

## 复杂度

在数组尾部追加一条消息平均为 `O(1)`；展示 `m` 条消息需要 `O(m)` 时间和空间。实际应用应分页加载，避免历史消息无限占用内存。

## 容易踩坑

- token 过期和安全存储；
- 用户重复点击发送；
- 离线重试和idempotency key；
- 消息到达顺序与服务器顺序不同；
- 键盘遮挡、动态字体、VoiceOver；
- 异步任务取消以及只在主线程更新 UI。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/e8fe101f-5f9a-4562-b204-ce991fded895)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

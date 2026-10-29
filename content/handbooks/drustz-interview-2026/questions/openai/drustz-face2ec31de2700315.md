---
id: drustz-face2ec31de2700315
section: openai
order: 49
level: A
title: Build a ChatGPT Chat Interface in an Existing iOS Project
quick: >-
  original-structured-preparation-guide · Build a ChatGPT Chat Interface in an
  Existing iOS Project
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
      https://www.1point3acres.com/interview/problems/ce24bf6d-a01f-58db-9fa8-dccd80e7fa1b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 在现有 iOS 项目中实现 ChatGPT 式聊天界面

> 内容定位：当前 UUID 的公开标题可确认，本地资料还记录了“现有 codebase、约 40 分钟、iOS chat interface”的相关题。没有当前会员页完整 README，所以下面是可落地的准备版本，未声称还原隐藏 UI 细节。

## 建议实现的功能

在给定 SwiftUI 或 UIKit 项目里补齐聊天屏：按时间显示用户/助手消息；底部输入框发送消息；请求中显示 loading 或流式文本；失败可重试；发送后滚动到最新消息。已有网络 client、model 和 design system 应优先复用，不要在短时间内另起架构。

## 状态与接口

```swift
struct Message: Identifiable {
    let id: UUID
    let role: Role
    var text: String
    var status: Status       // sending, streaming, complete, failed
}

protocol ChatService {
    func streamReply(to messages: [Message]) -> AsyncThrowingStream<String, Error>
}
```



页面状态至少包含 `messages`、`draft`、`activeRequestId` 和错误信息。能否发送由状态推导：`draft.trimmed` 非空且当前没有互斥请求。若题目允许多请求并行，则每条 assistant placeholder 自己保存 request ID。

## 主流程

用户点击发送时先捕获并清空 draft，追加 user message 与空的 assistant placeholder。启动 `Task` 消费 token stream，每到一个 chunk 就追加到对应 placeholder；正常结束设为 complete，异常设为 failed。所有异步更新应回到 `@MainActor`，页面销毁或重新发送时取消旧 Task。

```text
send → append user → append assistant placeholder
     → for chunk in stream: assistant.text += chunk
     → success / failed
```



滚动应由“消息新增或当前回复文本变化”触发，但要尊重用户主动向上浏览：可仅在用户接近底部时自动跟随，避免每个 token 抢走滚动位置。

## 例子

输入全为空格时按钮禁用；输入“解释 BFS”后立即看到自己的气泡和加载态；服务返回三个 chunk 时，同一 assistant 气泡逐步增长，而不是新增三条消息；失败后保留原问题并显示重试按钮。

## 复杂度与边界

设共 `m` 条消息、流式回复长度 `L`。列表渲染应复用 cell；直接逐 chunk 拼 Swift String 最坏可能反复复制，可缓冲后按帧合并，整体目标 `O(L)`。覆盖空输入、快速双击、请求取消、迟到 chunk、Unicode、键盘遮挡、超长文本、旋转/后台恢复、VoiceOver、深色模式和网络失败。面试中先跑现有测试，再做最小正确改动，通常比重构整个项目更重要。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ce24bf6d-a01f-58db-9fa8-dccd80e7fa1b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

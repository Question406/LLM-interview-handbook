---
id: drustz-0b4cdd3c86bb853d3b
section: openai
order: 4
level: A
title: Design AI Chatbot System
quick: original-structured-preparation-guide · Design AI Chatbot System
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
      https://www.1point3acres.com/interview/problems/company/openai/design-ai-chatbot-system
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Design AI Chatbot System：无服务端持久化版本

> 修正说明：旧资料误挂了一道“共享 channel 中的多命令 bot”题。那不是这个条目描述的 ChatGPT 式前端系统，现已移除。

## 可以确认的题意

设计一个类似 ChatGPT 主界面的简单 AI 聊天系统。重点是前端架构和完整交互流程；公开摘要明确说明**不需要服务端持久化**，所有会话状态只保存在当前客户端内存中。

建议先确认是否需要真实模型 API。如果没有，就用可取消的异步生成器模拟流式回答。

## 状态模型

```typescript
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: "streaming" | "done" | "error";
};

type ChatState = {
  conversations: Conversation[];
  activeConversationId: string | null;
  draft: string;
  requestId: string | null;
};
```



用 reducer 管理 `createConversation`、`sendMessage`、`appendToken`、`finishResponse`、`failResponse` 和 `cancelResponse`。不要在多个组件中各存一份 messages，否则切换会话时很容易不同步。

## 发送消息流程

1. 拒绝纯空白输入，并防止同一会话重复提交；
2. 立即加入 user message；
3. 再加入一个空的、状态为 `streaming` 的 assistant message；
4. 每收到一个 token，只更新该 assistant message；
5. 成功后标为 `done`，失败后保留已有文本并显示重试；
6. 新建会话、切换会话或点击停止时，取消旧请求，忽略过期 request ID 的后续 token。

## 复杂度

若消息保存在普通数组，追加一条消息摊销为 `O(1)`；更新列表中间某条消息通常为 `O(m)`。可以用 `messageById + orderedIds` 把定位降为平均 `O(1)`。页面保存的文本空间与全部消息字符数成正比。

## 边界

空输入、连续双击、流式中途失败、取消后仍到达的 token、切换会话、超长回答、自动滚动与用户手动向上阅读的冲突。刷新页面后数据丢失是题目“不持久化”假设的自然结果，应在说明中写清楚。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/design-ai-chatbot-system)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: p3a-openai-design-ai-chatbot-system
section: openai
order: 641
level: A
title: "OpenAI：浏览器保存状态的 AI 聊天界面"
quick: "服务端不能存对话时，我会把会话、消息和生成状态放在浏览器 IndexedDB，服务端只做认证、限额与模型代理。比如用户刷新后从本地恢复消息，生成断线则保留片段并标失败；多标签写入和跨设备能力要明确约定。"
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
  - title: "1Point3Acres · OpenAI · design-ai-chatbot-system"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-ai-chatbot-system
    type: secondary
---

我会把会话、消息和流式增量都保存在浏览器，服务端只做认证、限额和模型代理，密钥留在服务端。比如用户发送后立刻刷新，已经写进 IndexedDB 的输入还能恢复，生成中的助手消息则按本地状态展示。

题目明确要求服务端不持久化对话，支持多会话、流式生成、取消和刷新恢复。开始时要确认隐私、容量、是否跨设备，以及日志能否记录请求元数据，再选择本地存储契约。浏览器用 SSE 或 fetch streaming 请求代理；输入保存和生成是两个独立生命周期，生成失败不能导致用户输入丢失。

本地数据有 conversation、message、run 和 `chunk_cursor`，每次生成用 request id 区分，消息状态为 draft / streaming / done / failed。用户回车后，先把输入写入 IndexedDB，再建 run 与 streaming 助手消息，把本地上下文和 request id 发给服务端。服务端校验身份和额度后转给模型，再转回流式片段；前端逐段追加、推进 `chunk_cursor`，结束后标 done，服务端请求结束不留下对话内容。编辑旧消息时，要明确产生分支还是覆盖。

掉线后保留已有片段并标 failed；重试新建 run，只有明确支持断点恢复时才复用旧 run。多标签通过版本号或广播协调，避免同时写坏会话。长对话分页加载，本地删除后下一次请求立即移除相应上下文。验证首 token 时延、渲染帧率、存储配额错误和取消响应速度。

## 追问

**跨设备同步怎么办？**
默认不支持。可以让用户显式导出导入，或重新讨论端到端加密同步的范围。

**清空浏览器数据后还能找回聊天吗？**
不能。服务端没有副本，产品需要提前说明，并提供导出入口。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

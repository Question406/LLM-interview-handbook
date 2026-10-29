---
id: drustz-eb794be5f49a478e56
section: forum-notes
order: 84
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 3: API Definition'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 3: API Definition'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Step 3: API Definition

We need clear rules for how the frontend (browser) talks to the backend (server).

### Main API Calls

```text
// Managing Prompts
createPrompt(userId: string, content: string, tags: string[]): Promise<Prompt>
updatePrompt(promptId: string, content: string): Promise<PromptVersion>
getPrompt(promptId: string): Promise<Prompt>

// Managing Versions (History)
getVersions(promptId: string): Promise<PromptVersion[]>
revertToVersion(promptId: string, versionNumber: number): Promise<PromptVersion>

// Running the Prompt
// Returns an ID to track the job
executePrompt(promptId: string, model: string, params: ModelParams): Promise<ExecutionId>

// Real-time Updates (WebSocket)
// The server sends these messages to the client:
{
  type: "TOKEN",      // A piece of the answer
  text: "..."
}
{
  type: "DONE",       // Finished
  cost: 0.05          // How much it cost
}
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

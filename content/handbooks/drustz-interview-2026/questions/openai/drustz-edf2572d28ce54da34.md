---
id: drustz-edf2572d28ce54da34
section: openai
order: 138
level: A
title: Problem Prompt and ChatGPT Integration
quick: original-structured-preparation-guide · Problem Prompt and ChatGPT Integration
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
      https://www.1point3acres.com/interview/problems/c8b8d1cc-ca59-4dcb-ab59-b78f66ec1ea8
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Problem Prompt and ChatGPT Integration：相关准备指南

> 内容定位：除公开标题外，本地没有找到能与当前 UUID 精确绑定的完整题面。标题可能指前端接入、prompt playground，或一道“把题目送给模型并显示结果”的集成题。下面只提供覆盖这些交集的练习方案，置信度较低，不能当会员原文。

## 建议先澄清

面试开始先问：要调用真实 API 还是 mock？是一次性响应还是 streaming？需要保存历史吗？prompt 是否允许编辑模板与参数？错误、取消、rate limit 和 API key 由谁处理？若面试仓库已经给出 client，应沿用它，不要把密钥放进浏览器。

## 可练习的最小产品

页面左侧显示 problem statement，右侧提供 system prompt、user prompt、模型参数和 Run 按钮；运行后显示 loading、增量输出、耗时和错误。一次运行保存不可变快照：

```ts
type Run = {
  id: string;
  problemId: string;
  systemPrompt: string;
  userPrompt: string;
  params: { temperature: number; maxTokens: number };
  output: string;
  status: "queued" | "streaming" | "done" | "error";
};
```



前端调用自己的 `/api/runs`，后端再调用模型供应商。这样 API key 留在服务器，也能统一做鉴权、限流、审计和重试。每次请求带 idempotency key；服务端保存 prompt 的版本快照，避免用户随后编辑文本导致旧 run 显示成新 prompt 的结果。

## 交互流程

点击 Run 时校验输入，创建 run 与 `AbortController`；响应 chunk 必须按 run ID 写入对应记录。Stop 只终止当前 run，不清空已经收到的文本。Retry 默认复制旧参数创建新 run，便于比较，而不是覆盖历史。若要支持多轮 chat，则把 `thread -> messages -> runs` 分层，模型请求从已确认的 message snapshot 构造。

## 小例子

用户对同一题连续发起温度 0 和 0.8 两次运行。两者可以并行、各自流式更新，最终保留独立参数和输出；后到的 chunk 不应覆盖“当前选中”的另一条结果。服务返回 429 时显示可重试状态，并尊重 `Retry-After`，不进行无上限即时重试。

## 复杂度与边界

浏览器端处理成本与所有输出总长度 `L` 成正比，状态空间 `O(L+r)`（`r` 为 run 数）；历史很多时需分页/虚拟化。重点覆盖空 prompt、超长输入、XSS/Markdown sanitization、并发 run、取消后的迟到 chunk、刷新恢复、API 429/5xx、断线重连、token 预算和密钥泄漏。由于题面未确认，任何 schema、布局和模型参数都应标为练习约定。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/c8b8d1cc-ca59-4dcb-ab59-b78f66ec1ea8)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

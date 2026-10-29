---
id: sd-eval-multimodal
section: llm
order: 27
level: A
title: LLM 评测与多模态应用：如何覆盖质量、成本和故障？
quick: 我会先选能判断是否完成的具体任务。例如代码助手要通过独立测试，文档问答要能找到支持答案的原文，语音助手要执行正确操作。三者不能只用一个总分代替。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Google：Rules of Machine Learning
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: primary
  - title: Anthropic：Building effective agents
    url: 'https://www.anthropic.com/engineering/building-effective-agents'
    type: primary
---

## 题目描述

设计一个评测平台，评估代码助手、文档问答与语音/图片助手的新版本。输入为候选模型、prompt、工具版本和任务集；输出为可追溯报告及发布建议。请定义离线测试、人工抽查、在线实验和 regression criteria，说明评测污染、模型裁判偏差、多次 sampling 与工具非确定性的处理。所有任务集与 threshold 由练习自行设定。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 我会先选能判断是否完成的具体任务。
>
> **做法与原因：** 每次评估要固定模型、prompt、数据和工具版本，让新旧模型处理相同任务。
>
> **检查与取舍：** 发布时，我会分别看任务质量、重要失败和成本。

## 可以这样回答

我会先选能判断是否完成的具体任务。例如代码助手要通过独立测试，文档问答要能找到支持答案的原文，语音助手要执行正确操作。三者不能只用一个总分代替。

每次评估要固定模型、prompt、数据和工具版本，让新旧模型处理相同任务。自动 judge 可以扩大评价规模，但要用可信样本检查它是否偏爱长度或风格。

发布时，我会分别看任务质量、重要失败和成本。假设新模型平均分更高，却更容易把 PDF 中的金额读错，就需要单独处理这个问题，而不是让其他任务的收益把它平均掉。

## 技术备查

## 参考答案与设计讨论

评测绑定模型、数据、prompt 与工具版本；多模态应用还要按输入类型拆分延迟和失败指标。

### 先定义能验收的任务

代码看测试与可复现问题，RAG 看依据和引用，工具任务看最终业务状态。模型裁判可帮助扩展评分，但要用人工标注 calibration 偏差，不能只由另一个模型说“好”。为每种输入和任务设质量、延迟与费用护栏。

### 记录完整版本和执行

运行绑定数据快照、模型、prompt、检索索引与工具环境，保存必要轨迹。隔离开发集与最终留出集，控制公开测试被反复调优造成的污染。随机输出重复 sampling 并报告不确定性，不能把单次成功当作稳定能力。

### 多模态与线上链路

图片分辨率、页数、音频长度会改变成本和延迟；语音还要看打断、首响应与 ASR 错误传播。离线回放不等于真实线上效果，新版本通通过 acceptance checks 后仍需受控灰度和回滚。权限与工具环境变化也可触发回归。

### 示例与关联

新模型平均分提高，但 PDF 小字任务引用错误率上升，应按该切片的发布护栏判断。详见[离线评测](?book=us-tech&section=design&question=design-offline-eval)、[Agent 评测](?book=us-tech&section=design&question=design-eval-agent)、[代码助手](?book=us-tech&section=design&question=design-code-assistant)、[多模态助手](?book=us-tech&section=design&question=design-multimodal-prod)和[视觉引用与 token 预算](?book=us-tech&section=design&question=design-mm-assistant)。


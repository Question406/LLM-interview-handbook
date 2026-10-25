---
id: p3a-openai-gpt-3-playground
section: openai
order: 638
level: A
title: "OpenAI：GPT Playground：流式生成和参数预设"
quick: "每次生成先固定参数 snapshot 和 request id，流式事件按 run id、递增序号写回对应面板。编辑草稿不改正在运行的任务，共享预设明确版本和权限，取消、重试分别定义语义。"
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
  - title: "1Point3Acres · OpenAI · gpt-3-playground"
    url: https://www.1point3acres.com/interview/problems/company/openai/gpt-3-playground
    type: secondary
---

## 题目

设计一个类似 GPT-3 Playground 的全栈系统：用户输入 prompt、调整参数、看流式结果，并能保存预设。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

每次运行都绑定不可变的参数快照和 request id，用户继续编辑时，只改草稿。流式事件带 run id 和递增序号，前端按这个归属更新面板，切换 tab 或 prompt 也不会把结果写错地方。

练习是多人实验平台，支持编辑 prompt 和参数、保存版本、对比运行和共享预设。先确认团队空间和用量配额，另外约定取消与重试的语义。

前端维护编辑中、生成中、完成和失败几种状态。后端 API 连接 prompt 版本库、run 记录库和模型代理，每次运行保存 snapshot。数据模型包括 `prompt(id, owner)`、`version(body, params, parent)`、`run(version, input, status, output_events, usage)` 和 `share(resource, role, expiry)`。

比如用户把 temperature 调到 0.7 并运行，前端先存 version 或引用已保存版本，后端据此建 run、返回 run id，模型代理开始流式输出。事件只追加到这个 run；之后再改 temperature，正在跑的参数仍不变。并发保存时检查 version，有冲突就让用户选择合并方式。

共享链接指向固定版本，或明确写「跟随最新」，同时定义谁能看、谁能改。监控实验复现率、run 失败率、参数校验错误、每用户成本和流式事件延迟。保存完整输入和模型标识才便于重放；模型服务换版时，也要说明结果可能改变。

## 追问

**分享预设会暴露 API key 吗？**
不应该。密钥在服务端凭证库绑定 owner，分享只包含必要的 prompt 和输入；敏感测试样例单独授权。

**同一版本两次结果为什么不同？**
先看 snapshot 的 seed 和 temperature，温度大于 0 时采样有随机性。seed、参数都相同还不同，再查两次 run 的模型标识，确认服务是否换版。

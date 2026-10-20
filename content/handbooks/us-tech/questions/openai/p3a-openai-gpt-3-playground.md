---
id: p3a-openai-gpt-3-playground
section: openai
order: 638
level: A
title: "OpenAI：GPT Playground：流式生成和参数预设"
quick: "每次生成都绑定一份不可变的参数快照和 request id，前端明确区分编辑中、生成中、完成和失败几种状态。"
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

## 思路

每次生成都要绑定一份不可变的参数快照和 request id。这样用户在生成过程中改参数，正在跑的结果也不会变；结果也能追溯到当时用的设置。

前端状态要区分编辑中、生成中、完成和失败。流式更新必须写回发起它的那个会话，不能因为用户切了 tab 就写到别处。取消和重试各自要有明确语义。分享预设时，要说清楚谁能看、谁能改，以及分享的是哪个版本。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

多人使用的实验平台：用户可以编辑 prompt 和参数、保存版本、运行对比、共享预设。已经开始运行的任务不会因为用户修改参数而改变。

开始回答时复述这些范围，问面试官是否需要团队空间和用量配额。

### 一套可展开的参考答案

**1. 架构与关键路径。** 前端有编辑器和 run 状态机；后端 API 连接 prompt 版本库、run 记录库和模型代理。每次运行保存一份不可变 snapshot。共享链接要么指向某个固定版本，要么明确标为"跟随最新"。

**2. 数据模型和状态变化。**

- `prompt(id, owner)`
- `version(body, params, parent)`
- `run(version, input, status, output_events, usage)`
- `share(resource, role, expiry)`

**3. 走一遍一次运行。** 用户把 temperature 调到 0.7，点"运行"。前端先把当前编辑内容存成一个 version（或引用已保存的版本），后端据此创建 run 并返回 run id，模型代理开始流式输出。每个事件带 run id 和递增序号，前端只把它追加到这个 run 的面板。用户此时再改 temperature 只影响编辑器里的草稿，不影响正在跑的 run。

**4. 失败、重复与恢复。**

- 同一次生成的事件序号递增；用户切换 tab 或 prompt 时，结果仍归属原来的 run。
- 并发保存用 version 检查，冲突时让用户选择怎样合并，不悄悄覆盖别人的工作。

**5. 容量和验证指标。** 监控实验复现率、run 失败率、参数校验错误、每用户成本和流式事件延迟。一次 run 的完整输入和模型标识可以重放；如果模型服务本身换了版本，要向用户说明结果可能不同。

### 面试追问与参考回答

**分享出去的预设会暴露我的 API key 吗？** 不应该。密钥保存在服务端凭证库里并绑定 owner，分享对象只包含必要的 prompt 和输入。测试样例本身可能敏感，需要单独授权。

**两次运行用了同一个版本，结果却不一样，怎么解释？** 先看 snapshot 里的 seed 和 temperature：采样温度大于 0 时本来就有随机性。如果 seed 固定、参数相同还不一样，再查 run 记录里的模型标识，看模型服务是否在两次之间换了版本。

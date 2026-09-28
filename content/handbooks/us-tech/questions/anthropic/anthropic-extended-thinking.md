---
id: anthropic-extended-thinking
section: anthropic
order: 19
level: A
title: Anthropic：extended thinking 的推理预算、延迟，以及为什么不能把 CoT 当产品日志？
quick: >-
  旧接口用 `budget_tokens` 硬预算；新模型走向 adaptive thinking，用 effort 调深度。思考 token
  按输出计费，即使用户只看到摘要或空块。可见文本不是原始 CoT。默认不要展示、不要当监督标签、不要让用户改 thinking 再回传。
tags:
  - Anthropic
  - Extended thinking
  - Latency
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Extended thinking (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
    type: primary
  - title: Thinking overview (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/thinking
    type: primary
---

研究 / 应用岗会问「打开 thinking 质量涨、延迟也涨，产品怎么接」。文档现在把手工 `thinking.type: enabled` + `budget_tokens` 标成过渡：新模型用 adaptive，模型自己决定想不想、想多深；要可预期延迟才谈固定预算。面试别背死某一个字段名，要讲清预算、计费、可见性和安全。这是 API 产品题。

## 预算是目标，不是墙上的硬闸

手工模式：`budget_tokens` 是内部推理的目标长度，且通常必须小于 `max_tokens`，因为思考和最终回答抢同一截输出上限。交错 thinking（工具之间再想）可以让预算跨多个 thinking 块，例外要单独说。文档建议预算很大（大约超过 32k）时走 `anthropic-batch-api`，长连接会先被网关杀掉。

Adaptive：不再设 $N$ 个思考 token，用 `effort` 给软倾向。简单问题可能几乎不想，难题多想。`max_tokens` 仍是硬上限。混流量时 adaptive 更省；SLO 很紧的路径才值得用固定预算或低 effort。

思考块在最终文本之前（或插在 tool 调用之间）。TTFT 会变差：用户要等第一段可见输出。流式可以先推 thinking 摘要，但产品若把显示关掉，用户侧仍像卡住，要用独立的「正在推理」状态，不要假装已经在写答案。流式结束前会有 `signature_delta`，必须收齐再回传，半截 signature 会 400。和在线 serving 的限流一起看 `anthropic-rate-limit`：thinking 吃的是输出 token 桶。

交错 thinking 让模型在每轮 tool 结果之后再想，而不是把所有工具计划压进第一段。代价是多几段输出、延迟更抖。只读检索可以交错；下单、删文件这类副作用，想完也还是宿主确认，见 `anthropic-tool-use`。

## 计费和可见性不是一回事

思考按**完整内部 token**计输出费，即使用户看到的是摘要，或 `thinking` 字段是空的。`usage` 里的 thinking 计数才是账单。摘要生成本身文档写明不加收；别把「我没看到 CoT」理解成「没花」。

官方明确：你看到的从来不是原始思维链。`signature` 是加密后的完整推理，多轮和 tool use 必须原样回传，服务端靠它校验块没被改。安全系统触发时会变成 redacted 块，同样要原样回传。改 thinking 文本再提交，轻则 400，重则把不可信用户输入写进模型自以为的「内心独白」。

Thinking 配置会编进 prompt 前缀，乱切换 effort 会打爆 `anthropic-prompt-cache`。预热缓存时 thinking / effort 必须和线流量一致。

## 为什么产品默认不泄露 CoT

原始 CoT 会带：未说出口的工具计划、内部安全启发式、对用户的负面评价、偶发的竞赛答案。拿它当客服日志或训练标签，等于把对齐不希望用户优化的过程暴露出去。用户若能编辑 thinking，就是注入，和 `anthropic-prompt-injection` 同一类。

我的接法：API 默认不展示，或只给开发者摘要；面向用户只给最终答案。评测 reasoning 质量用任务分数和内部探针，不要用「摘要看起来很聪明」。回传 thinking 块为了连续推理，不等于展示。和 `anthropic-eval-honesty` 一起：摘要里「我不确定」而答案斩钉截铁，要以答案和引用为准，见 `anthropic-citations`。

错法：把可见 thinking 当黄金 CoT 做 SFT；在产品 UI 里默认展开；为了「可解释」把 redacted 块强行解密给用户。

预算很大时走 `anthropic-batch-api`，不要在同步路径上赌超长思考不被网关掐断。交错 thinking 适合只读工具链；有副作用的调用想完仍要宿主确认，见 `anthropic-tool-use`。thinking / effort 必须编进 prompt cache 预热请求，否则线上第一条必 miss。redacted 与 thinking 块都要原样回传，缺一块后续轮次会断。产品侧把 thinking 当调试开关，默认关；可见摘要可以给开发者排障，不要进用户合规日志，也不要做成用户可编辑的草稿箱。评测延迟时把思考时间和可见 token 时间分开报。要流式、要交互就别开超大预算；要质量、可隔夜出数，把高预算题丢进批处理。

## 追问

- **temperature 和 thinking？** 开启后采样常被钉死（例如 temperature 固定为 1）。不要指望靠低温省思考。
- **要不要训练模型模仿可见 thinking？** 模仿的是摘要政策，不是真实搜索。蒸馏推理用教师的完整内部轨迹（若你有），不要用 API 摘要当黄金 CoT。
- **工具循环里 thinking 丢了？** 最后一轮 assistant 的 thinking / redacted 必须完整回传，否则交错推理断掉。
- **延迟预算怎么拆？** 先测无 thinking 的 TTFT 和 decode；再扫 effort 或 `budget_tokens`，画质量–P95 曲线。只报平均质量会把尾延迟藏起来。

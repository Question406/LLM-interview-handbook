---
id: ali-ai-oa
section: alibaba-oa
order: 34
level: B
title: 阿里 AI 研发笔试（选择 + 编程 + Prompt）怎么准备？
quick: >-
  选择覆盖 Transformer/Agent/MCP 加 CS 基础；编程仍是算法；Prompt 题我会写清角色、提取字段、逐步规则、只输出约定
  JSON，并用边界 case 自测。
tags:
  - Alibaba
  - 笔试
  - Prompt
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里 AI 研发 0325 笔试
    url: 'https://www.nowcoder.com/discuss/866741961221292032'
    type: legacy-reference
---

常见误区是：「再刷一套 LeetCode」。阿里 AI 研发 0325 公开复盘是约 20 选择 + 3 编程 + 1 Prompt：选择会考 teacher forcing、MHA/MQA/GQA、ReAct、MCP tool vs resource、多 Agent；编程仍是算法；Prompt 单独计分，格式错、漏边界就是零。三条线缺一就翻车。总复习地图见 `ali-prep-map`。

## 选择：概念要对到实现，不要背名词

高频簇：teacher forcing（训练时输入 gold token，推理没有）；MHA / MQA / GQA 与 KV Cache 带宽；ReAct 是交错 Thought / Act / Obs，不是一次 plan 到底；MCP 里 tool 和 resource 不是一回事（对照 `ali-mcp-vs-fc`）。CS 基础仍会出现：进程线程、锁、索引、TCP。答法是「定义 + 反例」：例如 GQA 不是「少几个头就更快」，而是 KV 头共享、降低解码带宽。选择详解可对 `ali-oa-ai-mcq`。

## 编程：算法题，不要指望 LLM 题救场

三道编程按校招算法准备：实现正确、边界、复杂度。不要把时间全花在 Prompt 上导致编程超时。手撕清单见 `ali-oa-prep-map` 与 `ali-coding-islands`。提交前用最小反例自测（空、单元素、全相同）。

## Prompt：角色、规则逐步写死、只出 JSON

0325 Prompt 是出租车计费一类：角色 + 抽取字段默认值；计费/业务规则逐步写死；夜间加价、不足 1 km、等候不足 5 分钟等边界单独强调；强制遵守 JSON schema；禁止解释性废话。我会把规则引擎写进提示词：先列输入字段，再逐步 if-else，最后「只输出约定 JSON」。用反例自测：不足 1 km、等候不足 5 分钟、夜间跨段。完整题面见 `ali-oa-taxi-prompt`。现场时间紧，先写 schema 和边界，再补角色语气。

笔试后的面试会立刻接到 GRPO/DPO/Agent（`ali-ppo-dpo-grpo-ask`、`ali-grpo-vs-sft`）。笔试过了不等于算法面能白板推公式，选择里见过的名词要能在白板上展开：teacher forcing 为啥推理会暴露偏差、GQA 的 KV 体积怎么写、ReAct 和一次性 plan 差在哪。Prompt 题是把业务规则编译成模型可执行的约束，与线上 Agent 的 schema 校验和拒答设计需要同样的规则表达能力；计费规则漏边界，等价于工具参数没过校验器。建议同步刷牛客 Prompt 题库，但现场以「可自测的 JSON」为第一目标，不要写散文。

## 追问

- **Prompt 写很长会不会更好？** 不一定。规则重复、互相矛盾会被模型随便挑一条。短、逐步、可测比堆形容词重要。
- **MCP 选择怎么挖？** tool 是可调用动作，resource 是可读上下文；把二者说成「都是 function calling」会直接失分。
- **编程和 Prompt 哪个优先？** 编程超时是硬伤；Prompt 建议留 20-25 分钟，先 schema 后边界。

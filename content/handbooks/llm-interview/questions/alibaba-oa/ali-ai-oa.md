---
id: ali-ai-oa
section: alibaba-oa
order: 34
level: B
title: 阿里 AI 研发笔试（选择 + 编程 + Prompt）怎么准备？
quick: >-
  三条线都要准备：选择题覆盖 Transformer、Agent、MCP 加 CS 基础，概念要能对到实现；编程仍是算法题；Prompt
  题我会写清角色和提取字段、把规则逐步写死、只输出约定 JSON，再用 edge cases 自测。
tags:
  - Alibaba
  - 笔试
  - Prompt
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 阿里 AI 研发 0325 笔试
    url: 'https://www.nowcoder.com/discuss/866741961221292032'
    type: legacy-reference
---

三条线都要准备，缺一条就容易翻车。阿里 AI 研发 0325 的公开复盘是约 20 道选择、3 道编程、1 道 Prompt：选择会考 teacher forcing、MHA/MQA/GQA、ReAct、MCP 的 tool vs resource、多 Agent；编程还是算法题；Prompt 单独计分，格式错了、漏了 edge cases 就是零分。所以只「再刷一套 LeetCode」是不够的。总复习地图见 `ali-prep-map`。

选择题的常见 topics 我会按「定义加反例」来记，概念要能对到实现，光背名词没用。teacher forcing 是训练时输入 gold token，推理时没有；MHA / MQA / GQA 要和 KV Cache 带宽联系起来，比如 GQA 的要点是 KV 头共享、降低 decoding 带宽，说成「少几个头就更快」就错了；ReAct 是 Thought / Act / Obs 交错进行，和一次 plan 到底不一样；MCP 里 tool 和 resource 是两回事，对照 `ali-mcp-vs-fc`。CS 基础也会出，进程线程、锁、索引、TCP。选择题详解可以对 `ali-oa-ai-mcq`。

编程按校招算法准备，implementation correctness、edge cases、complexity 都要顾到，别指望 LLM 题救场，也别把时间全花在 Prompt 上导致编程超时。手撕清单见 `ali-oa-prep-map` 和 `ali-coding-islands`。提交前用最小反例自测，空、单元素、全相同。

0325 的 Prompt 题是出租车计费一类：角色加上抽取字段和默认值；计费和业务规则逐步写死；夜间加价、不足 1 km、等候不足 5 分钟这些 edge cases 单独强调；强制遵守 JSON schema；禁止解释性废话。我的写法是把规则引擎写进 prompt，先列输入字段，再逐步写 if-else，最后要求「只输出约定 JSON」，然后拿不足 1 km、等候不足 5 分钟、夜间跨段这几个反例自测。现场时间紧，先写 schema 和 constraints，角色语气最后补。完整题面见 `ali-oa-taxi-prompt`。这类题其实是把业务规则编译成模型能执行的约束，和线上 Agent 的 schema 校验、拒答设计用的是同一种规则表达能力，计费规则漏一个 edge case，就相当于工具参数没过校验器。可以同步刷牛客的 Prompt 题库，但现场以「可自测的 JSON」为第一目标，别写散文。

笔试过了，后面的面试会立刻接到 GRPO / DPO / Agent（`ali-ppo-dpo-grpo-ask`、`ali-grpo-vs-sft`）。笔试过了不等于能在白板上推公式，选择题里见过的名词都要能展开：teacher forcing 为什么推理时会 exposure bias，GQA 的 KV 体积怎么写，ReAct 和一次性 plan 差在哪。

## 追问

**Prompt 写得很长会不会更好？**
不一定。规则重复、互相矛盾，模型会随便挑一条。短、逐步、可测，比堆形容词重要。

**MCP 的选择题会怎么挖？**
tool 是可调用的动作，resource 是可读的上下文；把二者说成「都是 function calling」会直接失分。

**编程和 Prompt 哪个优先？**
编程超时是硬伤。Prompt 建议留 20-25 分钟，先写 schema，再补充 edge-case tests。

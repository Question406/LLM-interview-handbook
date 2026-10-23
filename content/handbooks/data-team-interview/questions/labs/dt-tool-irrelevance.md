---
id: dt-tool-irrelevance
section: labs
order: 26
level: A
title: BFCL：目录里没有能用的工具，模型还是调了，数据上怎么拆？
quick: "补两类示范：当前工具目录完成不了请求时，正确做法是不调用，说明限制或询问用户；缺少信息时，先调只读查询再执行。SFT 如果总假设有工具可用，模型就学会见 schema 就填，编造名称和参数。BFCL 的 Function Relevance Detection 专门测第一类，负例要用语义相近的无关工具来造。"
companies:
  - apple
tags:
  - Gorilla
  - BFCL
  - Tool Use
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Berkeley Function Calling Leaderboard
    url: https://gorilla.cs.berkeley.edu/leaderboard
    type: primary
  - title: "BFCL V3: Multi-Turn Function Calling"
    url: https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

问题出在训练数据里没有「不该调」的样本。我会补两类题：一类是工具目录根本解决不了请求，正确做法是说明限制或询问用户；另一类是必须先查询再调用，检查模型有没有走中间那一步。

监督微调（SFT）的数据如果全是「目录里总有一个工具能用」，模型学到的就是见到 JSON schema 就填参数。约束解码也拦不住，它只保证格式合法，管不了不该调却调了。

第一类是能力边界题。正确回答说明限制或者向用户询问，错误回答编造一个看似合理的调用。它和 `dt-safety-refuse` 结构相同，但标签不要合并成一个 `refuse`，一个是政策，一个是能力边界。BFCL 从 V1 起就有 Function Relevance Detection 这一类，约 240 条：目录里没有相关函数，期望输出是一段普通回复，没有 function call。

第二类是先查再调。比如跳过 `get_zipcode`、直接猜个邮编去查天气，最终结果可能碰巧对，可邮编是猜出来的，应当算幻觉。所以中间的查询工具即使只读、不改变状态，也要检查模型执行了它，只看最终状态会漏掉。BFCL V3 用状态核验加响应核验来补这种中间只读步骤。

## 追问

**目录很大，负例怎么采样？**
按语义相近的无关工具来造题，难度才够。随机抽一个天气函数配数学题，太容易拒，练不到东西。

**有了 schema 约束，模型还会编造工具名吗？**
schema 能防凭空生成工具名，AFM 2025 报告的工具后训练就建立在字段和类型规范（schema）上，见 `dt-guided-gen-data`。该不该调，仍然要靠负例来教。

**线上发现的乱调怎么补？**
记录失败类型，用研究集或合成环境复现同一种失败，再加进训练。

**图里没有的东西，算不算这一类？**
不算。图里没有的东西要依据实际证据拒答，见 `dt-grounding-data`，它和工具目录里没有的能力是两套题，分开记账。

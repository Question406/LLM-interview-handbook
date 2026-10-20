---
id: dt-tool-irrelevance
section: labs
order: 26
level: A
title: BFCL：目录里没有能用的工具，模型还是调了，数据上怎么拆？
quick: "补充两类示范：当前工具无法完成请求时不调用；缺少信息时先查询再调用。如果 SFT 总是假设有工具可用，模型就容易编造名称和参数。用户日志中的失败不能默认直接回灌，可以用研究集或合成环境复现失败类型。"
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

我会加入两类训练题。第一类是当前工具目录无法解决请求：正确回答应说明限制或向用户询问，错误回答则编造一个看似合理的调用。和 `dt-safety-refuse` 同构，标签不要并成一个 `refuse`：一个是政策，一个是能力边界。第二类是必须先查询再调用：即使中间查询工具是只读的、不会改变状态，也要检查模型是否执行了它，不能只看最终状态正确。数据里没有负例，约束解码也拦不住「不该调却调了」。AFM 的工具后训练建立在 字段和类型规范（schema） 上，防凭空生成工具名，见 `dt-guided-gen-data`。

不这么选的理由：监督微调（SFT） 全是「目录里总有一个能用」，模型学会见 JSON schema 就填。只看终局状态会漏掉「跳过 `get_zipcode` 直接猜邮编去查天气」。那是幻觉，不是走了捷径。

接到苹果：用户日志里的乱调默认不能回灌原文，用研究集或合成复现同一失败类型。负例按语义近的无关工具造题，别随机抽一个天气函数配数学题，那太好拒。有实际证据支持拒答（图里没有的东西）见 `dt-grounding-data`，工具目录里没有的能力也要拒，两套题分开记账。

公开锚点：BFCL V1 起就有 Function Relevance Detection，约 240 条，目录里没有相关函数，期望是普通回复不是 function call；V3 用状态核验加响应核验补中间只读。

## 追问

- **目录很大，负例怎么采样？** 按语义近的无关工具造题，别随机抽一个天气函数配数学题，那太好拒。
- **用户日志里的乱调能不能当负例？** 苹果默认不能回灌原文。用研究集或合成复现同一失败类型。
- **和有实际证据支持拒答？** 图里没有的东西要拒，见 `dt-grounding-data`。工具目录里没有的能力也要拒。两套题分开记账。

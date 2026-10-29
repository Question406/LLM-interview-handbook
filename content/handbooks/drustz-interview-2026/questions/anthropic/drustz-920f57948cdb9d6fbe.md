---
id: drustz-920f57948cdb9d6fbe
section: anthropic
order: 10
level: A
title: Rl Fundamentals GRPO Debug
quick: locally-saved-research-summary · Rl Fundamentals GRPO Debug
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-research-summary
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## RL Fundamentals 轮：debug GRPO training loop + 解释 ratio ≠ 1（RE 高频新题）

给一份简化的 GRPO（on-policy RLHF）训练 step 实现，含 3 个埋好的 bug，常见 bug 类型：log-prob 计算错误（未对齐 autoregressive shift）、loss/KL 里 token masking 错误、advantage normalization 错误（组内奖励全相同时除零/无信号）、新旧 policy 混用（rollout 与 update 的 policy 不一致）。每个 bug 要求给出检测方法+具体修复，不能只点名。核心追问：明明设计上严格 on-policy，为什么 importance ratio = exp(log πθ − log  $π_{old}$ ) 不等于 1？要求设计判别实验区分'设计内偏差'（推理引擎与训练器 forward 路径不同、bf16/fp32 数值精度、每个 rollout batch 走多次 optimizer step）与真 bug。Follow-up：clipped surrogate 如何防崩、组内奖励全相同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL penalty 放 reward 里还是 loss 里的 trade-off。应主动澄清：reward 类型、每 batch optimizer 步数、生成与打分是否同一 forward 路径、sampling温度/top-p、KL 实现、数值精度。1p3a 对应帖：interview thread 1167043 'RL Fundamental Interview: Code, Design, and Configuration'、1166898、bbs thread 1167940。

### 解题与准备提示

prachub 页面给了完整评分维度（见 detail）。ratio≠1 三大合法原因：多次 minibatch update 后 πθ 已漂移、vLLM sampling与 HF 训练 forward 的 kernel/精度差异、bf16 舍入；判别实验：同一 checkpoint 用训练器重算生成 log-prob 对比、fp32 复算、第一次 optimizer step 前检查 ratio 是否恰为 1。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug)
- [相关来源](https://www.1point3acres.com/interview/thread/1167043)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

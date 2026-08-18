---
id: pt-grounded-rlvr-reward-staging
section: posttrain
order: 37
level: S
title: RAG / Grounded QA 的 RLVR 如何同时奖励答案正确、引用充分、证据一致和恰当拒答？为什么适合分阶段训练？
quick: 不要把所有子目标粗暴相加。把 retrieval coverage、citation entailment、答案正确和拒答条件拆为可验证信号，先建立可靠引用/拒答行为，再优化端到端答案；否则模型容易用伪引用或过度拒答刷总分。
tags:
  - Grounded QA
  - RLVR
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Lessons from Training Grounded LLMs with Verifiable Rewards
    url: https://arxiv.org/abs/2506.15522
    type: primary
---

grounded QA 的 reward 至少有四层：检索证据是否覆盖关键事实、引用是否真正蕴含声明、最终答案是否正确、证据不足时是否拒答或表达不确定。它们会冲突：只奖 citation count 会堆引用，只奖拒答会让系统保守失用。

因此先为每个子奖励定义独立 oracle 与负例，再用 staged objective 或约束优化。早期可训练引用绑定与 answerability 判断，后期再加端到端质量；每个阶段都要保留前一能力的 regression test。

评测需要同时报 answer correctness、citation precision/recall、unsupported-claim rate、false refusal 和 retrieval miss。最终总分掩盖不了任一安全失败模式。

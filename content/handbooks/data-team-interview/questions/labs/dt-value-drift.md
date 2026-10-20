---
id: dt-value-drift
section: labs
order: 21
level: S
title: Anthropic 笔试：微调之后怎么证明模型相对基座「漂了」？
quick: "用同一批固定 prompt 对比基座和微调模型，同时看 KL、具体行为、安全与有用性的变化，以及分维度人评。KL 大只能说明分布变化，不能说明变好或变坏；总 loss 和 Arena 赢率也不能替代这些检查。对照数据使用研究集和固定评测集。"
companies:
  - apple
tags:
  - Anthropic
  - Evaluation
  - Preference
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)
    url: https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

可以从四个角度检查。先看输出分布：在固定 prompt 集上计算 $\mathrm{KL}(\pi\|\pi_{\mathrm{base}})$ 或 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$，按能力切片。KL 大只说明走远了，不说明好坏。行为套件：拒答、谄媚、有实际证据支持、工具合法性、locale，基座和当前模型同一题并排。安全税：有用性切片和应拒切片分开，见 `dt-safety-refuse`。人评使用小规模双人标注，分别评价忠实、礼貌和完整性。如果只保留一个「更好」分数，迎合用户的回答可能被误判为进步。端侧 3B 和 PCC server 分开报。

不这么选的理由：报一个 KL 数字交差，或把 Arena 赢了说成没漂。漂本身不一定坏，监督微调（SFT） 和 强化学习（RL） 就是要离开基座。我要证明的是离开发生在声明的轴上，锚点能力还在。同场口头题还有「诚实还是仅仅流畅」，数据动作是造「流畅但错 / 短而对」的对，评测单独开忠实维，不要并进 Arena。

接到苹果：AFM 多语课程要护住英语，就是这种对照。用户交互默认不进对照集，对照用研究集和冻结门禁。Director 若追「你怎么知道后训练没把预训练世界知识洗掉」，同一套图：按源 held-out、leave-one-source-out，见 `dt-data-mix-quota`、`dt-neg-transfer`。行为套件版本冻结，新失败模式只追加，不用当前模型刷新标签，见 `dt-contam-hold`。

公开锚点：2025 一趟 Anthropic RE CodeSignal 短答「怎么衡量微调模型相对基座发生了 value drift」；同场另一道是 基于人类反馈的强化学习（RLHF） 系统性奖励不诚实，见 `dt-sycophancy-data`。InstructGPT 已经写过对齐会改能力剖面。

## 追问

- **KL 对哪个锚？** 对外同时报相对预训练基座和相对 SFT。如果只比较不断更新的 ref，就看不出模型从最初基座偏离了多少。
- **行为套件谁维护？** 版本冻结，新失败模式只追加，不用当前模型刷新标签，见 `dt-contam-hold`。
- **多少 prompt 够？** 按危害和产品路径分层，少而硬。报不出分层，数字再大也是平均数。

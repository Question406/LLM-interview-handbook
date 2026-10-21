---
id: dt-eval-harness
section: labs
order: 47
level: S
title: DeepMind：评测台怎么按生产软件的标准来设计？
quick: "核心是让每个分数都可复现、可比较：每次评测记录模型、题集、提示模板、解码参数和种子，并固定打分器版本。小幅涨分要用逐题统计检验。日常跑快速检查、夜间跑全套；不同权重的模型分开报，保存逐题结果来定位回归。"
companies:
  - apple
tags:
  - DeepMind
  - Evaluation
  - Reproducibility
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context"
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: LiveBench
    url: https://arxiv.org/abs/2406.19314
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

脚本和生产软件的区别在于：生产评测台里每个分数都能说清是在什么条件下得到的，能复现，也能和另一个分数公平比较。所以每条分数都要对应 `(model, benchmark, prompt_template, decode, seed)`，其中模型、数据集、模板和参数都要有版本或哈希。少了任何一项，就无法确认两个分数是否在同样条件下得到。

DeepMind / Gemini 评测岗公开涉及泄漏检测、验证集和规模定律，回答要覆盖到这些，光说「跑 MMLU」不够。公开面经和系统设计指南也将 eval harness 列为 DeepMind 相关题型；这里按题型整理，并非某场逐字稿，`realInterview: false`。

## 版本和缓存

数据集、模板和打分器按内容寻址。提示哪怕只改了 3 个词，模板哈希也变了，旧分不再代表新设定，需要重新评测。解码设定也要写清楚，Gemini 1.5 报告就写明了 temperature 0 的采样设定。

生成缓存按这个五元组索引。只更改打分器时，保留原输出重新评分，不必再次采样；全套重跑时，相同五元组也可以直接复用缓存。

## 打分

能执行验证的任务优先用 oracle，judge 更适合作为开发阶段的回归检查，见 `dt-judge-bias`。LiveBench 定期更新题目并使用客观参考答案，就是为了减少公开榜污染和 LLM judge 的文风偏差。

比较两个汇总分时要做统计检验。500 题、准确率 50% 时，95% 置信区间大约是 $\pm 4$ 点，提高 2 点还在误差范围内。要用逐题配对的 McNemar 检验。

## 日常运行

几分钟的快速检查覆盖拒答、工具参数是否合法、污染金丝雀；夜间再运行全套。全套成本太高时，优先运行上次的边界题、新失败模式和安全测试。保存原始逐题记录，出现回归时能直接查看哪些题由对变错。

权重不同的模型各自运行、各自报告套件。训练数据侧的版本纪律见 `dt-repro-lineage`。

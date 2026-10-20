---
id: dt-eval-harness
section: labs
order: 47
level: S
title: DeepMind：评测台怎么设计成生产软件，而不是一堆脚本？
quick: "每次评测记录模型、题集、提示模板、解码参数和种子，并固定打分器版本，才能复现和比较。小幅涨分要用逐题统计检验。日常运行快速检查，夜间跑全套；端侧和 server 分开报，保存逐题结果定位回归。"
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

每条分数都要对应 `(model, benchmark, prompt_template, decode, seed)`。模型、数据集、模板和参数需要版本或哈希；少了其中一项，就无法确认两个分数是否在同样条件下得到。数据集、模板和打分器按内容寻址，提示变化后不能再当作原实验。

生成缓存按这个五元组索引。只更改打分器时，保留原输出重新评分，不必再次采样。

DeepMind / Gemini 评测岗公开涉及泄漏检测、验证集和规模定律，不能只回答「跑 MMLU」。Gemini 1.5 报告写明 temperature 0 的采样设定；LiveBench 强调定期更新题目与客观参考答案，以减少公开榜污染和 LLM judge 的文风偏差。

## 日常检查怎么安排

端侧 3B 和 PCC server 使用不同权重，各自运行、报告套件。能执行验证的任务优先用 oracle，judge 更适合作为开发回归检查，见 `dt-judge-bias`。

几分钟的快速检查可以覆盖拒答、工具参数是否合法、污染金丝雀；夜间再运行全套。保存原始逐题记录，出现回归时能直接查看哪些题由对变错。训练数据中的版本纪律见 `dt-repro-lineage`。

公开参考包括 Gemini 1.5 评测协议和 LiveBench。公开面经、系统设计指南也将 eval harness 列为 DeepMind 相关题型；这里不是某场逐字稿，`realInterview: false`。

## 追问

- 500 题、准确率 50%，提高 2 点算赢吗？95% 置信区间大约 $\pm 4$ 点，不能只比较两个汇总数。用逐题配对的 McNemar 检验。
- 全套成本太高怎么办？优先运行上次的边界题、新失败模式和安全测试；相同五元组可复用缓存。
- 提示只改了 3 个词呢？模板哈希已变，旧分不再代表新设定，需要重新评测。

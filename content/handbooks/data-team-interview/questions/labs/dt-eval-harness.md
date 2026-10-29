---
id: dt-eval-harness
section: labs
order: 47
level: S
title: DeepMind：评测台怎么按生产软件的标准来设计？
quick: >-
  核心是每个分数都能复现、能公平比较：每次评测记下模型、题集、提示模板、decoding 参数和 seed，scorer 版本也固定。小幅涨分要做逐题
  paired test。日常跑快速检查、夜间跑全套，保存逐题结果来定位回归。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Gemini 1.5: Unlocking multimodal understanding across millions of tokens
      of context
    url: 'https://arxiv.org/abs/2403.05530'
    type: primary
  - title: LiveBench
    url: 'https://arxiv.org/abs/2406.19314'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

脚本和生产软件的区别，在于生产评测台里每个分数都说得清是在什么条件下得到的，能复现，也能和另一个分数公平比较。所以每条分数都要对应 `(model, benchmark, prompt_template, decode, seed)`，模型、数据集、模板和参数都带版本或哈希。少了任何一项，就没法确认两个分数是不是在同样的条件下跑出来的。

比如有人说新 checkpoint 在某个 benchmark 上涨了 2 点。一查，提示模板改了 3 个词，decoding 设定也不一样，这两个分其实没法比。

所以数据集、模板和 scorer 都按内容寻址。提示哪怕只改了 3 个词，模板哈希就变了，旧分不再代表新设定，要重新评。decoding 设定也要写清楚，Gemini 1.5 报告就写明了 temperature 0 的 sampling 设定。生成缓存按这个五元组索引：只换 scorer 时，保留原输出重新打分，不必再次 sampling；全套重跑时，五元组相同的直接复用缓存。

打分上，能执行验证的任务优先用 oracle，judge 更适合当开发阶段的回归检查，见 `dt-judge-bias`。比较两个汇总分要做统计检验。500 题、准确率 50% 时，95% confidence interval 大约是 $\pm 4$ 点，涨 2 点还在误差范围里，要用逐题配对的 McNemar 检验。

日常运行分两档：几分钟的快速检查覆盖拒答、工具参数是否合法、contamination 金丝雀，夜间再跑全套。逐题的原始记录都存下来，出了回归能直接看哪些题从对变错。训练数据那边的版本纪律见 `dt-repro-lineage`。

## 追问

**这题 DeepMind 想听到什么？**
光说「跑 MMLU」不够。DeepMind / Gemini 评测岗公开涉及 leakage 检测、validation set 和规模定律，回答要覆盖这些。公开面经和系统设计指南也把 eval harness 列为 DeepMind 相关题型，这里按题型整理，所以标了 `realInterview: false`。

**为什么偏好有客观参考答案的题？**
为了减少公开榜 contamination 和 LLM judge 的文风偏差。LiveBench 定期更新题目、使用客观参考答案，就是这个目的。

**全套太贵、跑不起怎么办？**
优先跑上次的 borderline tasks、新失败模式和安全测试。

**权重不同的模型能放进一张报告里比吗？**
各自运行、各自报告套件。

---
id: dt-ifeval-overlay
section: labs
order: 39
level: A
title: IFEval 只有 541 条，后训练能不能直接拿来训？
quick: "不能。IFEval 的 541 条英文题是评测集，拿来训练就失去了评测意义。正确做法是另造训练集：从自己的 SFT 数据抽任务，叠加同类可执行约束，生成独立的 RLVR 数据。要检查约束能否同时满足，按语言改写检查器，并同时评估内容质量，避免只学格式。"
companies:
  - apple
tags:
  - Google
  - AllenAI
  - Instruction Following
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Instruction-Following Evaluation for Large Language Models
    url: https://arxiv.org/abs/2311.07911
    type: primary
  - title: "Tulu 3: Pushing Frontiers in Open Language Model Post-Training"
    url: https://arxiv.org/abs/2411.15124
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能直接训。IFEval 要留作评测，它的题一旦进入训练，分数就只说明模型背过题。能从 Hugging Face 加载，并不代表评测数据可以直接训练。要用的是它的思路：可执行的约束，另造一份训练集。

## IFEval 和 Tulu 3 的做法

Google IFEval 公开包含约 500 多题、25 类可以用脚本检查的指令，一条 prompt 可以带多条约束。Tulu 3 的 RLVR-IFeval 就是另造训练集的例子：从 Tulu 2 的 SFT 数据抽样，再随机加入同类约束。

## 怎么造训练集

1. **抽任务、加约束。** 从自己的监督微调（SFT）数据抽样，随机加入同类约束，把约束参数保存成 `ground_truth` JSON，用作规则奖励。
2. **检查可满足性。** 生成约束时先检查能否同时满足，例如「少于 50 词」和「列 12 条」可能冲突，无法满足的组合直接丢弃。
3. **隔离来源。** 训练 prompt 的来源要与评测集隔离，见 `dt-rlvr-data`；再对训练 prompt 和评测做 n-gram、embedding 重叠检查，命中就隔离，见 `dt-contamination`、`dt-contam-hold`。
4. **守住内容质量。** 加粗、字数、禁用词和标题层数可以用脚本检查，但回答是否礼貌、有帮助，仍需要人评或奖励模型（RM），见 `dt-judge-bias`。格式满分而内容无用，是常见的假提升，所以格式训练要保留内容锚点评测，摘要人评不能下降，见 `dt-neg-transfer`。

## 实践中的变化

摘要和改写任务常有「短、按条目写、不用标题党」这类约束，很适合生成规则奖励。约束叠在许可 SFT 数据或验证过的合成数据上。

541 条英文题仍留作评测。多语场景下检查器要按语言重写，英文的词数统计不能直接套到中文上，见 `dt-locale-data`。

---
id: dt-ifeval-overlay
section: labs
order: 39
level: A
title: IFEval 只有 541 条，后训练能不能直接拿来训？
quick: "IFEval 的 541 条英文评测题不能进入训练。可从自己的 SFT 数据抽任务，再叠加同类可执行约束，生成独立 RLVR 训练集。检查约束能否同时满足，按语言改写检查器，并同时评估内容质量，避免只学格式。"
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

保留 IFEval 作为评测，不把它的题直接用于训练。可以从自己的监督微调（SFT）数据抽样，随机加入同类约束，把约束参数保存为 `ground_truth` JSON，用于规则奖励。训练 prompt 的来源与评测集必须隔离，见 `dt-rlvr-data`。

加粗、字数、禁用词和标题层数，可以用脚本检查。真正礼貌、有帮助与否，仍需要人评或奖励模型（RM），见 `dt-judge-bias`。格式满分而内容无用，是常见的假提升。

生成约束时先检查能否同时满足。例如「少于 50 词」与「列 12 条」可能冲突，无法满足的组合丢弃。格式训练还要保留内容锚点评测，摘要人评不能下降，见 `dt-neg-transfer`。

对训练 prompt 与评测做 n-gram、embedding 重叠检查，命中就隔离，见 `dt-contamination`、`dt-contam-hold`。能从 Hugging Face 加载，并不代表评测数据可直接训练。

## 对应产品用途

通知和邮件改写常有「短、按条目写、不用标题党」等约束，适合生成规则奖励。约束应叠在许可 SFT 数据或验证合成上，不默认使用用户日志。

541 条英文评测题仍留作评测。多语检查器需按语言重写，英文词数统计不能直接套中文，见 `dt-locale-data`。

Google IFEval 公开包含约 500 多题、25 类可脚本检查的指令，一条 prompt 可以包含多条约束。Tulu 3 的 RLVR-IFeval 从 Tulu 2 SFT 数据抽样，并随机加入同类约束，体现的是另造训练集。

## 追问

- 约束冲突怎么办？生成阶段检查可满足性，不能满足就丢弃。
- 只训格式会伤内容吗？可能，用内容锚点一起检查，见 `dt-neg-transfer`。
- 如何防泄漏？训练与评测来源隔离，再做 n-gram 和 embedding 检查。

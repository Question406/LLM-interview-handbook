---
id: dt-ifeval-overlay
section: labs
order: 39
level: A
title: IFEval 只有 541 条，post-training 能不能直接拿来训？
quick: >-
  不能。IFEval 的 541 条英文题是 evaluation set，拿来训就失去评测意义。要借它的思路另造 training set：从自己的 SFT
  数据抽任务、叠同类的可执行约束，生成独立的 RLVR 数据；同时检查约束能否同时满足，按语言改写 checker，并单独评内容质量，免得只学会格式。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Instruction-Following Evaluation for Large Language Models
    url: 'https://arxiv.org/abs/2311.07911'
    type: primary
  - title: 'Tulu 3: Pushing Frontiers in Open Language Model Post-Training'
    url: 'https://arxiv.org/abs/2411.15124'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能直接训。IFEval 要留着当评测，它的题一旦进了训练，分数就只说明模型背过题。能从 Hugging Face 加载，不代表评测数据可以拿来训。要借的是它的思路：可执行的约束，另造一份 training set。

Google 的 IFEval 公开包含约 500 多题、25 类能用脚本检查的指令，一条 prompt 可以带好几条约束，比如「全文小写、不许用逗号、结尾加一句 P.S.」。这些都能用一段脚本判对错，这正是它能变成训练数据的原因。

Tulu 3 的 RLVR-IFeval 就是另造 training set 的例子：从 Tulu 2 的 SFT 数据 sampling，再随机加入同类约束。我也照这个思路，从自己的 SFT 数据里抽任务，随机加同类约束，把约束参数存成 `ground_truth` JSON，当 rule-based reward 用。训练 prompt 的来源要和 evaluation set 隔离，见 `dt-rlvr-data`；再对训练 prompt 和评测做 n-gram、embedding 重叠检查，命中就隔离，见 `dt-contamination`、`dt-contam-hold`。

还要守住内容质量。加粗、字数、禁用词、标题层数都能用脚本查，回答礼不礼貌、有没有帮助，还得靠 human evaluation 或 reward model（RM），见 `dt-judge-bias`。格式满分、内容没用，是很常见的假提升，所以格式训练要留着内容 regression evaluation，摘要 human evaluation 不能掉，见 `dt-neg-transfer`。

## 追问

**约束叠多了互相冲突怎么办？**
生成时先查能不能同时满足，比如「少于 50 词」和「列 12 条」可能冲突，满足不了的组合直接丢掉。

**541 条原题还用吗？**
用，继续留作评测。

**multilingual 场景下 checker 能直接用吗？**
不能，要按语言重写。英文的词数统计没法直接套到中文上，见 `dt-locale-data`。

**哪些任务最适合做这种 rule-based reward？**
摘要和改写，它们常有「短、按条目写、不用标题党」这类约束。约束叠在许可 SFT 数据或验证过的 synthetic data 上。

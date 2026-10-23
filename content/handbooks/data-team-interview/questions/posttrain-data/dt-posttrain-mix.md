---
id: dt-posttrain-mix
section: posttrain-data
order: 16
level: S
title: 数学、代码、工具、聊天后训练配在一起，怎么避免互相打掉？
quick: "四类数据分别设 token 配额和 loss 范围再混，可验证任务用规则奖励，主观偏好用人评或 RM，奖励尺度不同的任务不放进同一个 GRPO 分组，工具返回不计入损失。每加一类数据都回看其余能力，防止代码伤拒答、工具 JSON 伤自然语言。"
companies:
  - apple
tags:
  - Apple
  - Post-training
  - Data Mix
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Tulu 3: Pushing Frontiers in Open Language Model Post-Training"
    url: https://arxiv.org/abs/2411.15124
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

四类数据分别采样、各自设 token 配额和 loss 范围，再混在一起训。可验证任务用规则奖励，主观偏好用人评或奖励模型（RM）。每加一类数据，都要回头看其余能力有没有掉。

互相打掉的情况很常见。比如加了一大批工具 JSON 之后，用户随口问一句天气，模型也回一段 JSON。能力之间有负迁移，过量的代码 SFT 可能损害拒答能力，过量的工具 JSON 可能损害自然语言表达。奖励也不在一个尺度上，数学是 0/1，工具是环境状态奖励，不加区分地放进同一个 GRPO 分组，组内比较就失去意义。公开配方都是分开处理的：Tulu 3 把 SFT 混合和基于可验证奖励的强化学习（RLVR）分阶段写清楚了，Llama 3 的后训练也是多种能力分开采样再混合。

## 按什么顺序配

先定配比。token 预算按能力缺口分，和某类数据好不好合成无关。工具轨迹条数少但 token 长，所以按 token 计，不按条数。聊天的短模板容易被长轨迹挤掉，见 `dt-length-bucket-code`。

再分阶段。先用 SFT 冷启动各种格式，包括工具的字段和类型规范（schema）、boxed、代码围栏；再用 RLVR 提数学和代码；最后用偏好数据处理主观质量和安全。R1 的小模型只做 SFT 蒸馏，原因是强化学习（RL）在小模型上不稳，小模型更可能走这条路，见 `dt-r1-distill`。

训的时候管好 mask。同一条 packed 序列里，工具返回、用户话、测试输出全部 mask 掉，见 `dt-packed-sft-code`；数学的思维链（CoT，即分步推理过程）进交叉熵损失（CE），TIR 的 stdout 不进。

最后盯住负迁移。每加一类数据都要看对应的锚点：加了数学，看工具第二跳和拒答；加了 SWE，看短函数补全和多语言。`dt-neg-transfer` 里用来保留旧能力的数据，要一直留在配比里，等能力掉了再补就晚了。

## 追问

**能用一个 GRPO 同时训数学和工具吗？**
不这么做，奖励尺度不同，要分组或分阶段。Tulu 的 RLVR 也是按可验证任务族分开做的。

**安全数据放一个桶就够了吗？**
不够，要分桶。工具 write 前的确认和拒答是两个桶，见 `dt-tool-write-confirm`、`dt-safety-refuse`，两个桶各自准备示范。

**聊天数据还要不要？**
要，它是锚点，防止模型什么都输出 JSON。LIMA 那类精标数据就够用，见 `dt-lima-vs-scale`。

**结果怎么报？**
报四行 $\Delta$：数学、代码、工具 $\mathrm{pass}^{k}$、聊天 / 安全，再加一行污染率，见 `dt-cost-per-gain`。

相关：`dt-length-bucket-code`、`dt-r1-distill`、`dt-packed-sft-code`、`dt-neg-transfer`

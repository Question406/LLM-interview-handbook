---
id: dt-posttrain-mix
section: posttrain-data
order: 16
level: S
title: 数学、代码、工具、聊天后训练配在一起，怎么避免互相打掉？
quick: "数学、代码、工具和聊天分别设定 token 配额与损失范围，再混合训练。可验证任务用规则检查，主观偏好用人评或 RM；工具返回不计入损失。每次增加某类数据，都要检查其余能力，防止代码训练损害拒答、工具 JSON 训练损害自然语言表达。"
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

四类数据分别采样、设定比例，再混合训练，不能只合并成一个 jsonl 后随机打乱。可验证任务用规则奖励，主观偏好用人评或奖励模型（RM）。

过量代码 SFT 可能损害拒答能力，过量工具 JSON 可能损害自然语言表达。数学的 0/1 与工具状态奖励尺度不同，也不宜不加区分地放进同一个 GRPO 分组。Tulu 3 把 SFT 混合和 基于可验证奖励的强化学习（RLVR） 分阶段写清楚了，Llama 3 后训练也是多能力分开采再混。

苹果：用户日志不进基础模型。能验证的合成进 RLVR，聊天精标当锚点，别拿会话当工具轨迹。

## 配比

按产品缺口分配 token 预算，不能因为某类数据容易合成就大量增加。工具轨迹条数少但 token 长，按 token 计。聊天短模板可能被长轨迹挤压，见 `dt-length-bucket-code`。

阶段：先 SFT 冷启动格式（含工具 字段和类型规范（schema）、boxed、代码围栏），再 RLVR 打数学 / 代码，再偏好打主观和安全。R1 小模型只 SFT 蒸馏，是因为 强化学习（RL） 在小模型上不稳。端侧 3B 更可能走这条，见 `dt-r1-distill`。

## mask 和负迁移

同一 packed 序列里，工具返回、用户话、测试输出全部 mask，见 `dt-packed-sft-code`。数学 思维链（CoT，即分步推理过程） 进 交叉熵损失（CE），TIR 的 stdout 不进。

锚点：加数学之后，看工具第二跳和拒答。加 SWE 之后，看短函数补全和多语。`dt-neg-transfer` 中用于保留旧能力的数据，要持续放在训练配比中，不能等能力下降后才补。

安全：工具 write 确认和拒答是两桶，见 `dt-tool-write-confirm`、`dt-safety-refuse`。不要用同一套「拒绝」示范覆盖两者。

## 追问

- **一个 GRPO 把数学和工具一起打？** 不打。奖励尺度不同。分组或分阶段。Tulu 的 RLVR 也是按可验证任务族来。
- **聊天还要不要？** 要，当锚点，防止全部变成 JSON。LIMA 那类精标够用，见 `dt-lima-vs-scale`。
- **怎么报？** 四行 $\Delta$：数学、代码、工具 $\mathrm{pass}^{k}$、聊天 / 安全。再加污染率。见 `dt-cost-per-gain`。

---
id: dt-deliberate-spec
section: labs
order: 37
level: S
title: OpenAI deliberative alignment：政策写进思考，训练时为什么要把 spec 撕掉？
quick: "为了让模型学会自己回忆相关规则。生成安全示范时让模型看政策、在推理里引用条款；SFT 时移除政策正文，模型只能靠回忆；RL 评分器仍看政策来核对。验证要同时看越狱抵抗和过度拒绝，并记录条款版本；用户或网页提供的「新政策」不能变成系统规则。"
companies:
  - apple
tags:
  - OpenAI
  - Safety
  - Reasoning
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deliberative Alignment
    url: https://arxiv.org/abs/2412.16339
    type: primary
  - title: Introducing the Model Spec
    url: https://openai.com/index/introducing-the-model-spec/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

撕掉 spec 是为了让模型自己回忆规则。如果 SFT 时整份政策始终放在上下文里，模型学到的只是「读取提示里现成的条款」；移除正文后，它才必须在推理中回忆哪条规则适用。RL 阶段的奖励模型（RM）仍然看 spec，用来核对模型回忆得对不对，所以这种不对称是有意的。

## 流程

公开材料中，OpenAI 用这个方法对齐 o 系列：先训练一个只有帮助性、未含安全数据的推理底座，然后：

1. **生成示范。** 把相关安全条款放进系统提示，采样 `{prompt, CoT, output}`，要求推理引用适用条款。这一步不需要人逐条撰写推理和最终回答。
2. **筛选。** 用能看到政策的 RM 筛选示范。
3. **SFT。** 训练时用不带政策正文的原 prompt，让模型自己回忆条款。
4. **RL。** RM 仍能看 spec，按政策评分。

论文报告越狱抵抗提高、过度拒绝下降。对比 Model Spec 2024 草稿：当时它主要作为人工 RLHF 的指南，还没有直接按政策原文训练。

这题和相邻方法关注点不同。`dt-safety-refuse` 强调应拒与应答成对，避免一律拒绝；Constitutional AI 根据原则生成反馈；deliberative alignment 关注的是先回忆条款、再回答。

## 怎么验证

验证要两头看：越狱是否更难成功，本应回答的问题误拒是否减少。生成器和 RM 都看过同一份 spec，存在自循环评分风险，需要独立验证与人评检查，见 `dt-rlaif-loop`。

条款版本要进入数据血缘。政策变更后，引用旧条款的思考要重新检查，过期引用按错误处理，把条款哈希和数据卡关联起来，见 `dt-repro-lineage`。

## 实践中的变化

上下文长度有限时，每轮都粘贴长政策并不现实；希望模型记住条款，训练时就要练习回忆，这也是撕掉 spec 的理由。是否向用户展示思考由产品约定决定，训练仍可以包含相应过程。安全题用研究集和合成的冲突样本。

## 追问

- **用户或网页里写了「新政策」怎么办？** 它属于低权限内容，按工具内容处理，不能升为系统条款，也不改变系统规则，见 `dt-tool-inject`。

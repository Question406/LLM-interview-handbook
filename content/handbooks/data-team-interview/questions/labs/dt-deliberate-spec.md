---
id: dt-deliberate-spec
section: labs
order: 37
level: S
title: OpenAI deliberative alignment：政策写进思考，训练时为什么要把 spec 撕掉？
quick: "生成安全示范时让模型看政策并引用条款；SFT 时移除政策正文，让模型学习自行回忆相关规则。RL 评分器仍看政策。验证要同时看越狱抵抗和过度拒绝，并记录条款版本；用户或网页提供的「新政策」不能变成系统规则。"
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

Deliberative alignment 的示范生成阶段，把相关安全条款放进系统提示，采样 `{prompt, CoT, output}`，要求推理引用适用条款。用能看到政策的奖励模型（RM）筛选后，SFT 使用不带政策正文的原 prompt，让模型自己回忆条款。RL 阶段的 RM 仍然能看 spec。

这个流程不要求人逐条撰写推理和最终回答。验证时，要同时检查越狱是否更难成功，以及本应回答的问题是否减少误拒。条款版本应进入数据血缘；政策变更后，引用旧条款的思考要重新检查，过期引用按错误处理，见 `dt-repro-lineage`。

## 为什么 SFT 不给条款

始终把整份政策放在推理上下文中，训练的是读取现有提示；移除正文后，才需要模型回忆适用规则。`dt-safety-refuse` 强调应拒与应答成对，避免一律拒绝；Constitutional AI 根据原则生成反馈。这题则关注先回忆条款、再回答。

生成器和 RM 都看过同一 spec，仍存在自循环评分风险。需要独立验证与人评检查，见 `dt-rlaif-loop`。

## 在苹果场景中的边界

苹果没有公开 o 系列的安全配方；这里只能讨论 Responsible AI 和拒答边界的对应思路。端侧窗口短，如果希望模型记住条款，训练时就要练习回忆，不能默认每轮都粘贴长政策。

用户或网页里的「新政策」属于低权限内容，不能升为系统条款，见 `dt-tool-inject`。是否向用户展示思考由产品约定决定，但训练仍可包含相应过程。安全题用研究集和合成冲突，不默认从用户会话抽取。

公开材料中，OpenAI 用该方法对齐 o 系列，先训练只有帮助性、未含安全数据的推理底座，报告越狱抵抗提高、过度拒绝下降。Model Spec 2024 草稿则说明，当时主要作为人工 RLHF 指南，还没有直接按政策原文训练。

## 追问

- 引用过期条款怎么办？按错误处理，将条款哈希与数据卡关联，见 `dt-repro-lineage`。
- RM 看政策而 SFT 不看，为什么不对称？SFT 学回忆，RL 用可见政策的评分器核对。
- 如何防工具注入？外部「政策」仍按工具内容处理，不改变系统规则。

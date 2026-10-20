---
id: pt-hybrid-thinking
section: posttrain
order: 237
level: A
title: Qwen3 一类 hybrid thinking（think / no-think）怎么训、怎么切，和固定长 CoT 差在哪？
quick: "我会说同一套权重、两套模板：`/think` 先生成分步推理过程，`/no_think` 直接给答案。训的时候先用长分步推理（CoT）示范冷启动，再做推理强化学习，融合阶段再把 think 的终答蒸馏进 no-think。这是模式开关，别跟推理时预算控制器、训练里罚长度混在一起。"
tags:
  - Qwen3
  - Thinking
  - Distillation
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Qwen3 Technical Report
    url: https://arxiv.org/abs/2505.09388
    type: primary
---

本题管模式开关，再把 think 能力蒸馏进 no-think。`pt-adaptive-thinking-budget` 是推理时还要不要续写、何时停；`pt-reasoning-token-cost-frontier` 是训练目标里惩罚无效推理 token。三张卡不要并成「让模型少想一点」。常见误区是：直接答成固定长 CoT，或者训练只喂很长的推理过程、线上却把思考关掉。

## 怎么切：同一权重，两套模板

Qwen3 不是两套模型。Chat 模板里用 `/think` 与 `/no_think`（实现上也常是 `enable_thinking`）把用户请求打进不同条件。思考模式先写过程再给答案；非思考模式跳过过程段，直接答。开关是条件前缀，不是另起一个 LoRA。

切的瞬间分布必须是训练见过的。只在 think 模板上做 SFT / RL，推理关标签，就会让模型面对训练中未见过的条件：模型仍按很长的推理过程预算生成，或突然丢掉过程后格式崩掉。评测、线上、训练必须同一开关、同一停止符、同一截断。业务路由可以按题型选模式，但路由规则要写进评测，不能线下乱切刷分。

和运行时预算控制器的差别：hybrid 先选想或不想；控制器是在已经想的那条链上再决定想多久。可以叠：简单题走 no-think，难题走 think 再加长度封顶。别把 `/no_think` 说成「自适应停」。

## 怎么训：冷启动、推理 RL、再融合蒸馏

Qwen3 后训练是分阶段的，融合才是 hybrid 的关键，不是一上来混着训。

1. **长 CoT 冷启动。** 用带过程的示范做 SFT，把「先算再答」写进分布，模型先具备可强化学习的推理格式。
2. **推理 RL。** 在数学 / 代码 / 逻辑上用结果奖励（如 GRPO）提高长推理过程的质量。这一段仍主要在 think 模式里发生。
3. **思考模式融合。** 混入 think 与 no-think 两类监督：think 侧保留过程；no-think 侧用同一题的终答（常从 think 模型的答案蒸馏出来，去掉中间 token）当目标。模型学会：看见 no-think 条件就直接给出最终答案，不再生成无意义的过程段。
4. **通用 RL。** 再补帮助性、安全、格式，避免融合把指令跟随冲掉。

蒸馏对象是答案，不是把很长的推理过程压缩成固定 $L$ 个 token。学生在 no-think 条件下拟合教师的最终答案，过程留在教师 / think 模式里。这和 long-to-short「同一模式压短」不同：hybrid 允许推理时完全不生成过程。

SFT 开或关 Thinking 对分布的影响见 `meituan-thinking-on-sft`。那题问的是「开着微调会写进什么」；本题问「如何让同一权重两种模式都可用」。

## 和固定长 CoT 差在哪

固定长 CoT（或「永远先想固定步数」）每道题都付一段过程预算，简单题浪费、难题可能还不够，且没有经过训练的关闭方式。Hybrid 把「要不要过程」做成可切换的条件分布：延迟敏感、抽取、闲聊走 no-think；多步推理走 think。

验收不要只报 think 模式的 raw acc。必须同时报：no-think 的正确率与延迟、开关切换后格式合法率、以及「同一题 think 对、no-think 错」的比例。后一项度量蒸馏有没有把终答迁过去。只开 think 刷分，hybrid 没有训成。

长度惩罚让同一模式少写无效 token；hybrid 允许另一种模式零过程。两者可一起用：think 模式里仍可对无效步骤加代价，见 `pt-reasoning-token-cost-frontier`。缺融合阶段，关闭思考可能损失能力，因为模型尚未学会另一种模式。

## 追问

- **为什么不训两个模型？** 可以，维护两倍权重和路由。Hybrid 用条件前缀共享表示，think 学到的终答能迁到 no-think。代价是融合数据配比：no-think 太少切不干净，太多推理回退。
- **融合会不会把推理训废？** 会，如果 no-think 数据掺进难题且不带过程、又权重大。应按难度分组统计：难题保留 think，简单题才蒸馏直答。
- **和自适应预算谁先做？** 先有可切换的两套模式，再在 think 模式上加何时停。不会切模式，控制器只能在一条永远很长的链上拧。
- **标签漏了会怎样？** 训推不一致。训练带 `/think`、线上不带，分数掉得比能力掉得更狠。先对齐模板再谈效果。
- **no-think 的答案从哪来？** 优先用 think 模型在同一题上的终答做蒸馏，而不是另写一套短答案，避免两种模式结论打架。

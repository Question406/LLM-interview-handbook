---
id: dt-guided-gen-data
section: senior
order: 10
level: A
title: Director：guided generation / 约束解码要什么样的后训练数据？
quick: "训练样本要包含用户请求、框架实际注入的结构定义，以及符合定义且字段内容正确的输出。约束解码能保证格式合法，训练数据还要教模型填对内容。只给几条“请输出 JSON”的示范，和真实框架输入并不一致。"
companies:
  - apple
tags:
  - Apple
  - Guided Generation
  - Tool Use
  - Post-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

训练样本要和框架实际给模型的输入一致：用户请求、框架注入的结构定义，以及一个既符合定义、字段内容也正确的输出。约束解码只能保证格式合法，内容填对要靠训练数据来教。

## 为什么有约束解码还要训练数据

约束解码限制模型只能生成符合规则的结构，例如合法的 JSON 或指定的 Swift 类型。但「结构合法」和「字段内容正确」是两件事：程序能解析这个对象，不代表里面的工具名、日期或参数填对了。

工具调用也建立在这类规范上。训练要让模型选对工具名、填对参数；一个看起来像 JSON 的对象，参数照样可能是错的。

## 示例要和框架实际输入一致

Apple Foundation Models 框架允许开发者用 `@Generable` 声明 Swift 结构。框架把结构转成标准响应格式放进输入提示，模型通过相关后训练学会遵守它，系统再用约束解码保证格式合法。

所以正例要同时包含用户请求、框架注入的字段和类型规范，以及可解析的正确输出。只有一句「请输出 JSON」的自然语言示范，覆盖不了框架实际的输入形式。

## 数据分哪几类

正确示范教模型根据请求填写结构。错误样本覆盖缺字段、多字段和类型错误，并给出正确的修复结果或应当拒绝的结果。工具轨迹还要包含串行和并行调用，质量检查见 `dt-traj-quality`。

端侧模型的上下文较短，示范输出应尽量贴近简短的结构任务，避免长篇散文主导训练。

这种跨应用通用的格式能力适合放在基础模型后训练里。某个应用特有的业务枚举，可以考虑适配器，见 `dt-adapter-vs-base`。

## 怎么评测

解析成功率和字段正确率分开看。BLEU 不能告诉你工具参数有没有填对。

## 追问

- **结构定义每周都变怎么办？** 基础模型学习稳定的通用规范，频繁变化的业务字段放在适配器或开发者侧。
- **和 Function Calling 的 SFT 有什么关系？** 两者都在教结构化输出。这里的规格由宏生成、由系统注入，和 Chat Completions 的模板未必一致，训练数据要按框架实际的形式来造。

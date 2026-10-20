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

约束解码限制模型只能生成符合规则的结构，例如合法的 JSON 或指定 Swift 类型。但“结构合法”和“字段内容正确”是两件事：程序能解析这个对象，并不意味着里面的工具名、日期或参数填对了。

后训练数据需要教模型理解真实的结构定义，并按用户任务填写正确内容。

## 示例要和框架实际输入一致

Apple Foundation Models 框架允许开发者用 `@Generable` 声明 Swift 结构。框架把结构转成标准响应格式并放进输入提示，模型通过相关后训练学习遵守它，系统再用约束解码保证格式合法。

所以正例应该同时包含用户请求、框架注入的字段和类型规范，以及可解析的正确输出。只有一句“请输出 JSON”的自然语言示范，不能完整覆盖实际框架的输入形式。

工具调用也建立在这类规范上。训练还要让模型选对工具名、填写正确参数，而不仅是生成一个看起来像 JSON 的对象。

## 数据可以分成哪些类型

正确示范教模型根据请求填写结构。错误样本覆盖缺字段、多字段和类型错误，并给出正确修复或应当拒绝的结果。工具轨迹还需要包含串行和并行调用，质量检查见 `dt-traj-quality`。

这种跨应用通用的格式能力适合基础模型后训练。某个应用特有的业务枚举，可以考虑适配器，见 `dt-adapter-vs-base`。

评测应分别看解析成功率和字段正确率。BLEU 不能告诉你工具参数是否填对。端侧还要考虑 rapid / balanced 分辨率设置与较短的上下文，示范输出应尽量贴近简短的结构任务，避免让长篇散文主导训练。

## 面试追问

- **有约束解码，还需要训练数据吗？** 需要。约束解码负责格式，数据负责让模型理解任务并填对字段。
- **结构定义每周都变怎么办？** 基础模型学习稳定的通用规范，频繁变化的业务字段可以放在适配器或开发者侧。
- **和 Function Calling 的 SFT 有何关系？** 都在教结构化输出。这里还要匹配宏生成、系统注入的规格形式，不能直接假设它和 Chat Completions 的模板一致。

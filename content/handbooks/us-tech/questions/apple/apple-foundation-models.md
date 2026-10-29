---
id: apple-foundation-models
section: apple
order: 11
level: S
title: Apple：Foundation Models 公开叙事怎么讲，on-device 和云各自干什么、capability limits 在哪？
quick: >-
  Apple 的公开方案是 on-device 与 PCC 上的 server 模型互补：约 3B 的 on-device
  模型处理日常、低延迟和私有上下文任务，更难的推理交给 server-side。on-device
  擅长摘要、抽取和短对话，设计时要按能力与隐私要求决定路由，并保留拒答或非生成 UI。
tags:
  - Apple
  - Foundation Models
  - On-device
  - Private Cloud Compute
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 可以这样回答

Apple 的 Foundation Models 可以按两套互补模型来讲：约 3B 的 on-device 模型处理日常、低延迟和私有上下文任务，PCC 上更大的 server 模型处理更难的推理。比如邮件摘要可以留在本地，超出本地能力时再考虑把这一轮需要的最小上下文送到 server-side。

2024 报告给出这套 on-device / server 分工；2025 更新进一步使用 on-device 2-bit QAT、KV 共享，以及 server 的 Parallel-Track MoE。公开定位也明确了 on-device capability limits：它擅长摘要、抽取和短对话，开放世界知识聊天并非目标。面试时要把这些产品任务与 constraints 说清。

## 技术备查

Apple 的 Foundation Models 可以按两套互补模型来讲：约 3B 的 on-device 模型处理日常、低延迟和私有上下文任务，PCC 上更大的 server 模型处理更难的推理。比如邮件摘要可以留在本地，超出本地能力时再考虑把这一轮需要的最小上下文送到 server-side。

2024 报告给出这套 on-device / server 分工；2025 更新进一步使用 on-device 2-bit QAT、KV 共享，以及 server 的 Parallel-Track MoE。公开定位也明确了 on-device capability limits：它擅长摘要、抽取和短对话，开放世界知识聊天并非目标。面试时要把这些产品任务与 constraints 说清。

## 两套模型分别承担什么

两套模型的权重和约束分别是：

- on-device。约 3B，GQA、共享 embedding、vocabulary 公开约 49k。目标是常驻、低功耗、可离线。公开数字：iPhone 15 Pro 上大约 0.6 ms 每个 prompt token、约 30 token/s（speculative decoding 之前）。适合摘要、改写、抽取、短对话、通知、邮件、屏幕上的字。私有上下文默认不出设备，见 `apple-personalize`。
- Server / PCC。更大、更新架构（2025 公开 PT-MoE、交错局部/全局 attention）。跑在 Apple silicon 的 Private Cloud Compute 上：请求用完丢、不拿用户数据训基础模型。适合更长推理、更重工具、on-device 3B 明显不够的任务。压缩配方不同（公开有 ASTC、约 3.56 bpw），不要和 on-device 2-bit 混报，见 `apple-ondevice-quant`。

路由不是「有网就上云」。默认：隐私敏感且短的留本地；本地质量不够，再送这一轮需要的最小 evaluation slices 到 PCC，而不是同步整个邮箱。PCC 解决的是「苹果侧不持久化明文」，不是 differential privacy，见 `apple-diff-privacy`。

开发者面对的是 Foundation Models 框架：guided generation、工具、rank 32 的 adapter。框架把 on-device 模型暴露成系统能力，不是让第三方把 3B 当 GPT-4o 用。

## 按 capability limits 设计路由与评测

2025 更新写得很直：on-device 擅长 summarization、entity extraction、短对话、创意短文本；不是 chatbot for general world knowledge。现场我会把「不会做什么」说成设计：

- 会：用户眼前的邮件 / 通知 / 屏幕；格式稳定的任务（靠功能 adapter，见 `apple-rank-adapter`）；tool calls（日历、本地检索）。证据约束同 `apple-siri-grounded`。
- 不会默认做：开放世界长知识问答、把私人 corpus 拿去训基础模型、把全量上下文上传做云端 retrieval-augmented generation (RAG)（RAG）。后者是 `amazon-bedrock-rag` 那条路，这里默认不成立。
- multimodal。on-device 视觉编码器更小（公开 ViTDet 量级），server 更大。屏幕理解见 `apple-multimodal`，不要把 Image Playground 的扩散模型和 AFM 文本模型说成同一个 checkpoint。

evaluation 也要按任务类型与 capability limits 报告。human evaluation、locale、feature adapter（邮件摘要 vs 通知）比把 3B 丢进开放 chatbot 竞技场更贴近产品。只报 BLEU / MMLU 会被追「那通知摘要为什么还要单独 adapter」，见 `apple-afm-eval`。

on-device 和 server-side 在权重、数据、压缩、评测和产品任务上都有区别。on-device agent 也要围绕专用工具和热插拔 adapter 设计，能力范围要与公开定位一致。



先问用户数据能不能离开设备、任务是格式还是事实、延迟是语音还是静默文本。再给三条路径：本地 3B + 检索 / adapter；PCC + 最小 evaluation slices；拒答或走非生成 UI。quantization、KV、sampling 是实现细节，分别见 `apple-ondevice-quant`、`apple-ondevice-kv`、`apple-topk-sample`。语音通路还要拆首包，见 `apple-siri-latency`。

训练数据公开说明：许可数据、Applebot 爬取（可 opt out）、synthetic data；不用用户私有数据和交互训基础模型。改进全球模型走这条；改进「我的摘要口吻」走 on-device adapter 或 few-shot 证据，不要把邮箱当 SFT。

## 追问

**为什么不把 70B quantization 后塞进手机？**
权能压，KV、激活、功耗、热、ANE 静态图不一定压得动。公开选择是 3B 加压缩加 adapter，难的上 PCC。
**PCC 和「on-device 隐私」矛盾吗？**
不矛盾，如果 evaluation slices 最小、不落盘、不拿去训。矛盾的是「为了方便把整个用户画像同步上去」。
**开发者 fine-tuning 会不会把私有数据送回苹果？**
公开 toolkit 是在开发者侧训 adapter，且要跟基础模型版本绑定。产品路径仍应假设用户数据默认不出设备。
**和 Siri 的关系？**
AFM 是生成 base model；Siri 还有 ASR、工具、TTS、有实际证据支持。不要把「Foundation Model 很快」说成整条语音 SLO，见 `apple-siri-latency`。

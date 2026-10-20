---
id: apple-foundation-models
section: apple
order: 11
level: S
title: Apple：Foundation Models 公开叙事怎么讲，端侧和云各自干什么、能力边界在哪？
quick: >-
  公开故事是两套互补模型，不是一个万能聊天机器人。约 3B 端侧跑日常、低延迟、私有上下文；更难的推理走 Private Cloud
  Compute 上的 server 模型。端侧明确不是开放世界 chatbot。路由看任务难度和隐私切片，不看「一律上云」。
tags:
  - Apple
  - Foundation Models
  - On-device
  - Private Cloud Compute
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Apple Intelligence 岗和 Foundation Models 框架岗会问「你们到底训了个什么」。2024 报告给出端侧约 3B 加 PCC 上的更大 server 模型；2025 更新把端侧压到 2-bit QAT、KV 共享，server 改成 Parallel-Track MoE，并写明：端侧模型不是为开放世界闲聊设计的。面试要能复述这条产品契约，而不是背 MMLU 超过谁。

## 端侧和 PCC 不是同一模型的两个部署点

我会先画两套权重、两套约束：

- 端侧。约 3B，GQA、共享 embedding、词表公开约 49k。目标是常驻、低功耗、可离线。公开数字：iPhone 15 Pro 上大约 0.6 ms 每个 prompt token、约 30 token/s（投机解码之前）。适合摘要、改写、抽取、短对话、通知、邮件、屏幕上的字。私有上下文默认不出设备，见 `apple-personalize`。
- Server / PCC。更大、更新架构（2025 公开 PT-MoE、交错局部/全局注意力）。跑在 Apple silicon 的 Private Cloud Compute 上：请求用完丢、不拿用户数据训基础模型。适合更长推理、更重工具、端侧 3B 明显不够的任务。压缩配方不同（公开有 ASTC、约 3.56 bpw），不要和端侧 2-bit 混报，见 `apple-ondevice-quant`。

路由不是「有网就上云」。默认：隐私敏感且短的留本地；本地质量不够，再送这一轮需要的最小切片到 PCC，而不是同步整个邮箱。PCC 解决的是「苹果侧不持久化明文」，不是差分隐私，见 `apple-diff-privacy`。

开发者面对的是 Foundation Models 框架：guided generation、工具、rank 32 的 adapter。框架把端侧模型暴露成系统能力，不是让第三方把 3B 当 GPT-4o 用。

## 能力边界要主动说

2025 更新写得很直：端侧擅长 summarization、entity extraction、短对话、创意短文本；不是 chatbot for general world knowledge。现场我会把「不会做什么」说成设计：

- 会：用户眼前的邮件 / 通知 / 屏幕；格式稳定的任务（靠功能 adapter，见 `apple-rank-adapter`）；工具调用（日历、本地检索）。证据约束同 `apple-siri-grounded`。
- 不会默认做：开放世界长知识问答、把私人语料拿去训基础模型、把全量上下文上传做云端 检索增强生成（RAG）。后者是 `amazon-bedrock-rag` 那条路，这里默认不成立。
- 多模态。端侧视觉编码器更小（公开 ViTDet 量级），server 更大。屏幕理解见 `apple-multimodal`，不要把 Image Playground 的扩散模型和 AFM 文本模型说成同一个 checkpoint。

评测也要按边界报。人评、locale、feature adapter（邮件摘要 vs 通知）比把 3B 丢进开放 chatbot 竞技场更贴近产品。只报 BLEU / MMLU 会被追「那通知摘要为什么还要单独 adapter」，见 `apple-afm-eval`。

常见误区是：把 AFM 讲成「苹果的 GPT，小的在手机、大的在云」。权重、数据、压缩、评测、产品任务四套都不一样。另一常见误区是：声称端侧能做任意 agent。公开叙事是专用工具加热插拔 adapter，不是通用自主代理。

## 我会怎么收设计题

先问用户数据能不能离开设备、任务是格式还是事实、延迟是语音还是静默文本。再给三条路径：本地 3B + 检索 / adapter；PCC + 最小切片；拒答或走非生成 UI。量化、KV、采样是实现细节，分别见 `apple-ondevice-quant`、`apple-ondevice-kv`、`apple-topk-sample`。语音通路还要拆首包，见 `apple-siri-latency`。

训练数据公开口径：许可数据、Applebot 爬取（可 opt out）、合成数据；不用用户私有数据和交互训基础模型。改进全球模型走这条；改进「我的摘要口吻」走端上 adapter 或 few-shot 证据，不要把邮箱当 监督微调（SFT）。

## 追问

- **为什么不把 70B 量化后塞进手机？** 权能压，KV、激活、功耗、热、ANE 静态图不一定压得动。公开选择是 3B 加压缩加 adapter，难的上 PCC。
- **PCC 和「端侧隐私」矛盾吗？** 不矛盾，如果切片最小、不落盘、不拿去训。矛盾的是「为了方便把整个用户画像同步上去」。
- **开发者微调会不会把私有数据送回苹果？** 公开 toolkit 是在开发者侧训 adapter，且要跟基础模型版本绑定。产品路径仍应假设用户数据默认不出设备。
- **和 Siri 的关系？** AFM 是生成底座；Siri 还有 ASR、工具、TTS、有实际证据支持。不要把「Foundation Model 很快」说成整条语音 SLO，见 `apple-siri-latency`。

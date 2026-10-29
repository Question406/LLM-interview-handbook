---
id: apple-personalize
section: apple
order: 10
level: S
title: Apple：个性化不能上传全量私有上下文，adapter / 本地检索怎么选？
quick: >-
  会变的事实用本地检索，稳定的任务格式用功能 LoRA：比如日程走工具，邮件摘要和通知摘要切换各自的 adapter。公开 adapter 常为 rank
  16、16-bit、几十 MB，基础模型冻结 quantization；私有上下文默认留在设备，需要人群统计时再考虑 DP，见
  `apple-diff-privacy`。
tags:
  - Apple
  - Personalization
  - LoRA
  - RAG
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
  - title: Apple Intelligence Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 可以这样回答

个性化要拆成两件事：用本地检索取得当前用户的事实，用 adapter 约束摘要格式、语气和任务行为。比如「周二和谁开会」要查日历，「通知最多两句」可以由功能 adapter 学习。

Apple 公开声明不用用户私有数据训练 foundation model，因此不能默认把全量邮箱向 quantization 上传。那更接近 `amazon-bedrock-rag` 的云端 retrieval-augmented generation (RAG)（RAG）路径；这里先按 on-device 隐私约束设计，Exponent 指南也强调 privacy awareness。

## 技术备查

个性化要拆成两件事：用本地检索取得当前用户的事实，用 adapter 约束摘要格式、语气和任务行为。比如「周二和谁开会」要查日历，「通知最多两句」可以由功能 adapter 学习。

Apple 公开声明不用用户私有数据训练 foundation model，因此不能默认把全量邮箱向 quantization 上传。那更接近 `amazon-bedrock-rag` 的云端 retrieval-augmented generation (RAG)（RAG）路径；这里先按 on-device 隐私约束设计，Exponent 指南也强调 privacy awareness。

## Adapter 在 Apple 公开叙述里是什么

on-device 约 3B 基础模型 quantization 后冻结。LoRA 打在 attention 投影和 FFN 上，公开常用 rank 16，adapter 参数 16-bit，一份大约几十 MB，可动态加载、缓存、换掉。先训 accuracy-recovery adapter 把 palettization 掉的分捞回来，产品 adapter 从它初始化，再为邮件摘要、信息摘要、通知摘要各做一份——因为产品对「好摘要」的定义不一样。quantization 底见 `apple-ondevice-quant`。

这是按功能特化，不是按用户特化。同一份邮件 adapter 服务所有人，个性化来自这一刻塞进上下文的本地证据，不是每人一份上传的权重。热插拔的好处：基础模型驻留 ANE，换任务只换几十 MB，符合 `apple-ane` 的静态底图加外置权重。

若真做按用户的 adapter：必须在设备上用本地数据训，权重不离开设备。算力、overfitting、灾难遗忘都是问题；还要处理「用户删了那封邮件，模型还在记」的遗忘。面试把它标成高成本选项，不要当默认。

## 本地检索解决的是会变的事实

日历、邮件、消息、屏幕上的字，明天就过期。把它们写进权重既违反「不拿私有数据训基础模型」，也来不及更新。做法：

1. 设备内索引。邮件 / 消息已经在本地数据库，按时间、人、线程过滤，再上 embedding 检索。$n$ 是单用户规模，暴力或 IVF 足够，见 `apple-kmeans` 的 nearest neighbors。
2. 生成条件是 $(q,E)$，$E$ 来自检索或工具，有实际证据支持和拒答同 `apple-siri-grounded`。屏幕证据则是框或 OCR，见 `apple-multimodal`。
3. 上下文变长时重排，不要把三年邮件 JSON 塞满窗口。on-device KV 再 quantization 也贵。

选择时可以按数据变化速度区分：会变的事实走检索；稳定的格式、文风、功能约束走 adapter。「用项目符号、不要剧透、通知最多两句」是 adapter。「周二和谁开会」是检索。文风若要「像我」，优先从用户近期已发送邮件检索范例 few-shot，而不是上传 corpus fine-tuning 云端模型。范例仍是 $E$ 的一部分，用完可以不落盘。

PCC：本地 3B 加检索不够时，把当前这一轮需要的 evaluation slices 送到 Private Cloud Compute 上的 large model，而不是同步整个邮箱。PCC 不是 DP，见 `apple-diff-privacy`；它只说明苹果侧不拿明文去训。设计里仍要最小 evaluation slices、最短驻留。



今日日程、这封邮件里的数字：本地检索或工具，不要把原文写入 LoRA。

邮件摘要 vs 通知摘要的格式：功能 LoRA，不要为每个用户各训一个大模。

长期「我喜欢短句」：on-device 小 adapter 或偏好比特，不上传；不要全量对话送 SFT。

改进全球基础模型：许可数据加 synthetic data；人群统计走 LDP，不要用户邮件。

on-device 3B 做不了的推理：PCC 加最小上下文，不要默认云端日志。

评测也要拆：有实际证据支持率（事实是否来自 $E$）、任务格式分（adapter 是否在干活）、隐私事故（是否把 $E$ 打到不该去的通道）。满意度无法替代这些隐私和事实检查。延迟上，先检索再生成；adapter 切换摊还到 task boundaries，不要每生成一个 token 就切换一份 adapter。语音通路更要短 $E$，见 `apple-siri-latency`。

## 追问

**检索会不会 leakage 到下一轮 prompt 日志？**
on-device 默认不采。若做 opt-in 质量分析，走 DP 或聚合，不要原文。
**LoRA 和 QLoRA？**
QLoRA 是为了 fine-tuning 时省显存。Apple 的故事是 inference 时一份 quantization 基础模型加多份小 adapter 热切换。初始化来自 recovery，不是随机。
**用户说「记住这个」？**
显式记忆应是用户可删的本地键值，而不是偷偷写入权重。遗忘是产品功能。
**为什么不把 adapter 上传做联邦平均？**
可以研究，但 gradient / 权重仍可能 leakage $E$。没有用户级 DP 就不要把这条画成主路径。Apple 公开 AFM 训练没用这条。

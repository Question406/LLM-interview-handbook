---
id: dt-prep-map
section: overview
order: 1
level: S
title: Apple Foundation Models Data Team：整条 loop 按哪几轮准备？
quick: "按面试轮次准备：HM 30 分钟讲清数据项目；Technical Screen 45 分钟用 CoderPad 写数据管线，并解释规模和质量检查；Panel 包含四轮技术和一轮 See Around Corners。之后可能还有 Director / VP。数据岗重点是数据选择、合成和评测，不能只准备模型架构。"
companies:
  - apple
tags:
  - Apple
  - 备考地图
  - Foundation Models
  - Data Team
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

按面试轮次准备这套数据岗题目。us-tech 的端侧 MLE 题讨论 KV 共享、2-bit QAT 和 Siri 接地；这里则重点回答数据来源、过滤、合成，以及如何把评测缺口变成下一轮训练数据。`realInterview: false`，题面来自 guideline 和 AFM 公开报告，不是某一场逐字稿。

HM 只有 30 分钟，不适合从本科经历一路讲到现在，也不能只介绍项目换了什么模型架构。Panel 要求你讲清从数据到评测再到改进的过程，以及可能失败的环节；只背 Self-Instruct 或 DPO 的名字不够。

## 轮次和对应卡

| 轮次 | 时长 | 他们在听什么 | 本手册 |
| --- | --- | --- | --- |
| Hiring Manager | Webex 30 min | 数据改动是否改善过具体能力；Why Apple；失败和治理 | `dt-data-story`、`dt-why-apple`、`dt-failed-data-bet`、`dt-legal-capability` |
| Technical Screen | Webex 45 min，CoderPad | 能写、能讲规模和质控 | `dt-pipeline-talk` 到 `dt-countmin-code`。先写 pipeline / MinHash / 精确去重 / 质量门，再写污染 13-gram、水库抽样、PII、packing、verifier |
| Panel × 4 技术 | 各 45 min | 飞轮、合成、诊断、偏好，以及配比 / 污染 / 负迁移等追问 | `dt-data-flywheel`、`dt-synth-reasoning`、`dt-synth-tool-mm`、`dt-benchmark-gap`、`dt-reward-pref`，追问从 `dt-data-mix-quota` 看到 `dt-safety-refuse` |
| Panel × 1 Culture | 45 min | 如何提前补足缺口、及时停止无效项目 | `dt-see-around-corners`、`dt-killed-dataset` |
| Director / VP（条件） | 各 30 min | 整个数据生命周期和治理，能用一句话讲清立场 | `dt-pre-mid-post`、`dt-self-improve`、`dt-adapter-vs-base`、`dt-privacy-feedback`、`dt-paper-pitch` |
| 别家题迁过来（labs） | 自学 | Panel / Director 会借 OpenAI / Llama / FineWeb / Anthropic / xAI / Tesla 的题型追问；第二批还有分类器笔试、诚实评测、评测台、Phi、偏好采集 | `dt-labs-map` 起，种子和通道必须换成 AFM 口径 |
| 通识 · 好数据 | 自学 / Panel 口播 | 什么叫好、堆量还是挑好、滤会不会过头、一次干预怎么跑 | `dt-good-data-map` 起 |
| 后训练数据 | Panel / 自学 | 数学 TIR 和 Lean、代码执行门、工具失败恢复、SWE-Gym；Agent RL 环境和 lab 配方 | `dt-posttrain-map` 起，RL 从 `dt-agent-rl-map` |
| Frontier 发版评测 | 自学 / Panel 口播 | 发模型时写进博客的数据集怎么造、测哪项能力、哪家哪次发布报了哪一项 | `dt-frontier-release-map` 起 |

失败的数据下注和隐私冲突要能讲，见 `dt-failed-data-bet`、`dt-legal-capability`。

CoderPad 45 分钟，代码能跑不够。还需要解释为什么保留这条样本、丢弃那条样本。

Panel 四轮技术加一轮 Culture。加数据掉点、污染、教师偏差这些追问，也需要准备具体的诊断方法。

过了才可能有 Director / VP。Guideline 写成 conditional，按会被问立场准备。

## 公开口径先钉死

这三句现场要能复述，不能发明：

1. 基础模型训练数据是许可语料、公开 / 开源集、Applebot 抓的公开页，加上合成数据。用户私有数据和交互默认不进基础模型，除非用户明确选择帮助改进。
2. 预训练之后还有 continued pre-training（数学 / 代码 / 多语 / 视觉 / 长上下文），再做 SFT 和 RLHF。合成数据在后两段都用，能验证的先验证。
3. 端侧约 3B 和 PCC 上的 server 模型是两套权重、两套约束。Data team 的工作横跨这两套，但产品契约仍是：简短且隐私敏感的任务留在本地，困难任务只把需要处理的部分送上云端。

数字只报报告里写过的。抓取「数千亿页」、去重后超 100 亿图文对、合成 caption 超 50 亿对、server 预训练 13.4T token，这些可以点到。没写过的标注员规模、内部队列名，别编。

## 怎么刷

第一周把 HM 两张卡练成 90 秒项目稿加 60 秒 Why Apple，并把 `dt-good-data-def`、`dt-more-vs-better` 能口播。第二周 CoderPad：先闭卷写 pipeline / MinHash / 精确去重 / 质量门，再补污染 13-gram、水库抽样、PII、packing。边写边出声，说不清规模就重写。第三周按 Panel 四题各画一张白板：闭环、合成 DAG、诊断树、奖励表。通识章当口播底子，别只会背论文名。最后为 Culture 和 Director 的题准备自己的具体经历。

别家公开题放在 labs。预训练先刷 OpenAI bootstrap 和 FineWeb 全局去重；后训练刷偏好和 RLVR；代码 / agent 再刷执行合成、公私测、SWE 轨迹、不该调、注入、该不该搜。第二批刷分类器笔试、诚实 vs 流畅、评测台、Prompt vs RAG vs 微调。见 `dt-labs-map`。发版博客里那套评测（哪家、哪个模型、哪份数据集、怎么造）单独刷 `dt-frontier-release-map`。

和 us-tech Apple 章的分工：端侧延迟、量化、PCC 机制去那边；数据配比、合成验证、评测污染、偏好噪声留在这里。

## 追问

- **没有合成数据项目怎么讲 HM？** 用策展、过滤、难例挖掘或评测隔离讲「数据干预」，不要硬编一条合成管线。
- **会不会手撕 attention？** Technical Screen 的公开要求是 Python 加深度学习工具箱，期望写得动 tensor 代码。默认准备的是 pipeline；如果 CoderPad 里出现 gather / mask / packed CE，按 us-tech 的 ML Coding 补，不要在这本里临时默写 MHA。
- **Director 轮一定有吗？** Guideline 写成 conditional。先按「会被问立场」准备，别假设过了 Panel 就结束。

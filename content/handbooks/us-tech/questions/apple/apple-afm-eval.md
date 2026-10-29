---
id: apple-afm-eval
section: apple
order: 14
level: A
title: Apple：on-device LLM 怎么评，延迟、耗电、隐私，为什么不能只报 BLEU？
quick: >-
  我会分别评任务质量、证据支持、安全、系统性能和隐私，再决定 on-device 模型能否上线。BLEU 只看 n-gram
  重叠，既看不出摘要漏限定词，也测不到热降频或邮件是否离开设备，所以只能当辅助回归指标。
tags:
  - Apple
  - Evaluation
  - On-device
  - Privacy
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

on-device LLM 要按产品任务、证据与安全、系统、隐私四层验收，BLEU 只能提供辅助信息。比如邮件摘要抄了一句原文又补出一个错误事实，n-gram 重叠仍可能很高；一种正确改写只是换了词，又可能得低分。BLEU / ROUGE 依赖参考文本，而摘要没有唯一写法，开放知识问答还常常没有参考答案。

AFM 的产品任务是给定证据 $E$ 的条件生成，源里没有的信息应拒绝补写。Apple 公开评测以 human evaluation、feature adapter 和 locale 为主，辅以 IFEval；on-device 模型的定位也不是开放世界 chatbot。Exponent 的 MLE 指南同样提到 on-device limits，系统和隐私都要进入验收。

## 技术备查

on-device LLM 要按产品任务、证据与安全、系统、隐私四层验收，BLEU 只能提供辅助信息。比如邮件摘要抄了一句原文又补出一个错误事实，n-gram 重叠仍可能很高；一种正确改写只是换了词，又可能得低分。BLEU / ROUGE 依赖参考文本，而摘要没有唯一写法，开放知识问答还常常没有参考答案。

AFM 的产品任务是给定证据 $E$ 的条件生成，源里没有的信息应拒绝补写。Apple 公开评测以 human evaluation、feature adapter 和 locale 为主，辅以 IFEval；on-device 模型的定位也不是开放世界 chatbot。Exponent 的 MLE 指南同样提到 on-device limits，系统和隐私都要进入验收。

## 先确认输出是否把任务做好

公开 human evaluation 用 side-by-side 比较分析推理、头脑风暴、分类、抽取、摘要、工具和安全。locale 还要检查当地表达，例如英式 football 与 soccer。邮件、信息、通知分别有 750 条量级的分层 adapter 样本，多维度都好才判为好。任务评分要检查摘要是否删了关键限定词、通知是否两句、是否剧透；基础模型通测和 feature 集分开，换基础模型后 adapter 要重训重评，公开 toolkit 也要求这一点。

再核对每句话能否对齐本地证据或工具结果。引用过期日历要算事故，无证据生成、该拒未拒、有害或敏感输出分别报；安全用对抗 prompt 的 violation rate，与任务分分开。IFEval、内部指令集和工具参数合法率适合做自动回归，human evaluation 仍要负责它们覆盖不到的部分。把这些合成“质量 0.82”，就看不出到底哪里失败。

## 再测设备和数据路径

延迟拆成 prefill ms/prompt-token、decode token/s、TTFT，语音另看首包音频。公开约 0.6 ms/prompt-token 和 30 token/s 是能力上限，产品需要 p95 和热降频后的稳态；speculative decoding 只报验证后的有效 token/s。Talaria / Instruments 能看每层耗时和能量，用来指导 palettization；还要报 Joule/token、峰值内存、ANE 驻留和 KV 变长后的曲线。瞬时 30 token/s、两分钟后就节流，连续对话仍可能不合格。

至少覆盖目标 SoC、低内存档、前台和后台。掉到 GPU/CPU 的层单列：这会影响正确性和电量。compute unit 没全留在 Neural Engine 时，先查计算图。

隐私检查这一轮的 $E$ 是否离设备、离设备字节数、PCC 调用率及 evaluation slices 大小和驻留、日志是否有原文，以及 opt-in 分析是否按聚合或 DP 路径走。训练不用用户私有数据是一项声明，产品路径仍要实测，PCC 的存在本身不能当隐私指标。DP 在学习人群规律、发布统计时才需要花 $\varepsilon$。

上线以后继续看用户改写、重说、“你说错了”、打断和过热关闭特性的比例。线上与离线冲突，先查线上任务表现；把 prompt 调得更像参考译文，未必更符合用户邮件。用开放 chatbot 竞技场评 3B 后直接决定全走 PCC，可能把私有上下文送出去；只测英语 US，也会漏掉其他语言和地区的问题。

## 追问

**完全没有 gold labels 怎么办？**
先检查输出有没有超出 $E$，再用点开或撤销摘要等任务代理指标，抽少量 human evaluation calibration 后放大。BLEU 在这里补不出 gold labels。

**LLM-as-judge 能用吗？**
能用来扫描，但云端评委会让 evaluation set 离开设备。评测管道本身同样有隐私约束，高风险结果仍抽人审。

**MMLU 涨了能发版吗？**
还不能。它解释基础模型能力，通知 adapter、延迟或电量没过也不能发。

**quantization 回归怎么做？**
同一集在 fp16、palettized、8-bit KV 下测 greedy 对齐和任务分。下降时先查 mask、RoPE，再查码本。

相关：`amazon-titan-eval`、`apple-siri-grounded`、`apple-siri-latency`、`apple-spec-edge`、`apple-ane`、`apple-ondevice-quant`、`apple-diff-privacy`、`apple-rank-adapter`、`apple-personalize`、`apple-ondevice-kv`、`apple-foundation-models`

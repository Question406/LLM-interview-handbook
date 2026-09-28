---
id: design-offline-eval
section: design
order: 12
level: S
title: 设计：LLM 离线评测平台（切片、人评、污染、回归门禁）
quick: >-
  离线评测是发版闸门，不是脚本。集要版本化、按风险切片；人评有指南和金标陷阱；污染要报告去污后分数；回归门禁
  写死哪些切片不许掉。在线 A/B 另算，不能替代这套。
tags:
  - Evals
  - OpenAI
  - Google
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Holistic Evaluation of Language Models
    url: https://arxiv.org/abs/2211.09110
    type: primary
  - title: openai/simple-evals
    url: https://github.com/openai/simple-evals
    type: secondary
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: https://arxiv.org/abs/2306.05685
    type: primary
---

Google HELM、OpenAI simple-evals、LMSYS MT-Bench 都在说：评测要固定协议。MLE / 对齐岗白板问离线平台，要的是切片、人评、污染、回归门禁。在线 A/B、护栏、peek 见 `design-eval-platform`。内部 harness 纪律见 `openai-eval-harness`。污染手法见 `align-eval-contam`。

## 切片是一等公民

我会先问：评什么能力、谁能看原题、失败谁负责、是否和线上同一系统提示。然后把离线集当数据产品：每条 case 有 id、许可、标签、创建时间、提示模板版本。报告钉死 `eval_set@sha` + `prompt@sha` + 解码 + 工具模拟器版本。口头「MMLU 高了」没有复现性。

切片至少：

- **能力。** 事实、推理、代码、工具、长上下文、多语言。公开集只作参考，私有轮换集才进门禁。
- **安全。** 攻击、过度拒绝，见 `align-over-refuse`、`align-red-team`、`align-safety-tax`。
- **产品。** 接地、引用、延迟预算。RAG 题冻语料版本，见 `design-prod-rag`。
- **回归敏感。** 上次事故、已知脆弱模板、金标陷阱。

切分按文档 / 用户 / 时间，不要随机切对话把同一用户放进训练和测试。工具题环境冻结，否则成功率是模拟器漂移。

LLM-as-judge 做筛子，不做唯金标。位置交换、换家族验收，见 `align-llm-judge`。长度当协变量，见 `align-length-bias`。Arena 活榜不进离线门禁，见 `align-arena`。

## 人评和污染

人评：指南写成可打的维度（正确、接地、有害、过度拒绝），不是「好不好」。抽样按风险分层，不是随机 50 条。塞金标陷阱测标注员；不一致高的类别先改指南。人评队列有 SLA，积压时不要拿裁判分顶替门禁。

污染：n-gram、近邻、答案指纹、搜索查重，见 `align-eval-contam`。发现重叠要报污染率和去污后分数，不是删一条继续吹。Canary 埋进预发布语料，模型能复述就是泄漏。评测日志回流训练前必须换新 held-out。

跑分：同一 runner、超时、解码。种子固定或报告均值方差。长生成截断要当失败，不要当「部分正确」混进总分。

## 回归门禁

一张表，硬闸和软闸分开：

- **硬闸。** 安全攻击成功率、过度拒绝、污染未报、私有核心集掉点超过阈值、工具误操作。破了不能发。
- **软闸。** 公开集、文风、长度、成本。掉了要解释和切片，不自动红灯。
- **不变式。** 有 cache vs 无 cache 的 greedy 对齐；提示版本变更必须重跑全套，见 `design-prompt-mgmt`。

门禁对着 切片 不是对着一个平均分。平均持平、医疗切片崩，仍是红灯。对比对象是上一个生产 checkpoint 和 SFT 基线，不是「历史上最好的内部实验」。

失败模式：刷公开集提示词；用训练 RM 当验收；人评疲劳全标「还可以」；门禁只看总分；把评测 prompt 写进系统提示过拟合考题。

平台自己的 SLO：队列积压、重跑幂等、结果不可被训练任务误读。权限：原题 ACL，防止评测集进博客和预训练。

## 追问

- **离线过了为什么还要在线？** 用户分布、延迟、改写、拒答体验离线盖不住。在线见 `design-eval-platform`。
- **公开基准全砍掉？** 留作沟通，不进硬闸。私有集轮换。
- **人评太慢怎么办？** 裁判筛 + 人看分歧和安全切片。人从门禁消失之日就是过拟合裁判之日。
- **回归阈值怎么定？** 用历史噪声和标注一致率定带宽，不要拍 1%。安全切片带宽更窄。

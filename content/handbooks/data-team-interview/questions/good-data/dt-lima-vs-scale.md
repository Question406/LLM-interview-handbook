---
id: dt-lima-vs-scale
section: good-data
order: 7
level: A
title: LIMA 说 1000 条精标就够对齐，那预训练为什么还要上 T token？
quick: "LIMA 的 1000 条精标示范，主要教已有能力的模型怎样回答；预训练则让模型学知识、覆盖更多任务。如果基座本来不会做某件事，少量漂亮示范补不上。False Promise 论文也指出，模仿教师的输出风格不等于学到教师的能力。"
companies:
  - apple
tags:
  - Apple
  - SFT
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "LIMA: Less Is More for Alignment"
    url: https://arxiv.org/abs/2305.11206
    type: primary
  - title: The False Promise of Imitating Proprietary LLMs
    url: https://arxiv.org/abs/2305.15717
    type: primary
  - title: "s1: Simple test-time scaling"
    url: https://arxiv.org/abs/2501.19393
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这两阶段解决的问题不同。预训练让模型获得知识和能力；对齐再教它如何把已有能力用在回答里。对齐数据可以少而精，但如果模型本来不会做，就需要补充覆盖相关任务、能验证质量的数据。

常见误区是：把 LIMA 读成「数据越少越好」。Zhou 等：70B 的 LLaMA 上用 1000 条精心挑选的示范，对齐表现可以很强；前提是基座已经从预训练里学会了能力，监督微调（SFT） 主要在选风格和格式。Gudibande 等 False Promise：只模仿专有模型的输出风格，学生没有那些能力，评测看起来像，一出分布就垮。这是「看起来好的数据」最危险的一种。

## 两段数据，两种稀缺

预训练需要大量不重复、有使用许可、排除了评测污染的 token。Chinchilla 讨论的训练规模和 AFM 的 13.4T 数据量，都属于这一阶段。某个语言或地区的知识如果没有学到，1000 条精标示范也补不齐。

后训练更需要明确的标注标准，以及好坏回答之间确实有差别的监督信号。LIMA 和 s1K（1000 条推理 SFT）说明：对齐和推理示范可以很省，但要过难度、多样、质量三道门，见 `dt-s1k`。再堆 59k 同质链，s1 的公开结果未必更好。

教师轨迹能进 SFT，当且仅当学生的失败模式能被这些轨迹覆盖，并且能验证的已经验证。

## 人标预算怎么花

只有 1 万条人工标注预算时，不要平均分给所有任务。LIMA 的启示是：覆盖任务边界和难例，丢掉「差不多」的对。实现见 `dt-human-budget`、`dt-pref-pair-code`。

苹果这轮还要加上：用户日志默认不能当这 1000 条，见 `dt-privacy-feedback`。

## 追问

- **Phi 的教科书合成算 LIMA 还是预训练？** 更像用合成提高样本效率的预训练 / mid。它没有否定覆盖，只是把「更好」提前。
- **工具数据也能 1000 条吗？** 工具要覆盖 字段和类型规范（schema）、失败的尝试、不该调。条数少可以，多样性不能少，见 `dt-traj-quality`。
- **现场怎么一句话说完？** 对齐可以少而精；能力不行就回到覆盖和验证合成。

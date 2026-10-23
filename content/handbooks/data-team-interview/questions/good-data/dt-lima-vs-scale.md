---
id: dt-lima-vs-scale
section: good-data
order: 7
level: A
title: LIMA 说 1000 条精标就够对齐，那预训练为什么还要上 T token？
quick: "两个阶段解决的问题不同。LIMA 的 1000 条精标示范，教的是已有能力的模型怎么回答；预训练让模型学到知识、覆盖更多任务。基座本来不会的事，少量漂亮示范补不上，False Promise 也发现模仿教师的风格不等于学到教师的能力。"
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

两个阶段解决的问题不一样。预训练让模型获得知识和能力，对齐教它怎样把已有的能力用到回答里。对齐数据可以少而精，但模型本来就不会的事，要回到预训练，补覆盖相关任务、质量可验证的数据。

常见的误读是把 LIMA 理解成「数据越少越好」。Zhou 等在 70B 的 LLaMA 上用 1000 条精心挑过的示范，就得到了很强的对齐表现。前提是基座已经从预训练里学会了这些能力，监督微调（SFT）主要是在选风格和格式。比如某个语言或地区的知识，预训练里没学到，1000 条精标示范是补不齐的。

基座没有这项能力时，示范再漂亮也只改得了表面。Gudibande 等的 False Promise 发现，只模仿专有模型的输出风格，学生并没有拿到那些能力，评测时看着像，一出分布就垮。这是「看起来好的数据」里最危险的一种。

所以两个阶段缺的东西不一样。预训练缺的是量：大量不重复、有使用许可、排除了评测污染的 token，Chinchilla 讨论的训练规模和 AFM 的 13.4T 数据量都属于这一段。后训练缺的是标准：明确的标注规范，以及好坏回答之间确实有差别的监督信号。LIMA 和 s1K（1000 条推理 SFT）说明对齐和推理示范可以很省，但要过难度、多样性、质量三道关，见 `dt-s1k`。在 s1 的公开结果里，再堆 59k 条同质的推理链，效果未必更好。

落到具体决定上，教师轨迹能不能进 SFT，看两点：学生的失败模式能被这些轨迹覆盖，能验证的部分已经验证过。

## 追问

**只有 1 万条人工标注预算，怎么花？**
别平均分给所有任务。LIMA 的启示是把预算花在覆盖任务边界和难例上，丢掉「好坏差不多」的样本对，实现见 `dt-human-budget`、`dt-pref-pair-code`。

**Phi 的教科书合成算 LIMA 那一类，还是预训练？**
更像用合成数据提高样本效率的预训练或 mid-training。覆盖仍然需要，它是把「更好」的数据提前用在了这一阶段。

**工具数据也能只用 1000 条吗？**
条数可以少，多样性要够。工具数据要覆盖字段和类型规范（schema）、失败的尝试，以及不该调用工具的情形，见 `dt-traj-quality`。

**现场怎么一句话说完？**
对齐可以少而精；能力不够，就回到覆盖和可验证的合成数据。

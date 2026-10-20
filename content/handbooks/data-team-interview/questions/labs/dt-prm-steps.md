---
id: dt-prm-steps
section: labs
order: 19
level: A
title: OpenAI：过程监督标签怎么采？DeepSeek 为什么后来不用神经 PRM？
quick: "可执行的题先用规则验证。只有最终答案检查无法发现的过程错误，才考虑人工或神经 PRM。过程编造的轨迹不能作 CE 正例。逐步监督可能更省样本，但人工标注昂贵，必须先统一步骤划分，并保留独立结果检查。"
companies:
  - apple
tags:
  - OpenAI
  - DeepSeek
  - Process Supervision
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

数学、代码和工具任务如果能执行验证，先使用规则奖励，并给题目提供可靠的最终答案。需要过程监督时，先约定一步如何划分：自然段、公式行还是工具调用。划分方式变了，旧标签就要重新检查。最终答案正确、过程却是编造的轨迹，不应作为交叉熵损失（CE）的训练目标，见 `dt-synth-reasoning`。验收还要检查最终答案，并抽样人工核对过程；PRM 分不能独自决定发布。教师觉得某步「看起来合理」，也不足以成为可靠的过程标签。

不能把 Let's Verify 的逐步人工标注直接当作所有生产任务的配方。神经过程奖励模型（PRM）可能偏爱「像讲解的句子」，而没有辨别推理是否正确，类似长度 hack。DeepSeek-R1-Zero 公开写了：大规模 RL 里神经过程 / 结果 奖励模型（RM） 会被 hack，重训 RM 又贵，他们改用准确率规则 + 格式规则。

接到苹果：AFM 数学和视觉 STEM 走规则奖励，和这条公开选择一致。AFM 工具树是另一条过程监督：人改的是决策点，环境负责状态对不对，比「给数学逐步打钩」便宜。预算不够我就只在最终答案对、模型爱写长推理链（CoT） 的桶里抽查过程，见 `dt-human-budget`。仍值得抽查过程的情况包括：最终答案正确，但中间引用了题目没有提供的量；工具轨迹最后成功，但某一步篡改了工具返回（observation）。这些用规则能抓一部分，抓不住的才请人。思考标签是格式数据，见 `dt-rlvr-data`，没有验证的长思考不要当过程金标。标签来自许可题和执行器，不从用户会话抽过程。

公开锚点：Lightman et al. MATH 上逐步标，过程监督比结果监督样本效率高；R1-Zero 准确率看装箱答案或测试，格式看是否按模板思考，不用神经 ORM / PRM。

## 追问

- **多数票当过程标签？** 弱门。几条链都错在同一步，票会一起错。
- **PRM 和 outcome RM 能不能一起训？** 能，步分加终局分。发布仍以固定的参考答案检查为准，不能只看 PRM 平均分。
- **思考标签要不要进 监督微调（SFT）？** 那是格式数据，见 `dt-rlvr-data`。没有验证的长思考不要当过程金标。

---
id: dt-prm-steps
section: labs
order: 19
level: A
title: OpenAI：过程监督标签怎么采？DeepSeek 为什么后来不用神经 PRM？
quick: "能执行验证的题先用规则奖励，只有最终答案检查发现不了的过程错误，才考虑人工或神经 PRM。逐步监督更省样本，但人工标注贵，要先统一步骤怎么划分，并保留独立的结果检查；过程编造的轨迹不进 CE 正例。DeepSeek 不用神经 PRM，是因为它在大规模 RL 里会被 hack，重训又贵。"
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

采过程监督标签前，先问这道题能不能直接验证。数学、代码和工具任务如果能执行验证，先用规则奖励，并给题目准备可靠的最终答案。只有最终答案检查发现不了的过程错误，才值得花钱做逐步标注。DeepSeek 后来不用神经 PRM，原因也在这里：它在大规模 RL 里会被 hack。

## 逐步标注的局限

Lightman et al.（Let's Verify）在 MATH 上逐步人工标注，发现过程监督比结果监督的样本效率更高。这个结论来自 MATH 上的人工标注，推到其他生产任务前要先验证。神经过程奖励模型（PRM）可能学会偏爱「像讲解的句子」，给读起来顺但推理错的步骤打高分，这和长度 hack 是同一类问题。教师觉得某一步「看起来合理」只是主观印象，做不了可靠的过程标签。

DeepSeek-R1-Zero 公开写了：在大规模 RL 里，神经的过程奖励模型和结果奖励模型（RM）都会被 hack，重训 RM 又贵，所以他们改用准确率规则加格式规则。准确率看装箱的答案或测试是否通过，格式看是否按模板思考，不用神经 ORM 或 PRM。AFM 2025 报告的数学和视觉 STEM 也走规则奖励。

## 需要过程监督时怎么采

1. **先约定一步怎么划分。** 按自然段、公式行还是工具调用。划分方式一变，旧标签就要重新检查。
2. **决定在哪里抽查。** 预算不够时，只在最终答案正确、而模型又爱写长推理链（CoT）的桶里抽查过程，见 `dt-human-budget`。值得抽查的典型情况有：最终答案正确，但中间引用了题目没给的量；工具轨迹最后成功了，但某一步篡改了工具返回（observation）。这些用规则能抓到一部分，抓不住的再请人。
3. **处理编造的轨迹。** 最终答案对、过程却是编造的轨迹，不进交叉熵损失（CE）的训练目标，见 `dt-synth-reasoning`。
4. **验收。** 检查最终答案，同时抽样人工核对过程。发布以最终答案检查为准，PRM 分只作参考。

## 实践中的变化

工具 / agent 任务有一种更便宜的过程监督：人修改的是决策点，状态对不对由环境来判断。AFM 2025 报告的工具树就是这样做的，比「给数学题逐步打钩」便宜。

## 追问

- **多数票能当过程标签吗？** 只能当弱门槛。几条链如果都错在同一步，投票会一起错。
- **PRM 和 outcome RM 能一起训吗？** 能，步骤分加终局分。发布仍以固定的参考答案检查为准，PRM 平均分只作参考。
- **思考标签要不要进监督微调（SFT）？** 思考标签是格式数据，见 `dt-rlvr-data`。没有经过验证的长思考，当不了过程金标。

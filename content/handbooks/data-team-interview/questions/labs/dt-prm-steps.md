---
id: dt-prm-steps
section: labs
order: 19
level: A
title: OpenAI：过程监督标签怎么采？DeepSeek 为什么后来不用神经 PRM？
quick: >-
  先问这道题能不能直接验证：能执行验证的先用 rule-based reward，只有最终答案检查发现不了的过程错误，才值得做人工或神经
  PRM。逐步监督更省样本，但人工标注贵，要先统一步骤怎么划分并保留独立的结果检查，过程编造的 trajectories 不进 CE 正例。DeepSeek
  不用神经 PRM，是因为它在大规模 RL 里会被 hack，重训又贵。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Let's Verify Step by Step
    url: 'https://arxiv.org/abs/2305.20050'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

采过程标签之前，先问这道题能不能直接验证。数学、代码、工具任务能执行验证的，先用 rule-based reward，给题目备好可靠的最终答案；只有最终答案检查发现不了的过程错误，才值得花钱逐步标。DeepSeek 后来不用神经 PRM，原因也在这里，它在大规模 RL 里会被 hack。

过程错误长什么样？比如一道题最终答案正确，中间却引用了题目没给的量；或者一条 tool-use trajectories 最后成功了，某一步却篡改了工具返回（observation）。光看结果查不出这种错，过程监督要抓的就是它们。

过程监督确实更省样本。Lightman 等人的 Let's Verify Step by Step 在 MATH 上逐步人工标注，发现过程监督比结果监督的样本效率更高，不过这是 MATH 上人工标注得出的结论，推到别的生产任务之前要先验证。神经 process reward 模型（PRM）还有自己的毛病：它可能学会偏爱「像讲解的句子」，给读着顺、推理错的步骤打高分，这和长度 hack 是一类问题。teacher 觉得某一步「看起来合理」，只是主观印象，当不了可靠的过程标签。

DeepSeek-R1-Zero 公开写了，在大规模 RL 里，神经的 PRM 和 outcome reward 模型（RM）都会被 hack，重训 RM 又贵，所以他们改用准确率规则加格式规则。准确率看装箱的答案或测试是否通过，格式看是否按模板思考，不用神经 ORM 或 PRM。

真要采过程标签，先约定一步怎么划分，按自然段、公式行还是 tool calls；划分方式一变，旧标签就得重新检查。预算不够就别全标，只在最终答案正确、模型又爱写长 chain-of-thought (CoT) 的桶里抽查过程，见 `dt-human-budget`。上面那两类错误规则能抓到一部分，抓不住的再请人。最终答案对、过程却是编造的 trajectories，不进 cross-entropy 损失（CE）的训练目标，见 `dt-synth-reasoning`。验收时检查最终答案，同时 sampling 人工核对过程；发布以最终答案检查为准，PRM 分只作参考。

## 追问

**工具 / agent 任务有没有更便宜的过程监督？**
有。人只修改决策点，状态对不对交给环境判断。AFM 2025 报告的工具树就是这样做的，比给数学题逐步打钩便宜；同一份报告里，数学和视觉 STEM 也走 rule-based reward。

**多数票能当过程标签吗？**
只能当弱 threshold。几条链如果都错在同一步，投票会跟着一起错。

**PRM 和 outcome RM 能一起训吗？**
能，步骤分加终局分。发布仍以固定的参考答案检查为准，PRM 平均分只作参考。

**思考标签要不要进 SFT？**
思考标签是格式数据，见 `dt-rlvr-data`。没经过验证的长思考，当不了过程 gold labels。

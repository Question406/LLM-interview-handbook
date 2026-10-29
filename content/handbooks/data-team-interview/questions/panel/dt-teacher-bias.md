---
id: dt-teacher-bias
section: panel
order: 8
level: A
title: Panel：最强 teacher 生成的数据，为什么 student 不一定学得最好？
quick: >-
  teacher 回答正确，不代表 student 能学会。还要查过程是否过长、是否用了 student 没有的工具，以及 student 自己
  sampling 时能不能找到类似的正确解。太难的示范可以压缩、拆成子任务，或改用 student 自己生成且验证通过的回答。
companies:
  - apple
tags:
  - Apple
  - Teacher Bias
  - Distillation
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Self-Instruct
    url: 'https://arxiv.org/abs/2212.10560'
    type: primary
  - title: 'STaR: Bootstrapping Reasoning With Reasoning'
    url: 'https://arxiv.org/abs/2203.14465'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

teacher 回答正确不代表 student 学得会，还得检查 student 自己能不能找到类似的正确解。「数据由最强模型生成」只说明了来源，说明不了质量。

举个例子，目标任务是日常写作和文档问答，teacher 却总生成竞赛题，题目再正确，也可能没训练到目标任务要的能力。别的常见问题也类似：过程过长，训练花在重复套话上；依赖 student 部署时用不了的工具或知识；只有一种固定文风。固定小标题和固定拒答模式还可能被下一代模型继续复制，见 `dt-self-improve`。

判断 student 能不能学，我会看两样东西。一是 student 对示范里各 token 给出的似然，二是让 student 自己 sampling $k$ 次，看能不能生成等价的正确答案。示范的似然很低、pass@$k$ 又接近 0，就要怀疑它对 student 过难。STaR 和 rejection sampling 保留的是 student 自己生成、再经过验证的正确回答，这条学习路径可能比直接复制 teacher 的长推理更适合 student（`dt-rejection-sample-code`）。

不合适的示范可以缩短推理说明，把复杂任务拆成子任务，或者排一个从短过程到长过程的课程。最终答案正确但中间过程错的样本，不该当成 cross-entropy 训练的正确示范（`dt-synth-reasoning`）。用多个 teacher 能减少单一文风的影响，但仍要有独立 verifier，否则只是让几个模型反复确认同一个错误。

## 追问

**distillation 配方里怎么考虑 student 学不学得会？**
teacher 成本、logits 产出效率和 student 能否学会要一起算。AFM 报告公开过一个例子，用由稠密模型扩展来的 MoE teacher，只对稠密 student 最后 10% 的训练 token 加 distillation，见 `dt-ondevice-distill-data`。

**较弱的 teacher 能教较弱的 student 吗？**
单轮、结果有验证时可以试。多代循环且没有验证，会增加模型退化的风险。

**teacher 有工具，student 没有怎么办？**
把工具观测整理成 student 实际能拿到的证据；做不到的话，这一步不 distillation。

**只想改善文风，还需要强 teacher 吗？**
可以用强 teacher，但更适合短示范或 preference pairs，用不着很长的说教式回答。

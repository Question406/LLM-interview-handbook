---
id: dt-teacher-bias
section: panel
order: 8
level: A
title: Panel：最强教师生成的数据，为什么学生不一定学得最好？
quick: "教师回答正确，不代表学生能学会。还要查过程是否过长、是否用了学生没有的工具，以及学生自己采样时能不能找到类似的正确解。太难的示范可以压缩、拆成子任务，或改用学生自己生成且验证通过的回答。"
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
updatedAt: 2026-10-12
sources:
  - title: Self-Instruct
    url: https://arxiv.org/abs/2212.10560
    type: primary
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

教师回答正确不代表学生学得会，还得检查学生自己能不能找到类似的正确解。「数据由最强模型生成」只说明了来源，说明不了质量。

举个例子，目标任务是日常写作和文档问答，教师却总生成竞赛题，题目再正确，也可能没训练到目标任务要的能力。别的常见问题也类似：过程过长，训练花在重复套话上；依赖学生部署时用不了的工具或知识；只有一种固定文风。固定小标题和固定拒答模式还可能被下一代模型继续复制，见 `dt-self-improve`。

判断学生能不能学，我会看两样东西。一是学生对示范里各 token 给出的似然，二是让学生自己采样 $k$ 次，看能不能生成等价的正确答案。示范的似然很低、pass@$k$ 又接近 0，就要怀疑它对学生过难。STaR 和拒绝采样保留的是学生自己生成、再经过验证的正确回答，这条学习路径可能比直接复制教师的长推理更适合学生（`dt-rejection-sample-code`）。

不合适的示范可以缩短推理说明，把复杂任务拆成子任务，或者排一个从短过程到长过程的课程。最终答案正确但中间过程错的样本，不该当成交叉熵训练的正确示范（`dt-synth-reasoning`）。用多个教师能减少单一文风的影响，但仍要有独立验证器，否则只是让几个模型反复确认同一个错误。

## 追问

**蒸馏配方里怎么考虑学生学不学得会？**
教师成本、logits 产出效率和学生能否学会要一起算。AFM 报告公开过一个例子，用由稠密模型扩展来的 MoE 教师，只对稠密学生最后 10% 的训练 token 加蒸馏，见 `dt-ondevice-distill-data`。

**较弱的教师能教较弱的学生吗？**
单轮、结果有验证时可以试。多代循环且没有验证，会增加模型退化的风险。

**教师有工具，学生没有怎么办？**
把工具观测整理成学生实际能拿到的证据；做不到的话，这一步不蒸馏。

**只想改善文风，还需要强教师吗？**
可以用强教师，但更适合短示范或偏好对，用不着很长的说教式回答。

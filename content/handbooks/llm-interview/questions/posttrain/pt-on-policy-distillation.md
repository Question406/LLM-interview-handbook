---
id: pt-on-policy-distillation
section: posttrain
order: 32
level: S
title: On-policy Distillation 为什么能同时获得 RL 的 state-distribution relevance 和蒸馏的稠密反馈？
quick: 学生先自己 rollout，teacher 再在学生实际访问的状态上给 token-level 分布信号。它避开纯离线 SFT 的 exposure bias，又比只给终局 reward 的 RL 更稠密；代价是 teacher 查询、版本一致性和 teacher 偏差。
tags:
  - Distillation
  - On-policy
  - KL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Thinking Machines — On-Policy Distillation
    url: https://thinkingmachines.ai/blog/on-policy-distillation/
    type: primary
---

离线 SFT 只在 teacher/demo 前缀上学习，学生一旦走偏就看到未训练过的状态。on-policy distillation 让学生生成前缀，再由 teacher 为这些前缀提供下一个 token 或 continuation 的软目标，因此监督覆盖学生真正的 state distribution。

和 RL 相比，它的 reward 更稠密且 credit assignment 更直接；和普通 KD 相比，它需要在线采样与严格的 policy/teacher 版本记录。实现时要定义 teacher 不确定或拒绝时怎么办、是否截断坏轨迹，以及 token-level KL 与 sequence-level loss 的权重。

验收要同时看短期 imitation loss、长 rollout 成功率、对分布外状态的恢复能力和 teacher 调用成本。若 teacher 自身有系统偏差，学生会更高效地继承它。

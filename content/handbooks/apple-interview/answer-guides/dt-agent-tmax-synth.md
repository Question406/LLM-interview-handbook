---
id: dt-agent-tmax-synth
kind: design
situation: 没有现成 issue 池仍需要真实可执行任务。
task: 从环境目标构造有效训练分布。
approach: 生成状态差异和可验证目标，检查可解与多样性。
result: 新任务迁移有效，不能只在合成器偏好上进步。
---

## 可以这样回答

没有现成 issue 池仍需要真实可执行任务。

没有现成 issue 池，就按技能、复杂度、资源这些维度组合出题，每题配 Docker 环境和程序 verifier，这是 Ai2 TMax 的做法。生成时只保证镜像能 build，全零题留给 RL 训练时剪掉。质量看 teacher pass@$k$ 和领域覆盖，再和 Terminal-Bench decontamination；checker 还要抽查，全对的简单题也要控制比例。

---
id: dt-agent-env-is-data
kind: design
situation: 交互中的下一状态取决于策略动作。
task: 解释环境为何是训练数据的一部分。
approach: 保存初态、动作接口、转移和评分版本。
result: 同任务能重置 resampling，而不只是复用旧 JSONL。
---

## 可以这样回答

交互中的下一状态取决于策略动作。

Agent RL 的数据集是一批能装起来、能打分、能并行跑的任务环境：current policy 进去生成新 trajectories，grader 看结果给奖励。手里的演示 jsonl 只是某个策略在某版环境上采的样，策略或环境一变就过时，主要拿来做 SFT 冷启动。所以盘点时要记环境和奖励版本，训练和评测任务分开。

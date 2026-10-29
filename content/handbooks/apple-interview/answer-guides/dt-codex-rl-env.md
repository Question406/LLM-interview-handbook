---
id: dt-codex-rl-env
kind: design
situation: 代码 agent 依赖真实软件环境交互。
task: 说明环境设计怎样影响学习。
approach: 对照公开任务、工具和测试约束解释。
result: 不编内部数据规模，用可执行示例验证理解。
---

## 可以这样回答

代码 agent 依赖真实软件环境交互。

Codex 给每个 agent 一个装好代码和依赖的云容器，trajectories 开始后断网，agent 在里面改代码、反复跑测试直到通过。正确性靠测试判，风格放在测过之后另评；断网是怕 agent 搜到标准补丁 contamination 奖励。没有 grader 的仓库，要先建好 checker 才能做 RL。

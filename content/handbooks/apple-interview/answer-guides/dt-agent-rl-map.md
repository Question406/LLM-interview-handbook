---
id: dt-agent-rl-map
kind: guide
situation: 大量环境不一定产生有效学习。
task: 建立 Agent RL 任务质量标准。
approach: 先审计任务可解、反馈可靠和难度可学。
result: 独立环境收益和成本支持扩量。
---

## 可以这样回答

大量环境不一定产生有效学习。

Agent RL 的数据是任务、可执行环境和可复现奖励三样一起，trajectories jsonl 只拿来冷启动。判断一批环境好不好，看说明是否完整、测试是否稳定、奖励会不会被钻空子，以及当前模型是否偶尔能做对。要扩量就先筛现有任务，或按任务维度合成环境，再并行跑 rollout。

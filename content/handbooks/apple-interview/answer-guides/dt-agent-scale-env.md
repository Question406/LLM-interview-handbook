---
id: dt-agent-scale-env
kind: design
situation: 并行环境可能被启动、依赖和重置成本限制。
task: 提高有效训练 throughput。
approach: 先 profiling 瓶颈，再分离环境与模型服务。
result: 每小时有效 rollout 增长，质量和策略新鲜度不降。
---

## 可以这样回答

并行环境可能被启动、依赖和重置成本限制。

先让单个任务在干净容器里稳定复现，再加并行环境，Agent RL 的瓶颈在环境规模。Qwen 同时跑 2 万个独立环境，SkyRL 用异步执行、任务调度和工具服务把 throughput 提到朴素实现的约 4 到 5 倍。扩之前先查超时、依赖和文件系统隔离。

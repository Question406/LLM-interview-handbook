---
id: dt-frontier-agent-sets
kind: design
situation: 搜索、GUI 和对话工具有不同瓶颈。
task: 选择能覆盖目标行为的 agent 评价。
approach: 分开观察、规划、调用、状态和协作。
result: 任务成功与过程约束一起检查，协议固定。
---

## 可以这样回答

搜索、GUI 和对话工具有不同瓶颈。

这几套测的是 agent 的不同环节：BrowseComp 用 1266 道人写的事实题测持续搜索；OSWorld 原集用 369 个真实桌面任务检查最终状态；τ-bench 看 agent 和模拟用户对话后能不能把数据库改对，而且多跑几次都稳；MCP Atlas 测多步工具流程。所以要分开报，合成一个「工具分数」会盖住各自卡住的地方。

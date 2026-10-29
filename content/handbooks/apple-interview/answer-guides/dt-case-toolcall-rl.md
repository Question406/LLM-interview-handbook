---
id: dt-case-toolcall-rl
kind: concept
situation: 一个总奖励难定位调用哪里错。
task: 让反馈对应工具选择和参数质量。
approach: 拆分名称、参数和执行结果，校验模拟偏差。
result: 真实执行收益支持奖励粒度，不奖励无效长思考。
---

## 可以这样回答

一个总奖励难定位调用哪里错。

tool calls RL 里，奖励就是数据的标签。ToolRL 说明奖励要拆到工具名、参数名、参数值三层，额外鼓励长思考会掉点；Kimi K2 说明没有真实工具时可以大规模模拟，但模拟环境和 judge 的偏差要靠真实执行来校。

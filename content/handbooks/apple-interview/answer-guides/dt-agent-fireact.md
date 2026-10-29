---
id: dt-agent-fireact
kind: design
situation: 少量优质 trajectories 可能覆盖不足。
task: 理解示范质量和多样性的作用。
approach: 保留可执行路径，按任务与工具变化扩展。
result: 新任务收益验证，不能把固定条数当普适配方。
---

## 可以这样回答

少量优质 trajectories 可能覆盖不足。

几百条可 replay 的成功 trajectories，够教会模型调用格式和什么时候停，泛化还不够。多样性来自不同的任务、格式和 teacher，同一条 ReAct 复制再多遍也学不到新东西。FireAct 的约 500 条适合短程、好验证的搜索 QA，SWE、GUI、多轮客服要更多可执行任务。
